#!/usr/bin/env python3
"""
Parser for CFA Level 1 - Book 1: Quantitative Methods
Parses the Answers PDF text file into JSON format.

FORMAT OF PDF:
Q.XX question text
The correct answer is X.
explanation...
A is incorrect. reason...
B is incorrect. reason...
A. option_value
B. option_value
C. option_value
formulas...
© AnalystPrep
CFA Level I, ... LOS ...
"""

import re
import json
from pathlib import Path

# Module mapping based on Table of Contents
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

def extract_module_from_los(los_text, full_text=""):
    """Extract module number from LOS reference."""
    search_text = los_text or full_text
    if not search_text:
        return 1

    # Pattern: "Learning Module X:" or "Module X:"
    module_match = re.search(r'(?:Learning\s+)?Module\s*(\d+)', search_text, re.IGNORECASE)
    if module_match:
        mod_num = int(module_match.group(1))
        if 1 <= mod_num <= 11:
            return mod_num

    # Try to match by topic name
    search_lower = search_text.lower()
    if 'rate' in search_lower and 'return' in search_lower and 'portfolio' not in search_lower:
        return 1
    elif 'time value' in search_lower:
        return 2
    elif 'statistical measure' in search_lower:
        return 3
    elif 'probability' in search_lower or 'conditional expectation' in search_lower:
        return 4
    elif 'portfolio' in search_lower and 'math' in search_lower:
        return 5
    elif 'simulation' in search_lower:
        return 6
    elif 'estimation' in search_lower or 'inference' in search_lower:
        return 7
    elif 'hypothesis' in search_lower:
        return 8
    elif 'parametric' in search_lower or 'independence' in search_lower:
        return 9
    elif 'regression' in search_lower:
        return 10
    elif 'big data' in search_lower:
        return 11

    return 1  # Default


def parse_question(q_text, book_id=1):
    """Parse a single question from text."""

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
    # Pattern: lines that start with A., B., C. followed by value (not "is incorrect")
    options = {}

    # Find the options block - typically appears as:
    # A. value
    # B. value
    # C. value
    # Look for this pattern specifically

    # Try to find A. B. C. in sequence
    options_block_pattern = r'(?:^|\n)\s*A\.\s*([^\n]+)\s*\n\s*B\.\s*([^\n]+)\s*\n\s*C\.\s*([^\n]+)'
    options_match = re.search(options_block_pattern, q_text)

    if options_match:
        opt_a = options_match.group(1).strip()
        opt_b = options_match.group(2).strip()
        opt_c = options_match.group(3).strip()

        # Filter out if any option contains "is incorrect" or is too long (explanation)
        if 'incorrect' not in opt_a.lower() and len(opt_a) < 200:
            options['A'] = opt_a
        if 'incorrect' not in opt_b.lower() and len(opt_b) < 200:
            options['B'] = opt_b
        if 'incorrect' not in opt_c.lower() and len(opt_c) < 200:
            options['C'] = opt_c

    # If still missing options, try another pattern
    if len(options) < 3:
        # Look for pattern like "$XXX" or "XX%" after A. B. C.
        for letter in ['A', 'B', 'C']:
            if letter not in options:
                # Pattern: X. followed by currency/percentage/number
                pattern = rf'(?:^|\n)\s*{letter}\.\s*([$¥€£]?\s*[\d,]+\.?\d*%?(?:\s*(?:million|billion|to|or|and)\s*[$¥€£]?\s*[\d,]+\.?\d*%?)*)'
                match = re.search(pattern, q_text, re.IGNORECASE)
                if match:
                    val = match.group(1).strip()
                    if val and len(val) < 100:
                        options[letter] = val

    # If still missing, try word-based options
    if len(options) < 3:
        for letter in ['A', 'B', 'C']:
            if letter not in options:
                # Short text options (< 50 chars, not containing 'incorrect')
                pattern = rf'(?:^|\n)\s*{letter}\.\s*([A-Za-z][^.\n]{{1,50}}?)(?:\n|$)'
                match = re.search(pattern, q_text)
                if match:
                    val = match.group(1).strip()
                    if 'incorrect' not in val.lower():
                        options[letter] = val

    # Skip if we don't have at least A and correct answer option
    if correct_answer not in options or len(options) < 2:
        return None

    # Extract explanation (text after "The correct answer is X" until first "X is incorrect")
    explanation = ""
    exp_start = correct_match.end()
    incorrect_match = re.search(r'[ABC]\s+is incorrect', q_text[exp_start:], re.IGNORECASE)

    if incorrect_match:
        explanation = q_text[exp_start:exp_start + incorrect_match.start()].strip()
    else:
        # Find until options block
        if options_match:
            explanation = q_text[exp_start:options_match.start()].strip()

    # Clean explanation
    explanation = re.sub(r'\n+', ' ', explanation)
    explanation = re.sub(r'\s+', ' ', explanation).strip()

    # Extract wrong explanations
    explanation_wrong = {}
    for letter in ['A', 'B', 'C']:
        if letter != correct_answer:
            # Pattern: "X is incorrect. reason" up to next "X is incorrect" or options or ©
            wrong_pattern = rf'{letter}\s+is incorrect\.?\s*(.*?)(?=[ABC]\s+is incorrect|\n\s*A\.|\n\s*©|\Z)'
            wrong_match = re.search(wrong_pattern, q_text, re.DOTALL | re.IGNORECASE)
            if wrong_match:
                wrong_exp = wrong_match.group(1).strip()
                wrong_exp = re.sub(r'\n+', ' ', wrong_exp)
                wrong_exp = re.sub(r'\s+', ' ', wrong_exp).strip()
                # Remove options if accidentally captured
                wrong_exp = re.sub(r'\s*[ABC]\.\s*[$¥€£]?[\d,\.]+%?\s*$', '', wrong_exp)
                if wrong_exp and len(wrong_exp) > 5:
                    explanation_wrong[letter] = wrong_exp

    # Extract LOS reference
    los_match = re.search(r'(CFA Level[^©]+?LOS[^©\n]+)', q_text, re.IGNORECASE | re.DOTALL)
    los_text = ""
    if los_match:
        los_text = los_match.group(1).strip()
        los_text = re.sub(r'\n+', ' ', los_text)
        los_text = re.sub(r'\s+', ' ', los_text).strip()

    # Determine module from LOS
    module_id = extract_module_from_los(los_text, q_text)

    # Check for formula
    has_formula = bool(re.search(r'[=×÷±∑∏√∫]|FV\s*=|PV\s*=|NPV|IRR|\^|σ|μ', question_text + explanation))

    return {
        "question_id": f"QM-{module_id}-{q_num.zfill(3)}",
        "question_number": int(q_num),
        "question_text": question_text,
        "question_text_formula": None,
        "has_table": bool(re.search(r'Year\s+Return|\d{4}\s+\d+', q_text)),
        "has_image": False,
        "image_path": None,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation[:2000] if explanation else "",  # Limit length
        "explanation_wrong": explanation_wrong,
        "calculator_steps": extract_calculator_steps(q_text),
        "difficulty": "medium",
        "los_reference": los_text if los_text else None,
        "module_id": module_id
    }


