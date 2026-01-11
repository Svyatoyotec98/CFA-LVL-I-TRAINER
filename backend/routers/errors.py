"""
Errors router - handles user errors and spaced repetition.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os

from ..database import get_db
from ..models import User, UserError
from ..schemas import UserErrorResponse, ErrorReviewRequest
from ..auth import get_current_user

router = APIRouter(
    prefix="/api/errors",
    tags=["errors"]
)

# Path to questions data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "data", "books")


def load_question_by_id(question_id: str) -> Optional[dict]:
    """Load a specific question by ID."""
    # Question ID format: Q-{book_id}-{number} or QM-{module}-{number}
    for book_id in range(1, 11):
        try:
            filepath = os.path.join(DATA_PATH, f"book{book_id}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    book_data = json.load(f)
                    for module in book_data.get("learning_modules", []):
                        for q in module.get("questions", []):
                            if q.get("question_id") == question_id:
                                return q
        except Exception:
            continue
    return None


@router.get("", response_model=List[UserErrorResponse])
async def get_all_errors(
    limit: int = Query(100, description="Maximum errors to return"),
    book_id: Optional[int] = Query(None, description="Filter by book"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all errors for current user."""
    query = db.query(UserError).filter(
        UserError.user_id == current_user.id
    )

    if book_id:
        query = query.filter(UserError.book_id == book_id)

    errors = query.order_by(desc(UserError.error_count)).limit(limit).all()

    return errors


@router.get("/review")
async def get_review_questions(
    limit: int = Query(20, description="Maximum questions to review"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get questions due for review today (spaced repetition)."""
    today = datetime.utcnow()

    # Get errors due for review
    due_errors = db.query(UserError).filter(
        and_(
            UserError.user_id == current_user.id,
            UserError.next_review_at <= today
        )
    ).order_by(UserError.next_review_at).limit(limit).all()

    # Load full question data
    review_questions = []
    for error in due_errors:
        question = load_question_by_id(error.question_id)
        if question:
            review_questions.append({
                "error_id": error.id,
                "question_id": error.question_id,
                "book_id": error.book_id,
                "module_id": error.module_id,
                "error_count": error.error_count,
                "review_interval_days": error.review_interval_days,
                "question": question
            })

    return {
        "total_due": len(due_errors),
        "questions": review_questions
    }


@router.get("/stats")
async def get_error_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get error statistics for current user."""
    all_errors = db.query(UserError).filter(
        UserError.user_id == current_user.id
    ).all()

    today = datetime.utcnow()

    # Group by book
    by_book = {}
    total_errors = 0
    due_today = 0
    mastered = 0  # Errors with interval >= 30 days

    for error in all_errors:
        book_id = error.book_id
        if book_id not in by_book:
            by_book[book_id] = {"count": 0, "questions": []}
        by_book[book_id]["count"] += 1
        by_book[book_id]["questions"].append(error.question_id)

        total_errors += 1

        if error.next_review_at and error.next_review_at <= today:
            due_today += 1

        if error.review_interval_days >= 30:
            mastered += 1

    return {
        "total_errors": total_errors,
        "due_today": due_today,
        "mastered": mastered,
        "by_book": by_book,
        "most_problematic": sorted(
            all_errors,
            key=lambda e: e.error_count,
            reverse=True
        )[:10]
    }


@router.post("/mark-reviewed")
async def mark_reviewed(
    request: ErrorReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an error as reviewed and update spaced repetition schedule."""
    error = db.query(UserError).filter(
        and_(
            UserError.user_id == current_user.id,
            UserError.question_id == request.question_id
        )
    ).first()

    if not error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error record not found"
        )

    # SM-2 intervals
    intervals = [1, 3, 7, 14, 30, 60]

    if request.was_correct:
        # Increase interval
        current_idx = intervals.index(error.review_interval_days) if error.review_interval_days in intervals else 0
        next_idx = min(current_idx + 1, len(intervals) - 1)
        error.review_interval_days = intervals[next_idx]
        error.last_correct_at = datetime.utcnow()
    else:
        # Reset to beginning
        error.review_interval_days = intervals[0]
        error.error_count += 1
        error.last_error_at = datetime.utcnow()

    # Set next review date
    error.next_review_at = datetime.utcnow() + timedelta(days=error.review_interval_days)

    db.commit()
    db.refresh(error)

    return {
        "question_id": error.question_id,
        "new_interval_days": error.review_interval_days,
        "next_review_at": error.next_review_at,
        "total_errors": error.error_count
    }


@router.delete("/{question_id}")
async def delete_error(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an error record (mark as fully mastered)."""
    error = db.query(UserError).filter(
        and_(
            UserError.user_id == current_user.id,
            UserError.question_id == question_id
        )
    ).first()

    if not error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error record not found"
        )

    db.delete(error)
    db.commit()

    return {"message": f"Error record for {question_id} deleted"}
