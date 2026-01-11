"""
Glossary router - handles terms and definitions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os

from ..database import get_db
from ..models import User
from ..auth import get_current_user

router = APIRouter(
    prefix="/api/glossary",
    tags=["glossary"]
)

# Path to glossary data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "data", "glossary")


def load_glossary_data(book_id: int) -> dict:
    """Load glossary JSON data for a book."""
    filename = f"book{book_id}_terms.json"
    filepath = os.path.join(DATA_PATH, filename)

    if not os.path.exists(filepath):
        return {"book_id": book_id, "terms": []}

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_glossary() -> List[dict]:
    """Load all glossary data from all books."""
    all_terms = []

    for book_id in range(1, 11):
        try:
            data = load_glossary_data(book_id)
            for term in data.get("terms", []):
                term["book_id"] = book_id
                term["book_name"] = data.get("book_name", f"Book {book_id}")
                all_terms.append(term)
        except Exception:
            continue

    return all_terms


@router.get("")
async def get_all_terms(
    limit: int = Query(100, description="Maximum terms to return"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user)
):
    """Get all glossary terms across all books."""
    all_terms = load_all_glossary()

    return {
        "total": len(all_terms),
        "terms": all_terms[offset:offset + limit]
    }


@router.get("/book/{book_id}")
async def get_book_terms(
    book_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get glossary terms for a specific book."""
    data = load_glossary_data(book_id)

    return {
        "book_id": book_id,
        "book_name": data.get("book_name", f"Book {book_id}"),
        "total": len(data.get("terms", [])),
        "terms": data.get("terms", [])
    }


@router.get("/search")
async def search_terms(
    q: str = Query(..., min_length=2, description="Search query"),
    book_id: Optional[int] = Query(None, description="Filter by book"),
    limit: int = Query(50, description="Maximum results"),
    current_user: User = Depends(get_current_user)
):
    """Search glossary terms by keyword."""
    query = q.lower()

    if book_id:
        data = load_glossary_data(book_id)
        all_terms = data.get("terms", [])
        for term in all_terms:
            term["book_id"] = book_id
    else:
        all_terms = load_all_glossary()

    # Search in term names and definitions
    results = []
    for term in all_terms:
        term_en = term.get("term_en", "").lower()
        term_ru = term.get("term_ru", "").lower()
        def_en = term.get("definition_en", "").lower()
        def_ru = term.get("definition_ru", "").lower()

        if query in term_en or query in term_ru or query in def_en or query in def_ru:
            results.append(term)

        if len(results) >= limit:
            break

    return {
        "query": q,
        "total": len(results),
        "terms": results
    }


@router.get("/term/{term_id}")
async def get_term(
    term_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific term by ID."""
    all_terms = load_all_glossary()

    for term in all_terms:
        if term.get("term_id") == term_id:
            return term

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Term {term_id} not found"
    )


@router.get("/module/{book_id}/{module_id}")
async def get_module_terms(
    book_id: int,
    module_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get glossary terms related to a specific module."""
    data = load_glossary_data(book_id)

    # Filter terms by module_id
    module_terms = [
        term for term in data.get("terms", [])
        if term.get("module_id") == module_id
    ]

    return {
        "book_id": book_id,
        "module_id": module_id,
        "total": len(module_terms),
        "terms": module_terms
    }


@router.get("/random")
async def get_random_terms(
    count: int = Query(10, description="Number of random terms"),
    book_id: Optional[int] = Query(None, description="Filter by book"),
    current_user: User = Depends(get_current_user)
):
    """Get random terms for flashcard practice."""
    import random

    if book_id:
        data = load_glossary_data(book_id)
        all_terms = data.get("terms", [])
        for term in all_terms:
            term["book_id"] = book_id
    else:
        all_terms = load_all_glossary()

    if not all_terms:
        return {"terms": []}

    count = min(count, len(all_terms))
    selected = random.sample(all_terms, count)

    return {
        "count": len(selected),
        "terms": selected
    }
