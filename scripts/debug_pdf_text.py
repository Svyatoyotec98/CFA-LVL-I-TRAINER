#!/usr/bin/env python3
"""Debug script to see actual text content in PDF"""

import fitz

def debug_pdf_text(pdf_path, page_num=0):
    """Print all text from a specific page to see actual content"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    # Get all text
    text = page.get_text()

    print(f"\n{'='*60}")
    print(f"PAGE {page_num + 1} TEXT CONTENT")
    print(f"{'='*60}\n")
    print(text)
    print(f"\n{'='*60}")

    # Also search for various end patterns
    print("\n🔍 Searching for end patterns:")
    patterns = [
        "CFA Level 1,",
        "CFA Level 1",
        "CFA Level",
        "Level 1",
        "AnalystPrep",
        "www.",
        "©"
    ]

    for pattern in patterns:
        results = page.search_for(pattern)
        if results:
            print(f"  ✓ Found '{pattern}': {len(results)} instances")
            for i, rect in enumerate(results):
                print(f"    [{i+1}] {rect}")
        else:
            print(f"  ✗ NOT found: '{pattern}'")

    doc.close()

if __name__ == "__main__":
    pdf_path = "/home/user/CFA-LVL-I-TRAINER/Materials/QBank/Tests/Quants/Chapters/Copy of CH-1-Quantitative_Methods-Answers-3-39.pdf"

    # Check first 3 pages
    for page_num in range(3):
        debug_pdf_text(pdf_path, page_num)
        print("\n" + "="*60 + "\n")
