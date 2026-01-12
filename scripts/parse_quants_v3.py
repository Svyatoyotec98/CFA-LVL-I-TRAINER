#!/usr/bin/env python3
"""
Parser v3 for CFA Quantitative Methods - handles unusual PDF structure
where options appear AFTER explanations.
"""

import re
import json
from pathlib import Path

MODULES = {
    1: {"name": "Rate and Return", "name_ru": "Ставки и доходности"},
    2: {"name": "The Time Value of Money in Finance", "name_ru": "Временная стоимость денег"},
    3: {"name": "Statistical Measures of Asset Returns", "name_ru": "Статистические показатели доходности"},
    4: {"name": "Probability Trees and Conditional Expectations", "name_ru": "Деревья вероятностей и условные ожидания"},
    5: {"name": "Portfolio Mathematics", "name_ru": "Портфельная математика"},
    6: {"name": "Simulation Methods", "name_ru": "Методы симуляции"},
    7: {"name": "Estimation and Inference", "name_ru": "Оценка и статистические выводы"},
    8: {"name": "Hypothesis Testing", "name_ru": "Проверка гипотез"},
    9: {"name": "Parametric and Non Parametric Tests of Independence", "name_ru": "Параметрические и непараметрические тесты независимости"},
    10: {"name": "Simple Linear Regression", "name_ru": "Простая линейная регрессия"},
    11: {"name": "Introduction to Big Data Techniques", "name_ru": "Введение в методы Big Data"},
}


def clean_text(text):
    """Remove copyright notices and clean whitespace."""
    text = re.sub(r'©\s*2014-2024 AnalystPrep\.\s*\d*', '', text)
    return text


def parse_answer_file(text):
    """Parse the answers file which has a specific structure."""
    text = clean_text(text)

    questions = {}
    current_module = 1

    # Find module boundaries for module detection
    module_positions = []
    for match in re.finditer(r'Learning Module (\d+):', text):
        module_positions.append((match.start(), int(match.group(1))))

    # Find all questions
    q_pattern = r'Q\.(\d+)\s+'
    q_matches = list(re.finditer(q_pattern, text))

    print(f"Found {len(q_matches)} question markers")

    for i, q_match in enumerate(q_matches):
        q_num = q_match.group(1)
        q_start = q_match.end()

        # Find end of this question block
        q_end = q_matches[i + 1].start() if i + 1 < len(q_matches) else len(text)
        block = text[q_start:q_end]

        # Determine module
        q_pos = q_match.start()
        for pos, mod_id in module_positions:
            if pos < q_pos:
                current_module = mod_id

        # Find "The correct answer is X"
        correct_match = re.search(r'The correct answer is\s+([ABC])[\.\s]', block)
        if not correct_match:
            continue

        correct_answer = correct_match.group(1)

        # Question text is from start to "The correct answer"
        q_text = block[:correct_match.start()].strip()
        q_text = re.sub(r'\s+', ' ', q_text)

        # Find options A, B, C - they can be anywhere in the block
        # Look for patterns like "A. something" or "A. $123" at start of line
        options = {}

        # Try to find all option patterns in the block
        # Options usually appear as "A. text" pattern
        opt_lines = []
        for line in block.split('\n'):
            line = line.strip()
            if re.match(r'^[ABC]\.\s+', line):
                opt_lines.append(line)

        for line in opt_lines:
            match = re.match(r'^([ABC])\.\s+(.+)$', line)
            if match:
                letter = match.group(1)
                value = match.group(2).strip()
                # Only take first occurrence of each option
                if letter not in options and value:
                    options[letter] = value

        # If we don't have all 3 options, skip
        if len(options) < 3:
            # Try alternative: find consecutive A, B, C lines
            lines = block.split('\n')
            for idx, line in enumerate(lines):
                line = line.strip()
                if re.match(r'^A\.\s+', line) and idx + 2 < len(lines):
                    a_line = line
                    b_line = lines[idx + 1].strip()
                    c_line = lines[idx + 2].strip()

                    if re.match(r'^B\.\s+', b_line) and re.match(r'^C\.\s+', c_line):
                        options['A'] = re.sub(r'^A\.\s+', '', a_line)
                        options['B'] = re.sub(r'^B\.\s+', '', b_line)
                        options['C'] = re.sub(r'^C\.\s+', '', c_line)
                        break

        if len(options) < 3:
            continue

        # Extract explanation
        expl_start = correct_match.end()

        # Find where wrong explanations or LOS reference starts
        wrong_match = re.search(r'[ABC]\s+is incorrect', block[expl_start:])
        los_match = re.search(r'CFA Level', block[expl_start:])

        expl_end = len(block)
        if wrong_match:
            expl_end = min(expl_end, expl_start + wrong_match.start())
        if los_match:
            expl_end = min(expl_end, expl_start + los_match.start())

        explanation = block[expl_start:expl_end]
        explanation = re.sub(r'\s+', ' ', explanation).strip()

        # Extract wrong explanations
        explanation_wrong = {}
        wrong_pattern = r'([ABC])\s+is incorrect[.:]?\s*(.+?)(?=[ABC]\s+is incorrect|CFA Level|[ABC]\.\s+|$)'
        for match in re.finditer(wrong_pattern, block, re.DOTALL):
            letter = match.group(1)
            if letter != correct_answer:
                expl = match.group(2)
                expl = re.sub(r'\s+', ' ', expl).strip()
                if expl and len(expl) > 5:
                    explanation_wrong[letter] = expl

        # Extract LOS reference
        los_ref = None
        los_match = re.search(r'LOS\s*[\(\[]([a-z])[\)\]]', block)
        if los_match:
            los_ref = f"LOS {los_match.group(1)}"

        questions[q_num] = {
            'module_id': current_module,
            'question_text': q_text,
            'options': options,
            'correct_answer': correct_answer,
            'explanation': explanation,
            'explanation_wrong': explanation_wrong,
            'los_reference': los_ref
        }

    return questions


