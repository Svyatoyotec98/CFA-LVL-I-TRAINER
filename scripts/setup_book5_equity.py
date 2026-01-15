#!/usr/bin/env python3
"""
Setup book5_equity v2 structure
Creates frontend/data/v2/book5_equity/ with 8 modules
"""

import os
import json
import shutil
from pathlib import Path

# Mapping: notes page range → qbank question range
BOOK5_EQUITY_MAPPING = [
    {"module": 1, "notes": "3-41", "qbank": "3-50"},
    {"module": 2, "notes": "42-68", "qbank": "51-103"},
    {"module": 3, "notes": "69-88", "qbank": "104-156"},
    {"module": 4, "notes": "89-107", "qbank": "157-190"},
    {"module": 5, "notes": "108-146", "qbank": "191-224"},
    {"module": 6, "notes": "147-185", "qbank": "225-277"},
    {"module": 7, "notes": "186-216", "qbank": "278-308"},
    {"module": 8, "notes": "217-251", "qbank": "309-388"},
]

# Module names based on CFA Level I Equity curriculum
MODULE_NAMES = [
    "Market Organization and Structure",
    "Security Market Indexes",
    "Market Efficiency",
    "Overview of Equity Securities",
    "Introduction to Industry and Company Analysis",
    "Equity Valuation: Concepts and Basic Tools",
    "Introduction to Fixed-Income Valuation",
    "Fixed-Income Securities: Defining Elements"
]

def setup_book5_equity():
    """Setup book5_equity structure with all 8 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book5_equity"
    notes_dir = f"{base_dir}/Materials/notes/Equity/Chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/Equity/Chapters"

    print("🚀 Setting up book5_equity structure...")
    print(f"Base: {v2_dir}")

    for i, mapping in enumerate(BOOK5_EQUITY_MAPPING):
        module_num = mapping["module"]
        notes_range = mapping["notes"]
        qbank_range = mapping["qbank"]
        module_name = MODULE_NAMES[i]

        print(f"\n📁 Module {module_num}: {module_name}")
        print(f"   Notes: pages {notes_range}")
        print(f"   QBank: questions {qbank_range}")

        # Create module directory structure
        module_dir = f"{v2_dir}/module{module_num}"
        sources_dir = f"{module_dir}/sources"
        Path(sources_dir).mkdir(parents=True, exist_ok=True)

        # Find and copy notes PDF
        notes_pattern = f"CH-5-Equity-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Find and copy QBank PDF
        qbank_pattern = f"Copy of CH-5-Equity-Answers-{qbank_range}.pdf"
        qbank_src = f"{qbank_dir}/{qbank_pattern}"
        qbank_dst = f"{sources_dir}/qbank.pdf"

        if os.path.exists(qbank_src):
            shutil.copy2(qbank_src, qbank_dst)
            print(f"   ✓ Copied qbank.pdf (Q.{qbank_range})")
        else:
            print(f"   ✗ QBank not found: {qbank_src}")

        # Create empty glossary.json
        glossary_path = f"{module_dir}/glossary.json"
        with open(glossary_path, 'w', encoding='utf-8') as f:
            json.dump({"terms": []}, f, indent=2)
        print(f"   ✓ Created glossary.json")

        # Create empty questions.json
        questions_path = f"{module_dir}/questions.json"
        with open(questions_path, 'w', encoding='utf-8') as f:
            json.dump({"questions": []}, f, indent=2)
        print(f"   ✓ Created questions.json")

    # Create meta.json
    meta = {
        "book_id": 5,
        "book_code": "CH-5",
        "book_name": "Equity Investments",
        "book_name_ru": "Инвестиции в акции",
        "total_modules": 8,
        "modules": [
            {
                "module_id": i + 1,
                "module_name": MODULE_NAMES[i],
                "page_range": BOOK5_EQUITY_MAPPING[i]["notes"],
                "question_range": BOOK5_EQUITY_MAPPING[i]["qbank"],
                "los_codes": [f"LOS_{i+1}a", f"LOS_{i+1}b"]
            }
            for i in range(8)
        ]
    }

    meta_path = f"{v2_dir}/meta.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Created meta.json")

    print(f"\n{'='*60}")
    print(f"✅ book5_equity structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 8")

if __name__ == "__main__":
    setup_book5_equity()
