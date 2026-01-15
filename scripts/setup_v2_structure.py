#!/usr/bin/env python3
"""
Setup v2 data structure for CFA Trainer
Reorganizes Materials/ into frontend/data/v2/ with clear book/module structure
"""

import os
import json
import shutil
from pathlib import Path

# Mapping: notes page range → qbank question range
BOOK1_QUANTS_MAPPING = [
    {"module": 1, "notes": "3-30", "qbank": "3-39"},
    {"module": 2, "notes": "31-73", "qbank": "40-75"},
    {"module": 3, "notes": "74-108", "qbank": "76-111"},
    {"module": 4, "notes": "109-125", "qbank": "112-152"},
    {"module": 5, "notes": "126-144", "qbank": "153-167"},
    {"module": 6, "notes": "145-161", "qbank": "168-182"},
    {"module": 7, "notes": "162-177", "qbank": "183-203"},
    {"module": 8, "notes": "178-216", "qbank": "204-263"},
    {"module": 9, "notes": "217-229", "qbank": "264-280"},
    {"module": 10, "notes": "230-280", "qbank": "281-304"},
    {"module": 11, "notes": "281-291", "qbank": "305-310"},
]

def setup_book1_quants():
    """Setup book1_quants structure with all 11 modules"""

    base_dir = "/home/user/CFA-LVL-I-TRAINER"
    v2_dir = f"{base_dir}/frontend/data/v2/book1_quants"
    notes_dir = f"{base_dir}/Materials/notes/quants/chapters"
    qbank_dir = f"{base_dir}/Materials/QBank/Tests/Quants/Chapters"

    print("🚀 Setting up book1_quants structure...")
    print(f"Base: {v2_dir}")

    for mapping in BOOK1_QUANTS_MAPPING:
        module_num = mapping["module"]
        notes_range = mapping["notes"]
        qbank_range = mapping["qbank"]

        print(f"\n📁 Module {module_num}:")
        print(f"   Notes: pages {notes_range}")
        print(f"   QBank: questions {qbank_range}")

        # Create module directory structure
        module_dir = f"{v2_dir}/module{module_num}"
        sources_dir = f"{module_dir}/sources"
        Path(sources_dir).mkdir(parents=True, exist_ok=True)

        # Find and copy notes PDF
        notes_pattern = f"CH-1-Quantitative_Methods-{notes_range}.pdf"
        notes_src = f"{notes_dir}/{notes_pattern}"
        notes_dst = f"{sources_dir}/notes.pdf"

        if os.path.exists(notes_src):
            shutil.copy2(notes_src, notes_dst)
            print(f"   ✓ Copied notes.pdf ({notes_range})")
        else:
            print(f"   ✗ Notes not found: {notes_src}")

        # Find and copy QBank PDF
        qbank_pattern = f"Copy of CH-1-Quantitative_Methods-Answers-{qbank_range}.pdf"
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

    print(f"\n{'='*60}")
    print(f"✅ book1_quants structure complete!")
    print(f"   Location: {v2_dir}")
    print(f"   Modules: 11")
    print(f"\nStructure:")
    print(f"  book1_quants/")
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
    setup_book1_quants()
