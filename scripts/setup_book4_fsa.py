#!/usr/bin/env python3
"""
Setup book4_fsa v2 structure
Creates frontend/data/v2/book4_fsa/ with 12 modules
"""

import os
import json
import shutil
from pathlib import Path

# Mapping: notes page range → qbank question range
BOOK4_FSA_MAPPING = [
    {"module": 1, "notes": "3-27", "qbank": "3-31"},
    {"module": 2, "notes": "28-60", "qbank": "32-73"},
    {"module": 3, "notes": "61-86", "qbank": "74-99"},
    {"module": 4, "notes": "87-113", "qbank": "100-143"},
    {"module": 5, "notes": "114-129", "qbank": "144-162"},
    {"module": 6, "notes": "130-145", "qbank": "163-206"},
    {"module": 7, "notes": "146-166", "qbank": "207-242"},
    {"module": 8, "notes": "167-190", "qbank": "243-267"},
    {"module": 9, "notes": "191-212", "qbank": "268-306"},
    {"module": 10, "notes": "213-265", "qbank": "307-360"},
    {"module": 11, "notes": "266-320", "qbank": "361-401"},
    {"module": 12, "notes": "321-341", "qbank": "402-408"},
]

# Module names based on CFA Level I FSA curriculum
MODULE_NAMES = [
    "Introduction to Financial Statement Analysis",
    "Analyzing Income Statements",
    "Analyzing Balance Sheets",
    "Analyzing Statements of Cash Flows",
    "Analysis of Inventories",
    "Analysis of Long-Lived Assets",
    "Analysis of Income Taxes",
    "Analysis of Non-Current Liabilities",
    "Analysis of Financial Institutions",
    "Analysis of Intercorporate Investments",
    "Employee Compensation",
    "Analysis of Financial Reporting Quality"
]

def setup_book4_fsa():
    """Setup book4_fsa structure with all 12 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book4_fsa"
    notes_dir = f"{base_dir}/Materials/notes/FSA/Chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/FSA/Chapters"

    print("🚀 Setting up book4_fsa structure...")
    print(f"Base: {v2_dir}")

    for i, mapping in enumerate(BOOK4_FSA_MAPPING):
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
        notes_pattern = f"CH-4-Financial_Statements_Analysis-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Find and copy QBank PDF
        qbank_pattern = f"Copy of CH-4-Financial_Statements_Analysis-Answers-{qbank_range}.pdf"
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
        "book_id": 4,
        "book_code": "CH-4",
        "book_name": "Financial Statement Analysis",
        "book_name_ru": "Анализ финансовой отчетности",
        "total_modules": 12,
        "modules": [
            {
                "module_id": i + 1,
                "module_name": MODULE_NAMES[i],
                "page_range": BOOK4_FSA_MAPPING[i]["notes"],
                "question_range": BOOK4_FSA_MAPPING[i]["qbank"],
                "los_codes": [f"LOS_{i+1}a", f"LOS_{i+1}b"]
            }
            for i in range(12)
        ]
    }

    meta_path = f"{v2_dir}/meta.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Created meta.json")

    print(f"\n{'='*60}")
    print(f"✅ book4_fsa structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 12 (largest book!)")
    print(f"\nStructure:")
    print(f"  book4_fsa/")
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
    setup_book4_fsa()
