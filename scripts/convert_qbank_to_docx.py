#!/usr/bin/env python3
"""
Convert all qbank.pdf files to qbank.docx in v2 structure
Uses pdf2docx library for conversion
"""

import os
from pathlib import Path
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_path, docx_path):
    """Convert a single PDF file to DOCX"""
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def convert_book(book_path, book_name):
    """Convert all qbank.pdf files in a book to docx"""
    print(f"\n{'='*60}")
    print(f"📚 {book_name}")
    print(f"{'='*60}")

    converted_count = 0
    failed_count = 0

    # Find all module directories
    modules = sorted([d for d in Path(book_path).iterdir() if d.is_dir() and d.name.startswith('module')])

    for module_dir in modules:
        sources_dir = module_dir / "sources"
        pdf_path = sources_dir / "qbank.pdf"
        docx_path = sources_dir / "qbank.docx"

        if not pdf_path.exists():
            print(f"⚠️  {module_dir.name}: qbank.pdf not found")
            continue

        if docx_path.exists():
            print(f"⏭️  {module_dir.name}: qbank.docx already exists (skipping)")
            continue

        print(f"🔄 {module_dir.name}: Converting qbank.pdf → qbank.docx...")

        if convert_pdf_to_docx(str(pdf_path), str(docx_path)):
            file_size = docx_path.stat().st_size / 1024  # KB
            print(f"   ✓ Created qbank.docx ({file_size:.1f} KB)")
            converted_count += 1
        else:
            failed_count += 1

    print(f"\n✅ {book_name}: {converted_count} converted, {failed_count} failed")
    return converted_count, failed_count

def main():
    base_dir = Path("/home/user/CFA-LVL-I-TRAINER/frontend/data/v2")

    books = [
        ("book1_quants", "Book 1: Quantitative Methods"),
        ("book2_economics", "Book 2: Economics"),
        ("book3_corporate", "Book 3: Corporate Issuers"),
        ("book4_fsa", "Book 4: Financial Statement Analysis"),
        ("book5_equity", "Book 5: Equity Investments"),
        ("book6_fixed_income", "Book 6: Fixed Income"),
        ("book7_derivatives", "Book 7: Derivatives"),
        ("book8_alternatives", "Book 8: Alternative Investments"),
        ("book9_portfolio", "Book 9: Portfolio Management"),
        ("book10_ethics", "Book 10: Ethics"),
    ]

    total_converted = 0
    total_failed = 0

    for book_dir, book_name in books:
        book_path = base_dir / book_dir
        if book_path.exists():
            converted, failed = convert_book(book_path, book_name)
            total_converted += converted
            total_failed += failed

    print(f"\n\n{'='*60}")
    print(f"🎉 CONVERSION COMPLETE!")
    print(f"{'='*60}")
    print(f"Total converted: {total_converted}")
    print(f"Total failed: {total_failed}")

if __name__ == "__main__":
    main()