def extract_calculator_steps(content):
    """Extract calculator steps if present."""
    if re.search(r'BA II|calculator|PV=|FV=|I/Y=|PMT=|CPT', content, re.IGNORECASE):
        calc_match = re.search(r'((?:PV|FV|I/Y|N|PMT)\s*=\s*[^;]+(?:;\s*(?:PV|FV|I/Y|N|PMT|CPT)\s*[=>\s]*[^;]+)*)', content)
        if calc_match:
            return [calc_match.group(1).strip()]
    return None


def parse_all_questions(text_content):
    """Parse all questions from the text file."""

    # Split by Q.XXX pattern
    question_pattern = r'(Q\.\d+\s+.*?)(?=Q\.\d+\s+|\Z)'
    question_blocks = re.findall(question_pattern, text_content, re.DOTALL)

    print(f"Found {len(question_blocks)} question blocks")

    questions = []
    failed = 0
    for i, block in enumerate(question_blocks):
        q = parse_question(block)
        if q and len(q['options']) >= 2:
            questions.append(q)
        else:
            failed += 1

    print(f"Successfully parsed {len(questions)} questions, failed: {failed}")
    return questions


def group_by_module(questions):
    """Group questions by module."""
    modules_dict = {}

    for q in questions:
        mod_id = q.get('module_id', 1)
        if mod_id not in modules_dict:
            modules_dict[mod_id] = []
        q_copy = {k: v for k, v in q.items() if k != 'module_id'}
        modules_dict[mod_id].append(q_copy)

    modules_list = []
    for mod_id in sorted(modules_dict.keys()):
        mod_info = MODULES.get(mod_id, {"name": f"Module {mod_id}", "name_ru": f"Модуль {mod_id}"})
        modules_list.append({
            "module_id": mod_id,
            "module_name": mod_info["name"],
            "module_name_ru": mod_info["name_ru"],
            "questions": sorted(modules_dict[mod_id], key=lambda x: x.get('question_number', 0))
        })

    return modules_list


def main():
    input_path = Path("/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests/CH-1-Quantitative_Methods-Answers.txt")
    output_path = Path("/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book1.json")

    print(f"Reading {input_path}")
    text_content = input_path.read_text(encoding='utf-8')

    questions = parse_all_questions(text_content)
    modules = group_by_module(questions)

    output = {
        "book_id": 1,
        "book_name": "Quantitative Methods",
        "book_name_ru": "Количественные методы",
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
