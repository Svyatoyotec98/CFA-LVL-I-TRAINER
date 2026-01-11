"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============== User Schemas ==============

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ============== Token Schemas ==============

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# ============== Progress Schemas ==============

class ProgressBase(BaseModel):
    book_id: int
    module_id: int


class ProgressUpdate(ProgressBase):
    questions_seen: int
    questions_correct: int


class ProgressResponse(ProgressBase):
    id: int
    questions_seen: int
    questions_correct: int
    mastery_percent: float
    is_unlocked: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookProgressResponse(BaseModel):
    book_id: int
    book_name: str
    total_modules: int
    completed_modules: int
    overall_mastery: float
    modules: List[ProgressResponse]


# ============== Test Schemas ==============

class QuestionAnswer(BaseModel):
    question_id: str
    user_answer: str  # "A", "B", or "C"
    time_spent: int  # seconds


class TestSubmit(BaseModel):
    test_type: str = Field(..., pattern="^(module|book|mock_exam)$")
    test_mode: str = Field(..., pattern="^(standard|90_second)$")
    book_id: Optional[int] = None
    module_id: Optional[int] = None
    answers: List[QuestionAnswer]
    total_time_seconds: int


class TestResultResponse(BaseModel):
    id: int
    test_type: str
    test_mode: str
    book_id: Optional[int]
    module_id: Optional[int]
    total_questions: int
    correct_answers: int
    score_percent: float
    time_spent_seconds: int
    created_at: datetime
    question_details: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class TestHistoryResponse(BaseModel):
    total_tests: int
    average_score: float
    results: List[TestResultResponse]


# ============== Error/Review Schemas ==============

class UserErrorResponse(BaseModel):
    id: int
    question_id: str
    book_id: int
    module_id: int
    error_count: int
    last_error_at: datetime
    next_review_at: Optional[datetime]
    review_interval_days: int

    class Config:
        from_attributes = True


class ReviewQuestionResponse(BaseModel):
    question_id: str
    book_id: int
    module_id: int
    error_count: int
    # Question data will be loaded from JSON
    question_data: Optional[Dict[str, Any]] = None


class MarkReviewedRequest(BaseModel):
    question_id: str
    was_correct: bool


# ============== Glossary Schemas ==============

class GlossaryTermResponse(BaseModel):
    term_id: str
    term_en: str
    term_ru: Optional[str]
    definition_en: str
    definition_ru: Optional[str]
    formula: Optional[str]
    module_id: int
    related_los: Optional[List[str]]


class GlossaryBookResponse(BaseModel):
    book_id: int
    book_name: str
    terms: List[GlossaryTermResponse]


# ============== Calculator Schemas ==============

class CalculatorProblem(BaseModel):
    problem_id: str
    worksheet: str
    problem_text: str
    given: Dict[str, Any]
    find: str
    correct_answer: float
    tolerance: float = 0.01
    steps: List[str]
    common_mistakes: Optional[List[str]] = None


class CalculatorSubmit(BaseModel):
    problem_id: str
    worksheet_type: str
    user_answer: float
    time_spent_seconds: int
    user_steps: Optional[List[str]] = None


class CalculatorResultResponse(BaseModel):
    is_correct: bool
    correct_answer: float
    user_answer: float
    difference: float
    steps: List[str]


class CalculatorStatsResponse(BaseModel):
    total_problems: int
    correct_problems: int
    accuracy_percent: float
    by_worksheet: Dict[str, Dict[str, int]]  # {"TVM": {"total": 10, "correct": 8}}


# ============== Sync Schemas ==============

class SyncRequest(BaseModel):
    """For syncing localStorage data with backend."""
    progress: List[ProgressUpdate]
    last_sync_at: Optional[datetime] = None


class SyncResponse(BaseModel):
    success: bool
    synced_at: datetime
    conflicts: Optional[List[Dict[str, Any]]] = None
