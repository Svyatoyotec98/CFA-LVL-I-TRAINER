"""
Progress router - tracks user progress per book/module.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional

from ..database import get_db
from ..models import User, UserProgress
from ..schemas import (
    UserProgressCreate,
    UserProgressUpdate,
    UserProgressResponse,
    BookProgressResponse,
    OverallProgressResponse
)
from ..auth import get_current_user

router = APIRouter(
    prefix="/api/progress",
    tags=["progress"]
)


@router.get("", response_model=OverallProgressResponse)
async def get_overall_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall progress for current user across all books."""
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).all()

    # Group by book
    books_progress = {}
    for record in progress_records:
        book_id = record.book_id
        if book_id not in books_progress:
            books_progress[book_id] = {
                "book_id": book_id,
                "modules": [],
                "total_questions_seen": 0,
                "total_questions_correct": 0
            }
        books_progress[book_id]["modules"].append(record)
        books_progress[book_id]["total_questions_seen"] += record.questions_seen
        books_progress[book_id]["total_questions_correct"] += record.questions_correct

    # Calculate overall stats
    total_seen = sum(b["total_questions_seen"] for b in books_progress.values())
    total_correct = sum(b["total_questions_correct"] for b in books_progress.values())

    return {
        "user_id": current_user.id,
        "total_questions_seen": total_seen,
        "total_questions_correct": total_correct,
        "overall_mastery": (total_correct / total_seen * 100) if total_seen > 0 else 0,
        "books_started": len(books_progress),
        "books_progress": list(books_progress.values())
    }


@router.get("/book/{book_id}", response_model=BookProgressResponse)
async def get_book_progress(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress for a specific book."""
    progress_records = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.book_id == book_id
        )
    ).order_by(UserProgress.module_id).all()

    total_seen = sum(r.questions_seen for r in progress_records)
    total_correct = sum(r.questions_correct for r in progress_records)

    return {
        "book_id": book_id,
        "user_id": current_user.id,
        "modules": progress_records,
        "total_questions_seen": total_seen,
        "total_questions_correct": total_correct,
        "book_mastery": (total_correct / total_seen * 100) if total_seen > 0 else 0
    }


@router.get("/module/{book_id}/{module_id}", response_model=UserProgressResponse)
async def get_module_progress(
    book_id: int,
    module_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress for a specific module."""
    progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.book_id == book_id,
            UserProgress.module_id == module_id
        )
    ).first()

    if not progress:
        # Return empty progress
        return {
            "id": 0,
            "user_id": current_user.id,
            "book_id": book_id,
            "module_id": module_id,
            "questions_seen": 0,
            "questions_correct": 0,
            "mastery_percent": 0.0,
            "is_unlocked": module_id == 1,  # First module always unlocked
            "completed_at": None
        }

    return progress


@router.post("/sync", response_model=List[UserProgressResponse])
async def sync_progress(
    progress_data: List[UserProgressCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync progress from localStorage to backend.
    Creates or updates progress records.
    """
    results = []

    for data in progress_data:
        # Find existing record
        existing = db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == current_user.id,
                UserProgress.book_id == data.book_id,
                UserProgress.module_id == data.module_id
            )
        ).first()

        if existing:
            # Update existing
            existing.questions_seen = max(existing.questions_seen, data.questions_seen)
            existing.questions_correct = max(existing.questions_correct, data.questions_correct)
            existing.mastery_percent = (existing.questions_correct / existing.questions_seen * 100) if existing.questions_seen > 0 else 0

            # Check 80% unlock rule
            if existing.mastery_percent >= 80 and not existing.completed_at:
                from datetime import datetime
                existing.completed_at = datetime.utcnow()

            results.append(existing)
        else:
            # Create new
            mastery = (data.questions_correct / data.questions_seen * 100) if data.questions_seen > 0 else 0
            new_progress = UserProgress(
                user_id=current_user.id,
                book_id=data.book_id,
                module_id=data.module_id,
                questions_seen=data.questions_seen,
                questions_correct=data.questions_correct,
                mastery_percent=mastery,
                is_unlocked=True
            )
            db.add(new_progress)
            results.append(new_progress)

    db.commit()

    # Refresh to get IDs
    for r in results:
        db.refresh(r)

    # Check and unlock next modules
    _check_unlock_next_modules(current_user.id, db)

    return results


@router.put("/update", response_model=UserProgressResponse)
async def update_progress(
    update_data: UserProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress after answering a question."""
    progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.book_id == update_data.book_id,
            UserProgress.module_id == update_data.module_id
        )
    ).first()

    if not progress:
        # Create new progress record
        progress = UserProgress(
            user_id=current_user.id,
            book_id=update_data.book_id,
            module_id=update_data.module_id,
            questions_seen=0,
            questions_correct=0,
            mastery_percent=0.0,
            is_unlocked=True
        )
        db.add(progress)

    # Update counts
    progress.questions_seen += 1
    if update_data.is_correct:
        progress.questions_correct += 1

    # Recalculate mastery
    progress.mastery_percent = (progress.questions_correct / progress.questions_seen * 100)

    # Check 80% completion
    if progress.mastery_percent >= 80 and not progress.completed_at:
        from datetime import datetime
        progress.completed_at = datetime.utcnow()
        # Unlock next module
        _unlock_next_module(current_user.id, update_data.book_id, update_data.module_id, db)

    db.commit()
    db.refresh(progress)

    return progress


def _unlock_next_module(user_id: int, book_id: int, current_module_id: int, db: Session):
    """Unlock the next module after achieving 80% mastery."""
    next_module_id = current_module_id + 1

    # Check if next module progress exists
    next_progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == user_id,
            UserProgress.book_id == book_id,
            UserProgress.module_id == next_module_id
        )
    ).first()

    if next_progress:
        next_progress.is_unlocked = True
    else:
        # Create placeholder for unlocked module
        new_progress = UserProgress(
            user_id=user_id,
            book_id=book_id,
            module_id=next_module_id,
            questions_seen=0,
            questions_correct=0,
            mastery_percent=0.0,
            is_unlocked=True
        )
        db.add(new_progress)


def _check_unlock_next_modules(user_id: int, db: Session):
    """Check all progress and unlock next modules where applicable."""
    all_progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).all()

    for progress in all_progress:
        if progress.mastery_percent >= 80:
            _unlock_next_module(user_id, progress.book_id, progress.module_id, db)

    db.commit()
