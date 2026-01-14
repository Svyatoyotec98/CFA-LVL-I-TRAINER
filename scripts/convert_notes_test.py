#!/usr/bin/env python3
"""
Convert notes.pdf to notes.docx for book1_quants/module1
"""

from pdf2docx import Converter
from pathlib import Path

pdf_path = "/home/user/CFA-LVL-I-TRAINER/frontend/data/v2/book1_quants/module1/sources/notes.pdf"
docx_path = "/home/user/CFA-LVL-I-TRAINER/frontend/data/v2/book1_quants/module1/sources/notes.docx"

print(f"Converting {pdf_path}")
print(f"Target: {docx_path}\n")

cv = Converter(pdf_path)
cv.convert(docx_path)
cv.close()

pdf_size = Path(pdf_path).stat().st_size / 1024
docx_size = Path(docx_path).stat().st_size / 1024

print(f"\n✅ Conversion complete!")
print(f"PDF:  {pdf_size:.1f} KB")
print(f"DOCX: {docx_size:.1f} KB")
