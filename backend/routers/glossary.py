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

# Path to glossary data (v2 structure)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "data", "v2")

# Mapping book_id to folder name
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


def load_glossary_data(book_id: int) -> dict:
    """Load glossary JSON data for a book from v2 structure.

    Aggregates terms from all modules in the book:
    frontend/data/v2/book{N}_{name}/module{M}/glossary.json
    """
    if book_id not in BOOK_FOLDERS:
        return {"book_id": book_id, "terms": [], "modules": []}

    book_folder = BOOK_FOLDERS[book_id]
    book_path = os.path.join(DATA_PATH, book_folder)

    if not os.path.exists(book_path):
        return {"book_id": book_id, "terms": [], "modules": []}

    # Find all module directories
    all_terms = []
    module_info = []
    book_name = None
    book_name_ru = None

    # Scan for module1, module2, module3, etc.
    module_dirs = sorted([
        d for d in os.listdir(book_path)
        if os.path.isdir(os.path.join(book_path, d)) and d.startswith("module")
    ], key=lambda x: int(x.replace("module", "")))

    for module_dir in module_dirs:
        glossary_file = os.path.join(book_path, module_dir, "glossary.json")

        if os.path.exists(glossary_file):
            try:
                with open(glossary_file, 'r', encoding='utf-8') as f:
                    module_data = json.load(f)

                # Extract book metadata from first module
                if book_name is None:
                    book_name = module_data.get("book_name")
                    book_name_ru = module_data.get("book_name_ru")

                # Add module info
                module_info.append({
                    "module_id": module_data.get("module_id"),
                    "module_name": module_data.get("module_name"),
                    "module_name_ru": module_data.get("module_name_ru"),
                    "term_count": len(module_data.get("terms", []))
                })

                # Add all terms from this module
                for term in module_data.get("terms", []):
                    # Ensure module_id is set
                    if "module_id" not in term:
                        term["module_id"] = module_data.get("module_id")
                    all_terms.append(term)

            except Exception as e:
                print(f"Error loading {glossary_file}: {e}")
                continue

    return {
        "book_id": book_id,
        "book_name": book_name or f"Book {book_id}",
        "book_name_ru": book_name_ru or f"Книга {book_id}",
        "total_modules": len(module_info),
        "modules": module_info,
        "terms": all_terms
    }


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
    """Get glossary terms for a specific module (v2 structure)."""
    if book_id not in BOOK_FOLDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )

    book_folder = BOOK_FOLDERS[book_id]
    module_path = os.path.join(DATA_PATH, book_folder, f"module{module_id}")
    glossary_file = os.path.join(module_path, "glossary.json")

    if not os.path.exists(glossary_file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {module_id} glossary not found for book {book_id}"
        )

    try:
        with open(glossary_file, 'r', encoding='utf-8') as f:
            module_data = json.load(f)

        # Ensure all terms have module_id
        for term in module_data.get("terms", []):
            if "module_id" not in term:
                term["module_id"] = module_data.get("module_id")

        return {
            "book_id": book_id,
            "book_name": module_data.get("book_name"),
            "module_id": module_id,
            "module_name": module_data.get("module_name"),
            "module_name_ru": module_data.get("module_name_ru"),
            "los_list": module_data.get("los_list", []),
            "total": len(module_data.get("terms", [])),
            "terms": module_data.get("terms", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading module glossary: {str(e)}"
        )


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
