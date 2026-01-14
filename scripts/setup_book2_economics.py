#!/usr/bin/env python3
"""
Setup book2_economics v2 structure
Creates frontend/data/v2/book2_economics/ with 8 modules
"""

import os
import json
import shutil
from pathlib import Path

# Mapping: notes page range → qbank question range
BOOK2_ECONOMICS_MAPPING = [
    {"module": 1, "notes": "3-43", "qbank": "3-30"},
    {"module": 2, "notes": "44-66", "qbank": "31-49"},
    {"module": 3, "notes": "67-88", "qbank": "50-62"},
    {"module": 4, "notes": "89-112", "qbank": "63-85"},
    {"module": 5, "notes": "113-139", "qbank": "86-97"},
    {"module": 6, "notes": "140-154", "qbank": "98-112"},
    {"module": 7, "notes": "155-182", "qbank": "113-136"},
    {"module": 8, "notes": "183-195", "qbank": None},  # No separate qbank for module 8
]

# Module names based on CFA Level I Economics curriculum
MODULE_NAMES = [
    "Topics in Demand and Supply Analysis",
    "The Firm and Market Structures",
    "Aggregate Output, Prices and Economic Growth",
    "Understanding Business Cycles",
    "Monetary and Fiscal Policy",
    "International Trade and Capital Flows",
    "Currency Exchange Rates",
    "Economic Growth (optional module)"
]

def setup_book2_economics():
    """Setup book2_economics structure with all 8 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book2_economics"
    notes_dir = f"{base_dir}/Materials/notes/Economics/Chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/Economics/Chapters"

    print("🚀 Setting up book2_economics structure...")
    print(f"Base: {v2_dir}")

    for i, mapping in enumerate(BOOK2_ECONOMICS_MAPPING):
        module_num = mapping["module"]
        notes_range = mapping["notes"]
        qbank_range = mapping["qbank"]
        module_name = MODULE_NAMES[i]

        print(f"\n📁 Module {module_num}: {module_name}")
        print(f"   Notes: pages {notes_range}")
        if qbank_range:
            print(f"   QBank: questions {qbank_range}")
        else:
            print(f"   QBank: None (no separate qbank)")

        # Create module directory structure
        module_dir = f"{v2_dir}/module{module_num}"
        sources_dir = f"{module_dir}/sources"
        Path(sources_dir).mkdir(parents=True, exist_ok=True)

        # Find and copy notes PDF
        notes_pattern = f"CH-2-Economics-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Find and copy QBank PDF
        if qbank_range:
            qbank_pattern = f"Copy of CH-2-Economics-Answers-{qbank_range}.pdf"
            qbank_src = f"{qbank_dir}/{qbank_pattern}"
            qbank_dst = f"{sources_dir}/qbank.pdf"

            if os.path.exists(qbank_src):
                shutil.copy2(qbank_src, qbank_dst)
                print(f"   ✓ Copied qbank.pdf (Q.{qbank_range})")
            else:
                print(f"   ✗ QBank not found: {qbank_src}")
        else:
            print(f"   ⚠️  No QBank file for this module")

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
        "book_id": 2,
        "book_code": "CH-2",
        "book_name": "Economics",
        "book_name_ru": "Экономика",
        "total_modules": 8,
        "modules": [
            {
                "module_id": i + 1,
                "module_name": MODULE_NAMES[i],
                "page_range": BOOK2_ECONOMICS_MAPPING[i]["notes"],
                "question_range": BOOK2_ECONOMICS_MAPPING[i]["qbank"] or "N/A",
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
    print(f"✅ book2_economics structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 8")
    print(f"\nStructure:")
    print(f"  book2_economics/")
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
    setup_book2_economics()
