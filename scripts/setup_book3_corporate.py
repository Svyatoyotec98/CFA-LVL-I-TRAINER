#!/usr/bin/env python3
"""
Setup book3_corporate v2 structure
Creates frontend/data/v2/book3_corporate/ with 7 modules
"""

import os
import json
import shutil
from pathlib import Path

# Mapping: notes page range → qbank question range
BOOK3_CORPORATE_MAPPING = [
    {"module": 1, "notes": "3-19", "qbank": "3-14"},
    {"module": 2, "notes": "20-38", "qbank": "15-27"},
    {"module": 3, "notes": "39-54", "qbank": "28-44"},
    {"module": 4, "notes": "55-75", "qbank": "45-70"},
    {"module": 5, "notes": "76-99", "qbank": "71-152"},
    {"module": 6, "notes": "100-126", "qbank": "153-183"},
    {"module": 7, "notes": "127-139", "qbank": "184-194"},
]

# Module names based on CFA Level I Corporate Issuers curriculum
MODULE_NAMES = [
    "Introduction to Corporate Governance and Other ESG Considerations",
    "Capital Investments and Capital Allocation",
    "Capital Structure",
    "Business Models and Risks",
    "Measures of Leverage",
    "Working Capital Management",
    "Corporate Restructuring"
]

def setup_book3_corporate():
    """Setup book3_corporate structure with all 7 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book3_corporate"
    notes_dir = f"{base_dir}/Materials/notes/Corporate Issuers/Chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/Corporate Issuers/Chapters"

    print("🚀 Setting up book3_corporate structure...")
    print(f"Base: {v2_dir}")

    for i, mapping in enumerate(BOOK3_CORPORATE_MAPPING):
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
        notes_pattern = f"CH-3-Corporate_Issuers-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Find and copy QBank PDF
        qbank_pattern = f"Copy of CH-3-Corporate_Issuers-Answers-{qbank_range}.pdf"
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
        "book_id": 3,
        "book_code": "CH-3",
        "book_name": "Corporate Issuers",
        "book_name_ru": "Корпоративные эмитенты",
        "total_modules": 7,
        "modules": [
            {
                "module_id": i + 1,
                "module_name": MODULE_NAMES[i],
                "page_range": BOOK3_CORPORATE_MAPPING[i]["notes"],
                "question_range": BOOK3_CORPORATE_MAPPING[i]["qbank"],
                "los_codes": [f"LOS_{i+1}a", f"LOS_{i+1}b"]
            }
            for i in range(7)
        ]
    }

    meta_path = f"{v2_dir}/meta.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Created meta.json")

    print(f"\n{'='*60}")
    print(f"✅ book3_corporate structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 7")
    print(f"\nStructure:")
    print(f"  book3_corporate/")
    print(f"  ├── meta.json")
    print(f"  ├── module1/")
    print(f"  │   ├── sources/")
    print(f"  │   │   ├── notes.pdf")
    print(f"  │   │   └── qbank.pdf")
    print(f"  │   ├── glossary.json")
    print(f"  │   └── questions.json")
    print(f"  ├── module2/")
    print(f"  └── ...")

if __name__ == "__main__":
    setup_book3_corporate()
