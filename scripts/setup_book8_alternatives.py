#!/usr/bin/env python3
"""
Setup book8_alternatives v2 structure
Creates frontend/data/v2/book8_alternatives/ with 7 modules
"""

import os
import json
import shutil
from pathlib import Path

BOOK8_ALTERNATIVES_MAPPING = [
    {"module": 1, "notes": "3-32", "qbank": "3-41"},
    {"module": 2, "notes": "33-58", "qbank": "42-67"},
    {"module": 3, "notes": "59-82", "qbank": "68-120"},
    {"module": 4, "notes": "83-115", "qbank": "121-171"},
    {"module": 5, "notes": "116-137", "qbank": "172-197"},
    {"module": 6, "notes": "138-164", "qbank": "198-262"},
    {"module": 7, "notes": "165-193", "qbank": "263-297"},
]

MODULE_NAMES = [
    "Introduction to Alternative Investments",
    "Real Estate Investments",
    "Private Equity",
    "Hedge Funds",
    "Commodities",
    "Infrastructure Investments",
    "Other Alternative Investments"
]

def setup_book8_alternatives():
    """Setup book8_alternatives structure with all 7 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book8_alternatives"
    notes_dir = f"{base_dir}/Materials/notes/Alternative investments/Chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/Alternative Investments/Chapters"

    print("🚀 Setting up book8_alternatives structure...")
    print(f"Base: {v2_dir}")

    for i, mapping in enumerate(BOOK8_ALTERNATIVES_MAPPING):
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
        notes_pattern = f"CH-8-Alternative_Investments-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Copy QBank PDF
        qbank_pattern = f"Copy of CH-8-Alternative_Investments-Answers-{qbank_range}.pdf"
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
        "book_id": 8,
        "book_code": "CH-8",
        "book_name": "Alternative Investments",
        "book_name_ru": "Альтернативные инвестиции",
        "total_modules": 7,
        "modules": [
            {
                "module_id": i + 1,
                "module_name": MODULE_NAMES[i],
                "page_range": BOOK8_ALTERNATIVES_MAPPING[i]["notes"],
                "question_range": BOOK8_ALTERNATIVES_MAPPING[i]["qbank"],
                "los_codes": [f"LOS_{i+1}a", f"LOS_{i+1}b"]
            }
            for i in range(7)
        ]
    }

    with open(f"{v2_dir}/meta.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Created meta.json")

    print(f"\n{'='*60}")
    print(f"✅ book8_alternatives structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 7")

if __name__ == "__main__":
    setup_book8_alternatives()
