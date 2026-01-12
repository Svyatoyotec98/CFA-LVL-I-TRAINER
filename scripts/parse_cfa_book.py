#!/usr/bin/env python3
"""
Universal parser for CFA Level 1 books.
Parses Answers PDF text files into JSON format.

Usage:
    python parse_cfa_book.py <book_id> <input_txt> <output_json>

Example:
    python parse_cfa_book.py 9 CH-9-Portfolio_Management-Answers.txt book9.json
"""

import re
import json
import sys
from pathlib import Path

# Book configurations
BOOK_CONFIGS = {
    1: {
        "name": "Quantitative Methods",
        "name_ru": "Количественные методы",
        "prefix": "QM",
        "modules": {
            1: {"name": "Rate and Return", "name_ru": "Ставки и доходности"},
            2: {"name": "The Time Value of Money in Finance", "name_ru": "Временная стоимость денег"},
            3: {"name": "Statistical Measures of Asset Returns", "name_ru": "Статистические показатели доходности"},
            4: {"name": "Probability Trees and Conditional Expectations", "name_ru": "Деревья вероятностей"},
            5: {"name": "Portfolio Mathematics", "name_ru": "Портфельная математика"},
            6: {"name": "Simulation Methods", "name_ru": "Методы симуляции"},
            7: {"name": "Estimation and Inference", "name_ru": "Оценка и выводы"},
            8: {"name": "Hypothesis Testing", "name_ru": "Проверка гипотез"},
            9: {"name": "Parametric and Non Parametric Tests", "name_ru": "Параметрические тесты"},
            10: {"name": "Simple Linear Regression", "name_ru": "Линейная регрессия"},
            11: {"name": "Introduction to Big Data Techniques", "name_ru": "Big Data"},
        }
    },
    9: {
        "name": "Portfolio Management",
        "name_ru": "Управление портфелем",
        "prefix": "PM",
        "modules": {
            1: {"name": "Portfolio Risk & Return: Part I", "name_ru": "Риск и доходность портфеля: Часть I"},
            2: {"name": "Portfolio Risk & Return: Part II", "name_ru": "Риск и доходность портфеля: Часть II"},
            3: {"name": "Portfolio Management: An Overview", "name_ru": "Обзор управления портфелем"},
            4: {"name": "Basics of Portfolio Planning & Construction", "name_ru": "Основы планирования портфеля"},
            5: {"name": "The Behavioral Biases of Individuals", "name_ru": "Поведенческие предубеждения"},
            6: {"name": "Introduction to Risk Management", "name_ru": "Введение в риск-менеджмент"},
        }
    },
    10: {
        "name": "Ethics",
        "name_ru": "Этика",
        "prefix": "ETH",
        "modules": {
            1: {"name": "Ethics and Trust in the Investment Profession", "name_ru": "Этика и доверие"},
            2: {"name": "Code of Ethics and Standards of Professional Conduct", "name_ru": "Кодекс этики"},
            3: {"name": "Guidance for Standards I-VII", "name_ru": "Руководство по стандартам I-VII"},
            4: {"name": "Introduction to GIPS", "name_ru": "Введение в GIPS"},
            5: {"name": "Ethics Application", "name_ru": "Применение этики"},
        }
    },
}


def extract_module_from_text(text, book_id):
    """Extract module number from LOS or Learning Module reference."""
    # Pattern: "Learning Module X:" or "Module X:"
    module_match = re.search(r'(?:Learning\s+)?Module\s*(\d+)', text, re.IGNORECASE)
    if module_match:
        mod_num = int(module_match.group(1))
        max_modules = len(BOOK_CONFIGS.get(book_id, {}).get("modules", {}))
        if 1 <= mod_num <= max(max_modules, 11):
            return mod_num
    return 1


