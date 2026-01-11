"""
Calculator router - BA II Plus practice problems.
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
from ..models import User, CalculatorSession
from ..schemas import CalculatorProblemResponse, CalculatorCheckRequest, CalculatorStatsResponse
from ..auth import get_current_user

router = APIRouter(
    prefix="/api/calculator",
    tags=["calculator"]
)

# Path to calculator problems data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "data")

# Built-in sample problems (until JSON files are created)
SAMPLE_PROBLEMS = {
    "TVM": [
        {
            "problem_id": "CALC-TVM-001",
            "worksheet": "TVM",
            "problem_text": "You invest $10,000 today at 8% annual interest compounded quarterly. What will be the value in 5 years?",
            "given": {"PV": -10000, "I/Y": 8, "N_years": 5, "P/Y": 4, "C/Y": 4},
            "find": "FV",
            "correct_answer": 14859.47,
            "tolerance": 0.01,
            "steps": [
                "Press [2ND] [CLR TVM] to clear TVM worksheet",
                "Enter 10000 [+/-] [PV]",
                "Enter 8 [I/Y]",
                "Press [2ND] [P/Y], enter 4, press [ENTER]",
                "Enter 5 [2ND] [xP/Y] [N] (this calculates 5×4=20)",
                "Press [CPT] [FV]",
                "Answer: 14,859.47"
            ],
            "common_mistakes": [
                "Forgetting to set P/Y and C/Y to 4",
                "Not making PV negative (cash outflow)",
                "Using 5 directly for N instead of 20 periods"
            ],
            "difficulty": "medium"
        },
        {
            "problem_id": "CALC-TVM-002",
            "worksheet": "TVM",
            "problem_text": "A bond pays $50 semi-annually for 10 years and returns $1,000 at maturity. If the required return is 6% annually, what is the present value?",
            "given": {"PMT": 50, "FV": 1000, "I/Y": 6, "N_years": 10, "P/Y": 2},
            "find": "PV",
            "correct_answer": -1148.77,
            "tolerance": 0.01,
            "steps": [
                "Press [2ND] [CLR TVM]",
                "Enter 50 [PMT]",
                "Enter 1000 [FV]",
                "Enter 6 [I/Y]",
                "Press [2ND] [P/Y], enter 2, press [ENTER]",
                "Enter 10 [2ND] [xP/Y] [N] (20 periods)",
                "Press [CPT] [PV]",
                "Answer: -1,148.77"
            ],
            "common_mistakes": [
                "Using annual periods instead of semi-annual",
                "Forgetting to adjust I/Y for payment frequency"
            ],
            "difficulty": "medium"
        },
        {
            "problem_id": "CALC-TVM-003",
            "worksheet": "TVM",
            "problem_text": "You want to have $1,000,000 in 30 years. If you can earn 7% annually, how much must you save each month?",
            "given": {"FV": 1000000, "I/Y": 7, "N_years": 30, "P/Y": 12, "PV": 0},
            "find": "PMT",
            "correct_answer": -820.15,
            "tolerance": 0.50,
            "steps": [
                "Press [2ND] [CLR TVM]",
                "Enter 1000000 [FV]",
                "Enter 0 [PV]",
                "Enter 7 [I/Y]",
                "Press [2ND] [P/Y], enter 12, press [ENTER]",
                "Enter 30 [2ND] [xP/Y] [N] (360 periods)",
                "Press [CPT] [PMT]",
                "Answer: -820.15"
            ],
            "common_mistakes": [
                "Not setting P/Y to 12 for monthly payments",
                "Forgetting that PMT will be negative (cash outflow)"
            ],
            "difficulty": "easy"
        }
    ],
    "CF": [
        {
            "problem_id": "CALC-CF-001",
            "worksheet": "CF",
            "problem_text": "Calculate the NPV and IRR for an investment requiring $100,000 initial outlay with expected cash flows of $30,000 per year for 5 years. The required rate of return is 10%.",
            "given": {"CF0": -100000, "CF1": 30000, "F1": 5, "I": 10},
            "find": "NPV, IRR",
            "correct_answer": {"NPV": 13723.60, "IRR": 15.24},
            "tolerance": 0.05,
            "steps": [
                "Press [CF]",
                "Enter 100000 [+/-] [ENTER] ↓",
                "Enter 30000 [ENTER] ↓",
                "Enter 5 [ENTER] ↓",
                "Press [NPV]",
                "Enter 10 [ENTER] ↓",
                "Press [CPT] → NPV = 13,723.60",
                "Press [IRR] [CPT] → IRR = 15.24%"
            ],
            "common_mistakes": [
                "Forgetting to make CF0 negative",
                "Not entering frequency (F) for repeating cash flows"
            ],
            "difficulty": "medium"
        },
        {
            "problem_id": "CALC-CF-002",
            "worksheet": "CF",
            "problem_text": "A project costs $50,000 and generates: Year 1: $15,000, Year 2: $20,000, Year 3: $25,000, Year 4: $10,000. Calculate IRR.",
            "given": {"CF0": -50000, "CF1": 15000, "CF2": 20000, "CF3": 25000, "CF4": 10000},
            "find": "IRR",
            "correct_answer": 14.49,
            "tolerance": 0.05,
            "steps": [
                "Press [CF]",
                "Enter 50000 [+/-] [ENTER] ↓",
                "Enter 15000 [ENTER] ↓ [ENTER] ↓",
                "Enter 20000 [ENTER] ↓ [ENTER] ↓",
                "Enter 25000 [ENTER] ↓ [ENTER] ↓",
                "Enter 10000 [ENTER] ↓ [ENTER] ↓",
                "Press [IRR] [CPT]",
                "Answer: 14.49%"
            ],
            "common_mistakes": [
                "Entering cash flows in wrong order",
                "Missing the frequency input for each CF"
            ],
            "difficulty": "medium"
        }
    ],
    "Bond": [
        {
            "problem_id": "CALC-BOND-001",
            "worksheet": "Bond",
            "problem_text": "Calculate the price of a bond with 5% coupon, 10 years to maturity, YTM of 6%, face value $1,000, semi-annual payments.",
            "given": {"CPN": 5, "RV": 100, "YLD": 6, "years": 10, "frequency": 2},
            "find": "PRI",
            "correct_answer": 92.56,
            "tolerance": 0.01,
            "steps": [
                "Press [2ND] [BOND]",
                "Set SDT (settlement date)",
                "Set CPN = 5 [ENTER]",
                "Set RDT (redemption date - 10 years from SDT)",
                "Set RV = 100 [ENTER]",
                "Set ACT (day count)",
                "Set 2/Y (semi-annual)",
                "Set YLD = 6 [ENTER]",
                "Press [CPT] on PRI",
                "Answer: 92.56"
            ],
            "common_mistakes": [
                "Not setting correct day count convention",
                "Confusing coupon rate with YTM"
            ],
            "difficulty": "hard"
        }
    ],
    "Stats": [
        {
            "problem_id": "CALC-STAT-001",
            "worksheet": "Stats",
            "problem_text": "Calculate the mean and standard deviation of the following returns: 5%, 8%, -2%, 12%, 7%",
            "given": {"data": [5, 8, -2, 12, 7]},
            "find": "mean, std",
            "correct_answer": {"mean": 6.0, "std": 4.69},
            "tolerance": 0.01,
            "steps": [
                "Press [2ND] [DATA]",
                "Press [2ND] [CLR WORK]",
                "Enter 5 [ENTER] ↓↓",
                "Enter 8 [ENTER] ↓↓",
                "Enter -2 [ENTER] ↓↓",
                "Enter 12 [ENTER] ↓↓",
                "Enter 7 [ENTER] ↓↓",
                "Press [2ND] [STAT]",
                "Scroll to find x̄ = 6.0",
                "Scroll to find Sx = 4.69"
            ],
            "common_mistakes": [
                "Confusing population (σ) vs sample (s) standard deviation",
                "Not clearing previous data"
            ],
            "difficulty": "easy"
        }
    ],
    "Interest": [
        {
            "problem_id": "CALC-INT-001",
            "worksheet": "Interest",
            "problem_text": "Convert 8% nominal rate compounded quarterly to effective annual rate.",
            "given": {"NOM": 8, "C/Y": 4},
            "find": "EFF",
            "correct_answer": 8.24,
            "tolerance": 0.01,
            "steps": [
                "Press [2ND] [ICONV]",
                "Enter 8 [ENTER] ↓",
                "Enter 4 [ENTER] ↓",
                "Press [CPT] on EFF",
                "Answer: 8.24%"
            ],
            "common_mistakes": [
                "Confusing which rate to enter",
                "Wrong compounding frequency"
            ],
            "difficulty": "easy"
        }
    ]
}


def load_calculator_problems(worksheet_type: str) -> List[dict]:
    """Load calculator problems from JSON or use samples."""
    filepath = os.path.join(DATA_PATH, "calculator", f"{worksheet_type.lower()}_problems.json")

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f).get("problems", [])

    # Return sample problems
    return SAMPLE_PROBLEMS.get(worksheet_type, [])


@router.get("/problems/{worksheet_type}")
async def get_problems(
    worksheet_type: str,
    limit: int = Query(10, description="Number of problems"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    current_user: User = Depends(get_current_user)
):
    """Get calculator problems by worksheet type."""
    valid_types = ["TVM", "CF", "Bond", "Stats", "Interest", "Amort"]

    if worksheet_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid worksheet type. Must be one of: {valid_types}"
        )

    problems = load_calculator_problems(worksheet_type)

    if difficulty:
        problems = [p for p in problems if p.get("difficulty") == difficulty]

    # Random selection
    if len(problems) > limit:
        problems = random.sample(problems, limit)

    return {
        "worksheet_type": worksheet_type,
        "count": len(problems),
        "problems": problems
    }


@router.get("/problem/{problem_id}")
async def get_problem(
    problem_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific problem by ID."""
    for worksheet_type in SAMPLE_PROBLEMS.keys():
        problems = load_calculator_problems(worksheet_type)
        for problem in problems:
            if problem.get("problem_id") == problem_id:
                return problem

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Problem {problem_id} not found"
    )


