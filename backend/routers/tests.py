"""
Tests router - handles test sessions and results.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
import json
import os
import random
from datetime import datetime

from ..database import get_db
from ..models import User, TestResult, UserProgress, UserError
from ..schemas import (
    TestResultResponse,
    TestHistoryResponse,
    QuestionResponse,
    TestSubmitRequest
)
from ..auth import get_current_user

router = APIRouter(
    prefix="/api/tests",
    tags=["tests"]
)

# Path to questions data (v2 structure)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "data", "v2")

# Mapping of book_id to folder name
BOOK_FOLDERS = {
    1: "book1_quants",
    2: "book2_economics",
    3: "book3_corporate",
    4: "book4_fsa",
    5: "book5_equity",
    6: "book6_fixed_income",
    7: "book7_derivatives",
    8: "book8_alternatives",
    9: "book9_portfolio",
    10: "book10_ethics"
}


def load_book_data(book_id: int) -> dict:
    """Load book data from v2 structure (aggregates all modules)."""
    if book_id not in BOOK_FOLDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )

    book_folder = BOOK_FOLDERS[book_id]
    book_path = os.path.join(DATA_PATH, book_folder)

    if not os.path.exists(book_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} data not found"
        )

    # Find all module directories (module1, module2, module3, ...)
    module_dirs = sorted([
        d for d in os.listdir(book_path)
        if os.path.isdir(os.path.join(book_path, d)) and d.startswith("module")
    ])

    if not module_dirs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No modules found for book {book_id}"
        )

    # Load questions from each module
    learning_modules = []
    book_name = None
    book_name_ru = None
    book_code = None

    for module_dir in module_dirs:
        questions_file = os.path.join(book_path, module_dir, "questions.json")

        if not os.path.exists(questions_file):
            continue

        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                module_data = json.load(f)

            # Extract book info from first module
            if book_name is None:
                book_name = module_data.get("book_name", "")
                book_name_ru = module_data.get("book_name_ru", "")
                book_code = module_data.get("book_code", "")

            # Build module structure compatible with old API
            learning_modules.append({
                "module_id": module_data.get("module_id"),
                "module_name": module_data.get("module_name", ""),
                "module_name_ru": module_data.get("module_name_ru", ""),
                "questions": module_data.get("questions", [])
            })
        except Exception as e:
            print(f"Warning: Failed to load {questions_file}: {e}")
            continue

    # Return structure compatible with old API
    return {
        "book_id": book_id,
        "book_name": book_name or f"Book {book_id}",
        "book_name_ru": book_name_ru or "",
        "book_code": book_code or "",
        "learning_modules": learning_modules
    }


def get_module_questions(book_id: int, module_id: int) -> List[dict]:
    """Get questions for a specific module from v2 structure."""
    if book_id not in BOOK_FOLDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )

    book_folder = BOOK_FOLDERS[book_id]
    questions_file = os.path.join(DATA_PATH, book_folder, f"module{module_id}", "questions.json")

    if not os.path.exists(questions_file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Questions not found for book {book_id}, module {module_id}"
        )

    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            module_data = json.load(f)
        return module_data.get("questions", [])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load questions: {str(e)}"
        )


@router.get("/module/{book_id}/{module_id}", response_model=List[QuestionResponse])
async def get_module_test(
    book_id: int,
    module_id: int,
    shuffle: bool = Query(True, description="Shuffle questions"),
    limit: Optional[int] = Query(None, description="Limit number of questions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get questions for a module test."""
    questions = get_module_questions(book_id, module_id)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions found for book {book_id}, module {module_id}"
        )

    if shuffle:
        questions = random.sample(questions, len(questions))

    if limit and limit < len(questions):
        questions = questions[:limit]

    return questions