def build_book_json(questions):
    """Build the final book1.json structure."""
    modules_data = {i: [] for i in range(1, 12)}

    for q_num, q_data in questions.items():
        module_id = q_data['module_id']

        question_obj = {
            "question_id": f"QM-{module_id}-{q_num.zfill(4)}",
            "question_text": q_data['question_text'],
            "question_text_formula": None,
            "has_table": False,
            "has_image": False,
            "image_path": None,
            "options": q_data['options'],
            "correct_answer": q_data['correct_answer'],
            "explanation": q_data['explanation'],
            "explanation_wrong": q_data['explanation_wrong'],
            "calculator_steps": None,
            "difficulty": "medium",
            "los_reference": q_data['los_reference']
        }

        modules_data[module_id].append(question_obj)

    book1 = {
        "book_id": 1,
        "book_name": "Quantitative Methods",
        "book_name_ru": "Количественные методы",
        "total_questions": sum(len(m) for m in modules_data.values()),
        "learning_modules": []
    }

    for mod_id in range(1, 12):
        if modules_data[mod_id]:
            modules_data[mod_id].sort(key=lambda x: int(re.search(r'(\d+)$', x['question_id']).group()))

            module_obj = {
                "module_id": mod_id,
                "module_name": MODULES[mod_id]["name"],
                "module_name_ru": MODULES[mod_id]["name_ru"],
                "questions": modules_data[mod_id]
            }
            book1["learning_modules"].append(module_obj)

    return book1


def main():
    base_path = Path('/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests')

    a_text = (base_path / 'CH-1-Quantitative_Methods-Answers.txt').read_text()

    questions = parse_answer_file(a_text)
    print(f"Parsed {len(questions)} complete questions")

    book1 = build_book_json(questions)

    print(f"\nTotal questions: {book1['total_questions']}")
    for mod in book1["learning_modules"]:
        print(f"  Module {mod['module_id']}: {mod['module_name']} - {len(mod['questions'])} questions")

    # Target counts from screenshot
    target = {1: 39, 2: 23, 3: 26, 4: 31, 5: 12, 6: 8, 7: 15, 8: 50, 9: 13, 10: 15, 11: 3}
    print(f"\nTarget vs Actual:")
    for mod in book1["learning_modules"]:
        t = target.get(mod['module_id'], 0)
        a = len(mod['questions'])
        diff = a - t
        status = "✓" if abs(diff) <= 3 else "✗"
        print(f"  Module {mod['module_id']}: target={t}, actual={a}, diff={diff:+d} {status}")

    output_path = Path('/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book1_new.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(book1, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {output_path}")


if __name__ == '__main__':
    main()