@router.post("/check")
async def check_answer(
    request: CalculatorCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check user's calculator answer and record session."""
    # Find the problem
    problem = None
    for worksheet_type in SAMPLE_PROBLEMS.keys():
        problems = load_calculator_problems(worksheet_type)
        for p in problems:
            if p.get("problem_id") == request.problem_id:
                problem = p
                break
        if problem:
            break

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )

    # Check answer
    correct_answer = problem.get("correct_answer")
    tolerance = problem.get("tolerance", 0.01)

    is_correct = False
    if isinstance(correct_answer, dict):
        # Multiple answers (like NPV and IRR)
        is_correct = all(
            abs(request.user_answer.get(key, 0) - value) <= tolerance
            for key, value in correct_answer.items()
        )
    else:
        is_correct = abs(request.user_answer - correct_answer) <= abs(correct_answer * tolerance)

    # Record session
    session = CalculatorSession(
        user_id=current_user.id,
        worksheet_type=problem.get("worksheet"),
        problem_id=request.problem_id,
        problem_data=problem,
        user_steps=request.user_steps,
        user_answer=request.user_answer if isinstance(request.user_answer, float) else None,
        is_correct=is_correct,
        time_spent_seconds=request.time_spent_seconds
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "user_answer": request.user_answer,
        "steps": problem.get("steps", []),
        "common_mistakes": problem.get("common_mistakes", []),
        "session_id": session.id
    }


