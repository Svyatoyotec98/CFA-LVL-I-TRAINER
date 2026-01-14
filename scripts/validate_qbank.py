#!/usr/bin/env python3
"""
QBank Validation Script
Проверяет качество распарсенных вопросов
"""

import json
import sys
from pathlib import Path


def validate_qbank(qbank_path):
    """Validate parsed QBank JSON"""

    with open(qbank_path, 'r') as f:
        data = json.load(f)

    total = len(data['questions'])
    errors = []
    warnings = []

    print(f"🔍 Validating {qbank_path}")
    print(f"📝 Total questions: {total}\n")

    for i, q in enumerate(data['questions'], 1):
        q_id = q['question_id']
        q_num = q['question_number']

        # CRITICAL ERRORS (блокируют работу)

        # 1. No options
        if len(q['options']) == 0:
            errors.append(f"Q{i} ({q_id}, orig Q.{q_num}): ❌ НЕТ ОПЦИЙ")

        # 2. Missing options (less than 3)
        elif len(q['options']) < 3:
            errors.append(f"Q{i} ({q_id}, orig Q.{q_num}): ❌ Только {len(q['options'])} опции (нужно 3)")

        # 3. Invalid correct_option_id
        option_ids = [o['id'] for o in q['options']]
        if q['correct_option_id'] not in option_ids:
            errors.append(f"Q{i} ({q_id}, orig Q.{q_num}): ❌ Invalid correct_option_id '{q['correct_option_id']}'")

        # WARNINGS (не блокируют, но снижают качество)

        # 4. "The correct answer is" in question_text
        if 'correct answer' in q['question_text'].lower():
            warnings.append(f"Q{i} ({q_id}): ⚠️ Dirty question_text (contains 'correct answer')")

        # 5. Options too long or contain garbage
        for opt in q['options']:
            if len(opt['text']) > 100:
                warnings.append(f"Q{i} ({q_id}): ⚠️ Option {opt['id']} слишком длинный ({len(opt['text'])} chars)")

            # Check for garbage keywords
            garbage_keywords = ['since there', 'Invest in', 'Annuity due', 'incorrect', 'compounding', 'Exhibit']
            if any(kw in opt['text'] for kw in garbage_keywords):
                warnings.append(f"Q{i} ({q_id}): ⚠️ Option {opt['id']} содержит мусор: '{opt['text'][:50]}...'")

        # 6. Explanation truncated
        if q['explanation'] and not q['explanation'].rstrip().endswith(('.', '!', '?', '...')):
            if len(q['explanation']) < 50:
                warnings.append(f"Q{i} ({q_id}): ⚠️ Explanation слишком короткий ({len(q['explanation'])} chars)")

    # Print results
    print("\n" + "="*70)

    if errors:
        print(f"\n❌ CRITICAL ERRORS ({len(errors)}):")
        for err in errors:
            print(f"  {err}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warn in warnings[:10]:  # Show first 10
            print(f"  {warn}")
        if len(warnings) > 10:
            print(f"  ... и ещё {len(warnings) - 10} warnings")

    # Summary statistics
    clean_questions = total - len([e for e in errors if 'НЕТ ОПЦИЙ' in e or 'Только' in e])
    clean_percentage = 100 * clean_questions / total if total > 0 else 0

    print(f"\n" + "="*70)
    print(f"📊 SUMMARY:")
    print(f"  Total questions: {total}")
    print(f"  ❌ Critical errors: {len(errors)}")
    print(f"  ⚠️  Warnings: {len(warnings)}")
    print(f"  ✅ Usable questions: {clean_questions}/{total} ({clean_percentage:.1f}%)")

    # Quality thresholds
    if len(errors) > 0:
        print(f"\n🚫 VALIDATION FAILED: {len(errors)} critical errors found")
        print(f"   Fix these errors before proceeding to next checkpoint")
        return False
    elif len(warnings) > total * 0.3:  # More than 30% warnings
        print(f"\n⚠️  QUALITY WARNING: {len(warnings)} warnings ({100*len(warnings)/total:.1f}% of questions)")
        print(f"   Consider reviewing and improving parser")
        return True  # Don't block, but warn
    else:
        print(f"\n✅ VALIDATION PASSED")
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_qbank.py <qbank_json_path>")
        print("Example: python validate_qbank.py frontend/data/qbank/book1_ch2_questions.json")
        sys.exit(1)

    qbank_path = Path(sys.argv[1])

    if not qbank_path.exists():
        print(f"❌ File not found: {qbank_path}")
        sys.exit(1)

    success = validate_qbank(qbank_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
