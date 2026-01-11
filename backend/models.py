"""
SQLAlchemy models for CFA Trainer database.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, JSON, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="user", cascade="all, delete-orphan")
    errors = relationship("UserError", back_populates="user", cascade="all, delete-orphan")
    calculator_sessions = relationship("CalculatorSession", back_populates="user", cascade="all, delete-orphan")


class UserProgress(Base):
    """Tracks user progress per book/module."""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, nullable=False)
    module_id = Column(Integer, nullable=False)

    # Progress metrics
    questions_seen = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    mastery_percent = Column(Float, default=0.0)

    # Unlock status (80% rule)
    is_unlocked = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="progress")

    class Config:
        # Unique constraint: one progress record per user/book/module
        __table_args__ = (
            {"sqlite_autoincrement": True},
        )


class TestResult(Base):
    """Stores completed test results."""
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Test metadata
    test_type = Column(String(20), nullable=False)  # "module", "book", "mock_exam"
    test_mode = Column(String(20), nullable=False)  # "standard", "90_second"
    book_id = Column(Integer, nullable=True)
    module_id = Column(Integer, nullable=True)

    # Results
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score_percent = Column(Float, nullable=False)
    time_spent_seconds = Column(Integer, nullable=False)

    # Detailed question results
    # Format: [{"question_id": "QM-1-001", "user_answer": "A", "correct": false, "time_spent": 45}]
    question_details = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="test_results")


class UserError(Base):
    """Tracks questions user answered incorrectly for spaced repetition."""
    __tablename__ = "user_errors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(String(50), nullable=False)
    book_id = Column(Integer, nullable=False)
    module_id = Column(Integer, nullable=False)

    # Error tracking
    error_count = Column(Integer, default=1)
    last_error_at = Column(DateTime, default=datetime.utcnow)
    last_correct_at = Column(DateTime, nullable=True)

    # Spaced Repetition fields
    next_review_at = Column(DateTime, nullable=True)
    review_interval_days = Column(Integer, default=1)  # SM-2 interval: 1, 3, 7, 14, 30, 60

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="errors")


class CalculatorSession(Base):
    """Tracks calculator practice sessions."""
    __tablename__ = "calculator_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Problem info
    worksheet_type = Column(String(20), nullable=False)  # "TVM", "CF", "Bond", "Stats"
    problem_id = Column(String(50), nullable=True)
    problem_data = Column(JSON, nullable=True)

    # User solution
    user_steps = Column(JSON, nullable=True)
    user_answer = Column(Float, nullable=True)

    # Result
    is_correct = Column(Boolean, nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="calculator_sessions")
