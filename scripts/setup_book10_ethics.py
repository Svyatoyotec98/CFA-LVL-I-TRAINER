#!/usr/bin/env python3
"""
Setup book10_ethics v2 structure
Creates frontend/data/v2/book10_ethics/ with 5 modules
"""

import os
import json
import shutil
from pathlib import Path

BOOK10_ETHICS_MAPPING = [
    {"module": 1, "notes": "3-10", "qbank": "3-7"},
    {"module": 2, "notes": "11-18", "qbank": "8-84"},
    {"module": 3, "notes": "19-83", "qbank": "85-194"},
    {"module": 4, "notes": "84-93", "qbank": "195-206"},
    {"module": 5, "notes": "94-158", "qbank": "207-270"},
]

MODULE_NAMES = [
    "Code of Ethics and Standards of Professional Conduct",
    "Guidance for Standards I-VII",
    "Application of the Standards",
    "Introduction to the Global Investment Performance Standards (GIPS)",
    "The GIPS Standards"
]

def setup_book10_ethics():
    """Setup book10_ethics structure with all 5 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book10_ethics"
    notes_dir = f"{base_dir}/Materials/notes/Ethics/Chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/Ethics/Chapters"

    print("🚀 Setting up book10_ethics structure...")
    print(f"Base: {v2_dir}")

    for i, mapping in enumerate(BOOK10_ETHICS_MAPPING):
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
        notes_pattern = f"CH-10-Ethics-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Copy QBank PDF
        qbank_pattern = f"Copy of CH-10-Ethics-Answers-{qbank_range}.pdf"
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
        "book_id": 10,
        "book_code": "CH-10",
        "book_name": "Ethics and Professional Standards",
        "book_name_ru": "Этика и профессиональные стандарты",
        "total_modules": 5,
        "modules": [
            {
                "module_id": i + 1,
                "module_name": MODULE_NAMES[i],
                "page_range": BOOK10_ETHICS_MAPPING[i]["notes"],
                "question_range": BOOK10_ETHICS_MAPPING[i]["qbank"],
                "los_codes": [f"LOS_{i+1}a", f"LOS_{i+1}b"]
            }
            for i in range(5)
        ]
    }

    with open(f"{v2_dir}/meta.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Created meta.json")

    print(f"\n{'='*60}")
    print(f"✅ book10_ethics structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 5")

if __name__ == "__main__":
    setup_book10_ethics()
