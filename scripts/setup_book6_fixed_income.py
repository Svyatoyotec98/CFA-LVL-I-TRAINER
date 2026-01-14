#!/usr/bin/env python3
"""
Setup book6_fixed_income v2 structure
Creates frontend/data/v2/book6_fixed_income/ with 19 modules
"""

import os
import json
import shutil
from pathlib import Path

# Mapping: notes page range → qbank question range
BOOK6_FIXED_INCOME_MAPPING = [
    {"module": 1, "notes": "-1-12", "qbank": "3-23"},
    {"module": 2, "notes": "-13-27", "qbank": "24-47"},
    {"module": 3, "notes": "-28-41", "qbank": "48-69"},
    {"module": 4, "notes": "-42-59", "qbank": "70-84"},
    {"module": 5, "notes": "-60-71", "qbank": "85-93"},
    {"module": 6, "notes": "-72-94", "qbank": "94-118"},
    {"module": 7, "notes": "-95-111", "qbank": "119-130"},
    {"module": 8, "notes": "-112-122", "qbank": "131-151"},
    {"module": 9, "notes": "-123-137", "qbank": "152-173"},
    {"module": 10, "notes": "-138-151", "qbank": "174-198"},
    {"module": 11, "notes": "-152-159", "qbank": "199-221"},
    {"module": 12, "notes": "-160-170", "qbank": "222-229"},
    {"module": 13, "notes": "-171-186", "qbank": "230-232"},
    {"module": 14, "notes": "-187-197", "qbank": "233-248"},
    {"module": 15, "notes": "-198-204", "qbank": "249-256"},
    {"module": 16, "notes": "-205-221", "qbank": "257-277"},
    {"module": 17, "notes": "-222-229", "qbank": "278-289"},
    {"module": 18, "notes": "-230-243", "qbank": "290-301"},
    {"module": 19, "notes": "-244-259", "qbank": "302-323"},
]

MODULE_NAMES = [
    "Fixed-Income Securities: Defining Elements",
    "Fixed-Income Markets: Issuance, Trading, and Funding",
    "Introduction to Fixed-Income Valuation",
    "Introduction to Asset-Backed Securities",
    "Understanding Fixed-Income Risk and Return",
    "Fundamentals of Credit Analysis",
    "The Term Structure and Interest Rate Dynamics",
    "Credit Analysis Models",
    "Credit Default Swaps",
    "Fixed-Income Portfolio Management",
    "Yield Curve Strategies",
    "Fixed-Income Active Management",
    "Measurement of Interest Rate Risk",
    "Managing Credit Risk",
    "Structured Financial Instruments",
    "Municipal Bonds",
    "Sovereign Debt",
    "Agency MBS and CMOs",
    "Corporate Bonds"
]

def setup_book6_fixed_income():
    """Setup book6_fixed_income structure with all 19 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book6_fixed_income"
    notes_dir = f"{base_dir}/Materials/notes/Fixed Income/Chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/Fixed Income/Chapters"

    print("🚀 Setting up book6_fixed_income structure...")
    print(f"Base: {v2_dir}")

    for i, mapping in enumerate(BOOK6_FIXED_INCOME_MAPPING):
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
        notes_pattern = f"CH-6-Fixed_Income-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Find and copy QBank PDF
        qbank_pattern = f"Copy of CH-6-Fixed_Income-Answers-{qbank_range}.pdf"
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
        "book_id": 6,
        "book_code": "CH-6",
        "book_name": "Fixed Income",
        "book_name_ru": "Инструменты с фиксированным доходом",
        "total_modules": 19,
        "modules": [
            {
                "module_id": i + 1,
                "module_name": MODULE_NAMES[i],
                "page_range": BOOK6_FIXED_INCOME_MAPPING[i]["notes"],
                "question_range": BOOK6_FIXED_INCOME_MAPPING[i]["qbank"],
                "los_codes": [f"LOS_{i+1}a", f"LOS_{i+1}b"]
            }
            for i in range(19)
        ]
    }

    meta_path = f"{v2_dir}/meta.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Created meta.json")

    print(f"\n{'='*60}")
    print(f"✅ book6_fixed_income structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 19 (largest book!)")

if __name__ == "__main__":
    setup_book6_fixed_income()