@router.get("/book/{book_id}", response_model=List[QuestionResponse])
async def get_book_test(
    book_id: int,
    num_questions: int = Query(50, description="Number of questions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get random questions from all modules of a book."""
    book_data = load_book_data(book_id)

    all_questions = []
    for module in book_data.get("learning_modules", []):
        all_questions.extend(module.get("questions", []))

    if not all_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions found for book {book_id}"
        )

    # Random sample
    num_questions = min(num_questions, len(all_questions))
    selected = random.sample(all_questions, num_questions)

    return selected


@router.get("/book-info/{book_id}")
async def get_book_info(
    book_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get book structure with modules and questions."""
    return load_book_data(book_id)


@router.get("/mock-exam", response_model=List[QuestionResponse])
async def get_mock_exam(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a mock exam with 180 questions.
    30% from errors, 30% from weak modules, 40% random.
    """
    TOTAL_QUESTIONS = 180

    all_questions = []
    question_ids_used = set()

    # Load all available books
    for book_id in range(1, 11):
        try:
            book_data = load_book_data(book_id)
            for module in book_data.get("learning_modules", []):
                for q in module.get("questions", []):
                    q["_book_id"] = book_id
                    q["_module_id"] = module.get("module_id")
                    all_questions.append(q)
        except HTTPException:
            continue

    if len(all_questions) < TOTAL_QUESTIONS:
        # Not enough questions, return all shuffled
        random.shuffle(all_questions)
        return all_questions

    selected = []

    # 1. Get 30% from user's errors
    error_count = int(TOTAL_QUESTIONS * 0.3)
    user_errors = db.query(UserError).filter(
        UserError.user_id == current_user.id
    ).order_by(desc(UserError.error_count)).limit(error_count * 2).all()

    error_question_ids = {e.question_id for e in user_errors}
    error_questions = [q for q in all_questions if q.get("question_id") in error_question_ids]

    if error_questions:
        sample_size = min(error_count, len(error_questions))
        error_sample = random.sample(error_questions, sample_size)
        selected.extend(error_sample)
        question_ids_used.update(q.get("question_id") for q in error_sample)

    # 2. Get 30% from weak modules (mastery < 70%)
    weak_count = int(TOTAL_QUESTIONS * 0.3)
    weak_modules = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.mastery_percent < 70
        )
    ).all()

    weak_questions = []
    for progress in weak_modules:
        module_qs = [q for q in all_questions
                    if q.get("_book_id") == progress.book_id
                    and q.get("_module_id") == progress.module_id
                    and q.get("question_id") not in question_ids_used]
        weak_questions.extend(module_qs)

    if weak_questions:
        sample_size = min(weak_count, len(weak_questions))
        weak_sample = random.sample(weak_questions, sample_size)
        selected.extend(weak_sample)
        question_ids_used.update(q.get("question_id") for q in weak_sample)

    # 3. Fill rest with random questions
    remaining = TOTAL_QUESTIONS - len(selected)
    available = [q for q in all_questions if q.get("question_id") not in question_ids_used]

    if available and remaining > 0:
        sample_size = min(remaining, len(available))
        random_sample = random.sample(available, sample_size)
        selected.extend(random_sample)

    # Shuffle final selection
    random.shuffle(selected)

    # Clean up internal fields
    for q in selected:
        q.pop("_book_id", None)
        q.pop("_module_id", None)

    return selected


