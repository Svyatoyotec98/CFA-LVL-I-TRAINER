#!/usr/bin/env python3
"""Debug: find all Q. positions and answer positions on a page"""

import fitz

def debug_positions(pdf_path, page_num=0):
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    print(f"\n{'='*60}")
    print(f"PAGE {page_num + 1} - Q. and Answer positions")
    print(f"{'='*60}\n")

    # Find all "Q." instances
    q_rects = page.search_for("Q.")
    print(f"Found {len(q_rects)} 'Q.' instances:")
    for i, rect in enumerate(q_rects):
        print(f"  Q.{i+1}: y0={rect.y0:.1f}, y1={rect.y1:.1f}")

    # Find all "The correct answer is" instances
    answer_patterns = ["The correct answer is A", "The correct answer is B", "The correct answer is C"]
    print(f"\nSearching for answer markers:")
    for pattern in answer_patterns:
        rects = page.search_for(pattern)
        if rects:
            for rect in rects:
                print(f"  '{pattern}': y0={rect.y0:.1f}, y1={rect.y1:.1f}")

    doc.close()

if __name__ == "__main__":
    pdf_path = "/home/user/CFA-LVL-I-TRAINER/Materials/QBank/Tests/Quants/Chapters/Copy of CH-1-Quantitative_Methods-Answers-3-39.pdf"

    # Check first 5 pages
    for page_num in range(5):
        debug_positions(pdf_path, page_num)
