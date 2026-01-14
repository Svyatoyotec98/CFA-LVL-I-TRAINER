#!/usr/bin/env python3
"""
Setup book9_portfolio v2 structure
Creates frontend/data/v2/book9_portfolio/ with 5 modules
"""

import os
import json
import shutil
from pathlib import Path

# Note: QBank has 6 question sets but Notes has 5 modules
# Module 5 spans two QBank sets
BOOK9_PORTFOLIO_MAPPING = [
    {"module": 1, "notes": "3-27", "qbank": "3-46"},
    {"module": 2, "notes": "28-62", "qbank": "47-93"},
    {"module": 3, "notes": "63-104", "qbank": "94-113"},
    {"module": 4, "notes": "105-125", "qbank": "114-160"},
    {"module": 5, "notes": "126-152", "qbank": "161-181,182-216"},  # spans 2 QBank sets
]

MODULE_NAMES = [
    "Portfolio Risk and Return: Part I",
    "Portfolio Risk and Return: Part II",
    "Basics of Portfolio Planning and Construction",
    "Introduction to Risk Management",
    "Fintech in Investment Management"
]

def setup_book9_portfolio():
    """Setup book9_portfolio structure with all 5 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book9_portfolio"
    notes_dir = f"{base_dir}/Materials/notes/Portfolio management/Chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/Portfolio mathematics/Chapters"

    print("🚀 Setting up book9_portfolio structure...")
    print(f"Base: {v2_dir}")

    for i, mapping in enumerate(BOOK9_PORTFOLIO_MAPPING):
        module_num = mapping["module"]
        notes_range = mapping["notes"]
        qbank_range = mapping["qbank"]
        module_name = MODULE_NAMES[i]

        print(f"\n📁 Module {module_num}: {module_name}")
        print(f"   Notes: pages {notes_range}")
        print(f"   QBank: questions {qbank_range}")

        module_dir = f"{v2_dir}/module{module_num}"
        sources_dir = f"{module_dir}/sources"
        Path(sources_dir).mkdir(parents=True, exist_ok=True)

        # Copy notes PDF
        notes_pattern = f"CH-9-Portfolio_Management-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Copy QBank PDF(s) - module 5 may have 2 files
        if "," in qbank_range:
            # Multiple QBank files - just use first one for now
            qbank_range_first = qbank_range.split(",")[0]
            qbank_pattern = f"Copy of CH-9-Portfolio_Management-Answers-{qbank_range_first}.pdf"
        else:
            qbank_pattern = f"Copy of CH-9-Portfolio_Management-Answers-{qbank_range}.pdf"

        qbank_src = f"{qbank_dir}/{qbank_pattern}"
        qbank_dst = f"{sources_dir}/qbank.pdf"

        if os.path.exists(qbank_src):
            shutil.copy2(qbank_src, qbank_dst)
            print(f"   ✓ Copied qbank.pdf (Q.{qbank_range})")
        else:
            print(f"   ✗ QBank not found: {qbank_src}")

        # Create empty glossary.json
        with open(f"{module_dir}/glossary.json", 'w', encoding='utf-8') as f:
            json.dump({"terms": []}, f, indent=2)
        print(f"   ✓ Created glossary.json")

        # Create empty questions.json
        with open(f"{module_dir}/questions.json", 'w', encoding='utf-8') as f:
            json.dump({"questions": []}, f, indent=2)
        print(f"   ✓ Created questions.json")

    # Create meta.json
    meta = {
        "book_id": 9,
        "book_code": "CH-9",
        "book_name": "Portfolio Management",
        "book_name_ru": "Управление портфелем",
        "total_modules": 5,
        "modules": [
            {
                "module_id": i + 1,
                "module_name": MODULE_NAMES[i],
                "page_range": BOOK9_PORTFOLIO_MAPPING[i]["notes"],
                "question_range": BOOK9_PORTFOLIO_MAPPING[i]["qbank"],
                "los_codes": [f"LOS_{i+1}a", f"LOS_{i+1}b"]
            }
            for i in range(5)
        ]
    }

    with open(f"{v2_dir}/meta.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Created meta.json")

    print(f"\n{'='*60}")
    print(f"✅ book9_portfolio structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 5")

if __name__ == "__main__":
    setup_book9_portfolio()