@router.post("/submit", response_model=TestResultResponse)
async def submit_test(
    result: TestSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit test results and update progress."""

    # Calculate score
    correct = sum(1 for q in result.question_details if q.get("correct", False))
    total = len(result.question_details)
    score_percent = (correct / total * 100) if total > 0 else 0

    # Create test result record
    test_result = TestResult(
        user_id=current_user.id,
        test_type=result.test_type,
        test_mode=result.test_mode,
        book_id=result.book_id,
        module_id=result.module_id,
        total_questions=total,
        correct_answers=correct,
        score_percent=score_percent,
        time_spent_seconds=result.time_spent_seconds,
        question_details=result.question_details
    )
    db.add(test_result)

    # Update user errors for incorrect answers
    for q_detail in result.question_details:
        if not q_detail.get("correct", False):
            _record_error(
                user_id=current_user.id,
                question_id=q_detail.get("question_id"),
                book_id=result.book_id or 0,
                module_id=result.module_id or 0,
                db=db
            )
        else:
            # Mark as correct in error tracking
            _mark_correct(
                user_id=current_user.id,
                question_id=q_detail.get("question_id"),
                db=db
            )

    # Update progress for module tests
    if result.test_type == "module" and result.book_id and result.module_id:
        _update_module_progress(
            user_id=current_user.id,
            book_id=result.book_id,
            module_id=result.module_id,
            questions_seen=total,
            questions_correct=correct,
            db=db
        )

    db.commit()
    db.refresh(test_result)

    return test_result


@router.get("/history", response_model=List[TestHistoryResponse])
async def get_test_history(
    limit: int = Query(20, description="Number of results to return"),
    test_type: Optional[str] = Query(None, description="Filter by test type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's test history."""
    query = db.query(TestResult).filter(
        TestResult.user_id == current_user.id
    )

    if test_type:
        query = query.filter(TestResult.test_type == test_type)

    results = query.order_by(desc(TestResult.created_at)).limit(limit).all()

    return results


def _record_error(user_id: int, question_id: str, book_id: int, module_id: int, db: Session):
    """Record or update an error for spaced repetition."""
    existing = db.query(UserError).filter(
        and_(
            UserError.user_id == user_id,
            UserError.question_id == question_id
        )
    ).first()

    if existing:
        existing.error_count += 1
        existing.last_error_at = datetime.utcnow()
        # Reset spaced repetition
        existing.review_interval_days = 1
        existing.next_review_at = datetime.utcnow()
    else:
        new_error = UserError(
            user_id=user_id,
            question_id=question_id,
            book_id=book_id,
            module_id=module_id,
            error_count=1,
            next_review_at=datetime.utcnow(),
            review_interval_days=1
        )
        db.add(new_error)


def _mark_correct(user_id: int, question_id: str, db: Session):
    """Update error record when answered correctly."""
    existing = db.query(UserError).filter(
        and_(
            UserError.user_id == user_id,
            UserError.question_id == question_id
        )
    ).first()

    if existing:
        from datetime import timedelta
        existing.last_correct_at = datetime.utcnow()
        # Increase spaced repetition interval
        intervals = [1, 3, 7, 14, 30, 60]
        current_idx = intervals.index(existing.review_interval_days) if existing.review_interval_days in intervals else 0
        next_idx = min(current_idx + 1, len(intervals) - 1)
        existing.review_interval_days = intervals[next_idx]
        existing.next_review_at = datetime.utcnow() + timedelta(days=intervals[next_idx])


def _update_module_progress(user_id: int, book_id: int, module_id: int,
                           questions_seen: int, questions_correct: int, db: Session):
    """Update module progress after test completion."""
    progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == user_id,
            UserProgress.book_id == book_id,
            UserProgress.module_id == module_id
        )
    ).first()

    if progress:
        progress.questions_seen = max(progress.questions_seen, questions_seen)
        progress.questions_correct = max(progress.questions_correct, questions_correct)
        progress.mastery_percent = (progress.questions_correct / progress.questions_seen * 100) if progress.questions_seen > 0 else 0

        if progress.mastery_percent >= 80 and not progress.completed_at:
            progress.completed_at = datetime.utcnow()
    else:
        mastery = (questions_correct / questions_seen * 100) if questions_seen > 0 else 0
        progress = UserProgress(
            user_id=user_id,
            book_id=book_id,
            module_id=module_id,
            questions_seen=questions_seen,
            questions_correct=questions_correct,
            mastery_percent=mastery,
            is_unlocked=True,
            completed_at=datetime.utcnow() if mastery >= 80 else None
        )
        db.add(progress)