@router.get("/stats", response_model=CalculatorStatsResponse)
async def get_calculator_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calculator practice statistics."""
    sessions = db.query(CalculatorSession).filter(
        CalculatorSession.user_id == current_user.id
    ).all()

    # Group by worksheet type
    by_type = {}
    total_correct = 0
    total_attempts = 0

    for session in sessions:
        ws_type = session.worksheet_type
        if ws_type not in by_type:
            by_type[ws_type] = {"attempts": 0, "correct": 0}

        by_type[ws_type]["attempts"] += 1
        total_attempts += 1

        if session.is_correct:
            by_type[ws_type]["correct"] += 1
            total_correct += 1

    # Calculate accuracy per type
    for ws_type in by_type:
        attempts = by_type[ws_type]["attempts"]
        correct = by_type[ws_type]["correct"]
        by_type[ws_type]["accuracy"] = (correct / attempts * 100) if attempts > 0 else 0

    return {
        "total_attempts": total_attempts,
        "total_correct": total_correct,
        "overall_accuracy": (total_correct / total_attempts * 100) if total_attempts > 0 else 0,
        "by_worksheet_type": by_type,
        "recent_sessions": sessions[-10:] if sessions else []
    }


@router.get("/random")
async def get_random_problem(
    worksheet_type: Optional[str] = Query(None, description="Filter by type"),
    current_user: User = Depends(get_current_user)
):
    """Get a random calculator problem."""
    all_problems = []

    if worksheet_type:
        all_problems = load_calculator_problems(worksheet_type)
    else:
        for ws_type in SAMPLE_PROBLEMS.keys():
            all_problems.extend(load_calculator_problems(ws_type))

    if not all_problems:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No problems available"
        )

    return random.choice(all_problems)
