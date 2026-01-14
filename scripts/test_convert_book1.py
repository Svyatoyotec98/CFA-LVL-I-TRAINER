#!/usr/bin/env python3
"""
Test conversion: Convert qbank.pdf to qbank.docx for book1_quants modules 1-3
"""

import os
from pathlib import Path
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_path, docx_path):
    """Convert a single PDF file to DOCX"""
    try:
        print(f"   Starting conversion...")
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

base_dir = Path("/home/user/CFA-LVL-I-TRAINER/frontend/data/v2/book1_quants")

print("🧪 Testing conversion on book1_quants modules 1-3\n")

for module_num in [1, 2, 3]:
    module_dir = base_dir / f"module{module_num}"
    sources_dir = module_dir / "sources"
    pdf_path = sources_dir / "qbank.pdf"
    docx_path = sources_dir / "qbank.docx"

    print(f"📁 Module {module_num}:")

    if not pdf_path.exists():
        print(f"   ✗ qbank.pdf not found")
        continue

    if docx_path.exists():
        print(f"   ℹ️  qbank.docx already exists")
        pdf_size = pdf_path.stat().st_size / 1024
        docx_size = docx_path.stat().st_size / 1024
        print(f"   PDF: {pdf_size:.1f} KB → DOCX: {docx_size:.1f} KB")
        continue

    print(f"   Converting qbank.pdf → qbank.docx...")

    if convert_pdf_to_docx(str(pdf_path), str(docx_path)):
        pdf_size = pdf_path.stat().st_size / 1024
        docx_size = docx_path.stat().st_size / 1024
        print(f"   ✓ Success! PDF: {pdf_size:.1f} KB → DOCX: {docx_size:.1f} KB")
    else:
        print(f"   ✗ Conversion failed")

    print()

print("✅ Test complete!")
