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


class UserProgressCreate(ProgressBase):
    questions_seen: int
    questions_correct: int


class UserProgressUpdate(ProgressBase):
    is_correct: bool


class UserProgressResponse(ProgressBase):
    id: int
    user_id: int
    questions_seen: int
    questions_correct: int
    mastery_percent: float
    is_unlocked: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookProgressResponse(BaseModel):
    book_id: int
    user_id: int
    modules: List[Any]
    total_questions_seen: int
    total_questions_correct: int
    book_mastery: float


class OverallProgressResponse(BaseModel):
    user_id: int
    total_questions_seen: int
    total_questions_correct: int
    overall_mastery: float
    books_started: int
    books_progress: List[Dict[str, Any]]


# ============== Test Schemas ==============

class QuestionResponse(BaseModel):
    question_id: str
    question_text: str
    question_text_formula: Optional[str] = None
    has_table: bool = False
    has_image: bool = False
    image_path: Optional[str] = None
    options: Dict[str, str]
    correct_answer: str
    explanation: str
    explanation_wrong: Optional[Dict[str, str]] = None
    calculator_steps: Optional[List[str]] = None
    difficulty: Optional[str] = None
    los_reference: Optional[str] = None


class TestStartRequest(BaseModel):
    test_type: str
    test_mode: str
    book_id: Optional[int] = None
    module_id: Optional[int] = None


class TestSubmitRequest(BaseModel):
    test_type: str
    test_mode: str
    book_id: Optional[int] = None
    module_id: Optional[int] = None
    time_spent_seconds: int
    question_details: List[Dict[str, Any]]


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

    class Config:
        from_attributes = True


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


class ErrorReviewRequest(BaseModel):
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

class CalculatorProblemResponse(BaseModel):
    problem_id: str
    worksheet: str
    problem_text: str
    given: Dict[str, Any]
    find: str
    correct_answer: Any  # Can be float or dict
    tolerance: float = 0.01
    steps: List[str]
    common_mistakes: Optional[List[str]] = None
    difficulty: Optional[str] = None


class CalculatorCheckRequest(BaseModel):
    problem_id: str
    user_answer: Any  # Can be float or dict
    time_spent_seconds: int
    user_steps: Optional[List[str]] = None


class CalculatorStatsResponse(BaseModel):
    total_attempts: int
    total_correct: int
    overall_accuracy: float
    by_worksheet_type: Dict[str, Dict[str, Any]]
    recent_sessions: List[Any]


# ============== Sync Schemas ==============

class SyncRequest(BaseModel):
    """For syncing localStorage data with backend."""
    progress: List[UserProgressUpdate]
    last_sync_at: Optional[datetime] = None


class SyncResponse(BaseModel):
    success: bool
    synced_at: datetime
    conflicts: Optional[List[Dict[str, Any]]] = None
