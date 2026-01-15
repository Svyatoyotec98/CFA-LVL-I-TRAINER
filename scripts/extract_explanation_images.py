#!/usr/bin/env python3
"""
CHECKPOINT 1: Extract explanation images from QBank PDFs
Instead of parsing text, we extract explanations as images.

Strategy:
1. Convert PDF pages to images
2. Find text boundaries:
   - START: "The correct answer is X."
   - END: "CFA Level 1," (appears at end of each explanation)
3. Crop the explanation area as separate image
4. Save to frontend/images/explanations/
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
from PIL import Image
import io

def find_text_instances(page, search_text):
    """Find all instances of text on a page and return their bounding boxes."""
    instances = page.search_for(search_text)
    return instances

def extract_explanation_boundaries(pdf_path, output_dir="output/checkpoint1", max_pages=15):
    """
    CHECKPOINT 1: Find explanation boundaries in PDF

    Args:
        pdf_path: Path to QBank PDF file
        output_dir: Where to save debug output
        max_pages: Maximum pages to process (for testing)
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Open PDF
    doc = fitz.open(pdf_path)

    print(f"\n📄 Processing: {pdf_path}")
    print(f"📊 Total pages: {len(doc)}")
    print(f"🔍 Processing first {max_pages} pages for CHECKPOINT 1\n")

    explanations_found = []

    for page_num in range(min(max_pages, len(doc))):
        page = doc[page_num]

        print(f"--- Page {page_num + 1} ---")

        # Find "The correct answer is" instances
        answer_patterns = [
            "The correct answer is A",
            "The correct answer is B",
            "The correct answer is C"
        ]

        answer_rects = []
        for pattern in answer_patterns:
            rects = find_text_instances(page, pattern)
            if rects:
                answer_rects.extend([(pattern, rect) for rect in rects])

        # Find "Q." instances (marks START of next question = END of previous explanation)
        # "CFA Level..." is metadata WITHIN the explanation, not the end!
        end_markers = []

        # Pattern: "Q." followed by number (start of next question)
        q_rects = find_text_instances(page, "Q.")
        end_markers.extend([("Q.", rect) for rect in q_rects])

        print(f"  ✓ Found {len(answer_rects)} answer markers")
        print(f"  ✓ Found {len(end_markers)} end markers")

        # Match answer starts with ends
        for i, (answer_text, answer_rect) in enumerate(answer_rects):
            print(f"\n  📍 Explanation {i+1}:")
            print(f"     Start: {answer_text}")
            print(f"     Start coords: {answer_rect}")

            # Find the closest end marker below this answer
            closest_end = None
            closest_end_type = None
            min_distance = float('inf')

            for end_type, end_rect in end_markers:
                # End should be below answer (larger y1 coordinate)
                if end_rect.y0 > answer_rect.y1:
                    distance = end_rect.y0 - answer_rect.y1
                    if distance < min_distance:
                        min_distance = distance
                        closest_end = end_rect
                        closest_end_type = end_type

            # For CHECKPOINT 1: if no end marker found on same page,
            # crop to bottom of page (explanations often span multiple pages)
            if closest_end:
                print(f"     End: {closest_end_type}")
                print(f"     End coords: {closest_end}")
                bottom_y = closest_end.y0 - 5  # slightly above next Q.
            else:
                print(f"     End: BOTTOM OF PAGE (explanation continues or no next Q found)")
                # Use page bottom minus margin (~ 50 points from bottom)
                bottom_y = page.rect.height - 50

            # Define bounding box for explanation
            # x: use full page width (or detect margins)
            # y: from answer start to end marker
            bbox = fitz.Rect(
                50,  # left margin
                answer_rect.y0,  # top (answer start)
                page.rect.width - 50,  # right margin
                bottom_y  # bottom (end marker or page end)
            )

            print(f"     Bounding box: {bbox}")
            print(f"     Height: {bbox.height:.1f} points")

            # Extract this region as image
            mat = fitz.Matrix(2, 2)  # 2x scale for better quality
            pix = page.get_pixmap(matrix=mat, clip=bbox)

            # Save image
            img_filename = f"page{page_num+1}_explanation{i+1}.png"
            img_path = os.path.join(output_dir, img_filename)
            pix.save(img_path)

            print(f"     ✅ Saved: {img_filename}")

            explanations_found.append({
                "page": page_num + 1,
                "index": i + 1,
                "answer": answer_text,
                "bbox": bbox,
                "image_path": img_path,
                "has_end_marker": closest_end is not None
            })

        # Also save full page as reference
        mat = fitz.Matrix(1.5, 1.5)  # 1.5x scale
        pix = page.get_pixmap(matrix=mat)
        page_img_path = os.path.join(output_dir, f"page{page_num+1}_full.png")
        pix.save(page_img_path)
        print(f"\n  💾 Full page saved: page{page_num+1}_full.png")

    doc.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 CHECKPOINT 1 SUMMARY")
    print(f"{'='*60}")

    total = len(explanations_found)
    with_end = sum(1 for e in explanations_found if e['has_end_marker'])
    without_end = total - with_end

    print(f"Total explanations extracted: {total}")
    print(f"  ✓ With end marker (same page): {with_end} ({with_end/total*100:.1f}%)" if total > 0 else "")
    print(f"  ⚠️  Without end marker (multi-page?): {without_end} ({without_end/total*100:.1f}%)" if total > 0 else "")
    print(f"\nOutput directory: {output_dir}")
    print(f"\nNext steps:")
    print(f"1. Review extracted images in {output_dir}")
    print(f"2. Check if boundaries are correct")
    print(f"3. If good → proceed to CHECKPOINT 2 (full extraction)")

    return explanations_found

if __name__ == "__main__":
    # Test with one QBank PDF
    pdf_path = "/home/user/CFA-LVL-I-TRAINER/Materials/QBank/Tests/Quants/Chapters/Copy of CH-1-Quantitative_Methods-Answers-3-39.pdf"

    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        exit(1)

    results = extract_explanation_boundaries(pdf_path)  # uses default max_pages=15

    print(f"\n✅ CHECKPOINT 1 complete!")
    print(f"   Check output/checkpoint1/ for extracted images")