def parse_question(q_text, book_id):
    """Parse a single question from text."""
    config = BOOK_CONFIGS.get(book_id, {"prefix": f"B{book_id}", "modules": {}})
    prefix = config["prefix"]

    # Extract question number
    q_num_match = re.match(r'Q\.(\d+)\s*', q_text)
    if not q_num_match:
        return None
    q_num = q_num_match.group(1)

    # Find "The correct answer is X"
    correct_match = re.search(r'The correct answer is\s*([ABC])\.?\s*', q_text, re.IGNORECASE)
    if not correct_match:
        return None
    correct_answer = correct_match.group(1).upper()

    # Extract question text (from Q.XX to "The correct answer")
    question_text = q_text[q_num_match.end():correct_match.start()].strip()
    question_text = re.sub(r'\n+', ' ', question_text)
    question_text = re.sub(r'\s+', ' ', question_text).strip()

    # Extract options - find consecutive A. B. C. lines
    options = {}

    # Method 1: Find A. B. C. in sequence (typical format)
    options_block_pattern = r'(?:^|\n)\s*A\.\s*([^\n]+)\s*\n\s*B\.\s*([^\n]+)\s*\n\s*C\.\s*([^\n]+)'
    options_match = re.search(options_block_pattern, q_text)

    if options_match:
        for i, letter in enumerate(['A', 'B', 'C']):
            opt_val = options_match.group(i + 1).strip()
            # Filter out "is incorrect" and overly long values
            if 'incorrect' not in opt_val.lower() and len(opt_val) < 300:
                options[letter] = opt_val

    # Method 2: Find individual options if method 1 failed
    if len(options) < 3:
        for letter in ['A', 'B', 'C']:
            if letter not in options:
                # Look for pattern: X. value (on its own line, not "is incorrect")
                pattern = rf'(?:^|\n)\s*{letter}\.\s*([^\n]+?)(?:\n|$)'
                matches = re.findall(pattern, q_text)
                for match in matches:
                    val = match.strip()
                    if val and 'incorrect' not in val.lower() and len(val) < 300 and len(val) > 1:
                        options[letter] = val
                        break

    # Skip if we don't have the correct answer option
    if correct_answer not in options:
        return None

    # Extract explanation (text after "The correct answer is X" until "X is incorrect" or options)
    explanation = ""
    exp_start = correct_match.end()

    # Find where explanation ends
    incorrect_match = re.search(r'[ABC]\s+is incorrect', q_text[exp_start:], re.IGNORECASE)
    if incorrect_match:
        explanation = q_text[exp_start:exp_start + incorrect_match.start()].strip()
    elif options_match:
        # Explanation ends before options
        exp_end = options_match.start()
        if exp_end > exp_start:
            explanation = q_text[exp_start:exp_end].strip()

    # Clean explanation
    explanation = re.sub(r'\n+', ' ', explanation)
    explanation = re.sub(r'\s+', ' ', explanation).strip()

    # Extract wrong explanations
    explanation_wrong = {}
    for letter in ['A', 'B', 'C']:
        if letter != correct_answer:
            wrong_pattern = rf'{letter}\s+is incorrect\.?\s*(.*?)(?=[ABC]\s+is incorrect|\n\s*A\.|\n\s*©|CFA Level|\Z)'
            wrong_match = re.search(wrong_pattern, q_text, re.DOTALL | re.IGNORECASE)
            if wrong_match:
                wrong_exp = wrong_match.group(1).strip()
                wrong_exp = re.sub(r'\n+', ' ', wrong_exp)
                wrong_exp = re.sub(r'\s+', ' ', wrong_exp).strip()
                # Remove any trailing option values
                wrong_exp = re.sub(r'\s*[ABC]\.\s*[^\s].*$', '', wrong_exp)
                if wrong_exp and len(wrong_exp) > 5:
                    explanation_wrong[letter] = wrong_exp[:1000]  # Limit length

    # Extract LOS reference
    los_match = re.search(r'(CFA Level[^©]+?LOS[^©\n]+)', q_text, re.IGNORECASE | re.DOTALL)
    los_text = ""
    if los_match:
        los_text = los_match.group(1).strip()
        los_text = re.sub(r'\n+', ' ', los_text)
        los_text = re.sub(r'\s+', ' ', los_text).strip()

    # Determine module
    module_id = extract_module_from_text(los_text or q_text, book_id)

    return {
        "question_id": f"{prefix}-{module_id}-{q_num.zfill(3)}",
        "question_number": int(q_num),
        "question_text": question_text,
        "question_text_formula": None,
        "has_table": bool(re.search(r'Year\s+Return|\d{4}\s+[\d\.]+', q_text)),
        "has_image": False,
        "image_path": None,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation[:2000] if explanation else "",
        "explanation_wrong": explanation_wrong,
        "calculator_steps": None,
        "difficulty": "medium",
        "los_reference": los_text if los_text else None,
        "module_id": module_id
    }


def parse_all_questions(text_content, book_id):
    """Parse all questions from the text file."""
    # Split by Q.XXX pattern
    question_pattern = r'(Q\.\d+\s+.*?)(?=Q\.\d+\s+|\Z)'
    question_blocks = re.findall(question_pattern, text_content, re.DOTALL)

    print(f"Found {len(question_blocks)} question blocks")

    questions = []
    failed = 0
    for block in question_blocks:
        q = parse_question(block, book_id)
        if q and len(q['options']) >= 2:
            questions.append(q)
        else:
            failed += 1

    print(f"Successfully parsed {len(questions)} questions, failed: {failed}")
    return questions


def group_by_module(questions, book_id):
    """Group questions by module."""
    config = BOOK_CONFIGS.get(book_id, {"modules": {}})
    modules_config = config.get("modules", {})

    modules_dict = {}
    for q in questions:
        mod_id = q.get('module_id', 1)
        if mod_id not in modules_dict:
            modules_dict[mod_id] = []
        q_copy = {k: v for k, v in q.items() if k != 'module_id'}
        modules_dict[mod_id].append(q_copy)

    modules_list = []
    for mod_id in sorted(modules_dict.keys()):
        mod_info = modules_config.get(mod_id, {"name": f"Module {mod_id}", "name_ru": f"Модуль {mod_id}"})
        modules_list.append({
            "module_id": mod_id,
            "module_name": mod_info["name"],
            "module_name_ru": mod_info["name_ru"],
            "questions": sorted(modules_dict[mod_id], key=lambda x: x.get('question_number', 0))
        })

    return modules_list


def main():
    if len(sys.argv) < 4:
        print("Usage: python parse_cfa_book.py <book_id> <input_txt> <output_json>")
        sys.exit(1)

    book_id = int(sys.argv[1])
    input_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    config = BOOK_CONFIGS.get(book_id, {"name": f"Book {book_id}", "name_ru": f"Книга {book_id}"})

    print(f"Parsing Book {book_id}: {config['name']}")
    print(f"Reading {input_path}")

    text_content = input_path.read_text(encoding='utf-8')

    questions = parse_all_questions(text_content, book_id)
    modules = group_by_module(questions, book_id)

    output = {
        "book_id": book_id,
        "book_name": config["name"],
        "book_name_ru": config["name_ru"],
        "total_questions": len(questions),
        "learning_modules": modules
    }

    print(f"Saving to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSummary:")
    print(f"Total questions: {len(questions)}")
    print(f"Modules: {len(modules)}")
    for mod in modules:
        print(f"  Module {mod['module_id']}: {mod['module_name']} - {len(mod['questions'])} questions")


if __name__ == "__main__":
    main()
