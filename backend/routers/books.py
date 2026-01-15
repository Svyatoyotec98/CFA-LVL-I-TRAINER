"""
Books router - handles book metadata and structure.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import json
import os

router = APIRouter(
    prefix="/api/books",
    tags=["books"]
)

# Path to books data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "data", "books")


def load_book_metadata(book_id: int) -> dict:
    """Load book JSON data and return metadata without questions."""
    filename = f"book{book_id}.json"
    filepath = os.path.join(DATA_PATH, filename)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} data not found"
        )

    with open(filepath, 'r', encoding='utf-8') as f:
        book_data = json.load(f)

    # Remove questions from modules to reduce payload size
    if "learning_modules" in book_data:
        for module in book_data["learning_modules"]:
            # Keep module metadata but remove questions
            questions_count = len(module.get("questions", []))
            module["questions_count"] = questions_count
            module.pop("questions", None)

    return book_data


@router.get("/{book_id}")
async def get_book_metadata(book_id: int):
    """
    Get book metadata including modules structure but without questions.
    This is used by the frontend to display available modules.
    """
    return load_book_metadata(book_id)


@router.get("/")
async def get_all_books():
    """
    Get list of all available books with basic info.
    """
    books = []

    for book_id in range(1, 11):  # Assuming books 1-10
        try:
            book_data = load_book_metadata(book_id)
            # Return only basic info
            books.append({
                "book_id": book_data.get("book_id"),
                "book_name": book_data.get("book_name"),
                "book_name_ru": book_data.get("book_name_ru"),
                "total_questions": book_data.get("total_questions"),
                "modules_count": len(book_data.get("learning_modules", []))
            })
        except HTTPException:
            continue

    return books
