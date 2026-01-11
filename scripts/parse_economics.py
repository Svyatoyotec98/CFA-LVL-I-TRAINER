#!/usr/bin/env python3
"""
Parser for CFA Economics PDF (Book 2)
Converts AnalystPrep PDF format to JSON
"""

import re
import json

# Module mapping from PDF
MODULES = {
    1: {"name": "Firm & Market Structures", "name_ru": "Структуры фирм и рынков"},
    2: {"name": "Understanding Business Cycles", "name_ru": "Понимание бизнес-циклов"},
    3: {"name": "Fiscal Policy", "name_ru": "Фискальная политика"},
    4: {"name": "Monetary Policy", "name_ru": "Монетарная политика"},
    5: {"name": "Introduction to Geopolitics", "name_ru": "Введение в геополитику"},
    6: {"name": "International Trade", "name_ru": "Международная торговля"},
    7: {"name": "Capital Flows and the FX Market", "name_ru": "Потоки капитала и валютный рынок"},
    8: {"name": "Exchange Rate Calculations", "name_ru": "Расчёты обменных курсов"},
}

def parse_economics_pdf(text_file_path, output_path):
    """Parse the extracted text and create JSON."""

    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split by question pattern Q.XXXX
    question_pattern = r'Q\.(\d+)\s+'
    parts = re.split(question_pattern, text)

    questions = []
    current_module = 1

    # parts[0] is before first Q., then alternating: number, content, number, content...
    for i in range(1, len(parts) - 1, 2):
        q_num = parts[i]
        q_content = parts[i + 1] if i + 1 < len(parts) else ""

        question = parse_single_question(q_num, q_content)
        if question:
            # Detect module from LOS reference
            module_id = detect_module(question.get('los_reference', ''), q_content)
            question['module_id'] = module_id
            questions.append(question)

    # Group questions by module
    modules_data = {}
    for q in questions:
        mid = q.pop('module_id', 1)
        if mid not in modules_data:
            modules_data[mid] = []
        modules_data[mid].append(q)

    # Build output structure
    learning_modules = []
    for mid in sorted(modules_data.keys()):
        if mid in MODULES:
            module_info = MODULES[mid]
            # Renumber questions within module
            for idx, q in enumerate(modules_data[mid], 1):
                q['question_id'] = f"EC-{mid}-{idx:03d}"

            learning_modules.append({
                "module_id": mid,
                "module_name": module_info["name"],
                "module_name_ru": module_info["name_ru"],
                "questions": modules_data[mid]
            })

    output = {
        "book_id": 2,
        "book_name": "Economics",
        "book_name_ru": "Экономика",
        "total_questions": len(questions),
        "learning_modules": learning_modules
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output


def parse_single_question(q_num, content):
    """Parse a single question from content."""

    # Skip if too short
    if len(content) < 100:
        return None

    # Extract question text (before "The correct answer is")
    question_match = re.search(r'^(.*?)(?=The correct answer is [ABC])', content, re.DOTALL)
    if not question_match:
        return None

    question_text = clean_text(question_match.group(1))

    # Extract correct answer
    correct_match = re.search(r'The correct answer is ([ABC])', content)
    if not correct_match:
        return None
    correct_answer = correct_match.group(1)

    # Extract main explanation (after "The correct answer is X." until next incorrect explanation or options)
    explanation_match = re.search(
        r'The correct answer is [ABC]\.\s*(.*?)(?=[ABC] is incorrect\.|A\.\s+[A-Z]|$)',
        content, re.DOTALL
    )
    explanation = clean_text(explanation_match.group(1)) if explanation_match else ""

    # Extract wrong explanations
    explanation_wrong = {}
    for letter in ['A', 'B', 'C']:
        if letter != correct_answer:
            pattern = rf'{letter} is incorrect\.\s*(.*?)(?=[ABC] is incorrect\.|CFA Level|A\.\s+[A-Z]|$)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                explanation_wrong[letter] = clean_text(match.group(1))

    # Extract options A, B, C (they appear at the END, before copyright)
    options = extract_options_alternative(content)

    # Extract LOS reference
    los_match = re.search(r'LOS\s+[\d\.]*[a-z]?:?\s*(.*?)(?:\n|$)', content)
    los_reference = los_match.group(0).strip() if los_match else None

    # Detect if has formula (simple heuristic)
    has_formula = bool(re.search(r'[=×÷∑∏√∫]|[A-Z]+\s*[=<>]|\$.*\$', question_text))

    return {
        "question_id": f"EC-0-{q_num}",  # Will be renumbered
        "question_text": question_text,
        "question_text_formula": None,
        "has_table": bool(re.search(r'\t.*\t|\|.*\|', question_text)),
        "has_image": False,
        "image_path": None,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "explanation_wrong": explanation_wrong,
        "calculator_steps": None,
        "difficulty": "medium",
        "los_reference": los_reference
    }


def extract_options_alternative(content):
    """Extract options from the END of content (before copyright)."""
    options = {}

    # Find the section with A. B. C. at the very end (before copyright)
    # Options are typically the last 3 lines with A. B. C. pattern
    end_section = re.search(r'(A\.[^\n]+\n(?:B\.[^\n]+\n)?(?:C\.[^\n]+)?)(?:\s*©|\s*$)', content, re.DOTALL)

    if end_section:
        options_text = end_section.group(1)
        for letter in ['A', 'B', 'C']:
            pattern = rf'^{letter}\.\s*(.+?)$'
            match = re.search(pattern, options_text, re.MULTILINE)
            if match:
                options[letter] = clean_text(match.group(1))

    # If still not found, try looking for short lines at end
    if len(options) < 3:
        lines = content.split('\n')
        for line in reversed(lines[-20:]):  # Check last 20 lines
            line = line.strip()
            if not line or line.startswith('©') or len(line) > 200:
                continue
            opt_match = re.match(r'^([ABC])\.\s*(.+)$', line)
            if opt_match:
                letter, text = opt_match.groups()
                if letter not in options and len(text) < 150:  # Options are usually short
                    options[letter] = clean_text(text)

    return options


def detect_module(los_ref, content):
    """Detect module number from LOS reference or content."""

    # Check for explicit module mention
    module_match = re.search(r'Learning Module (\d+)', content)
    if module_match:
        return int(module_match.group(1))

    # Check content for module keywords
    content_lower = content.lower()

    if any(kw in content_lower for kw in ['firm', 'market structure', 'monopol', 'oligopol', 'competition']):
        return 1
    elif any(kw in content_lower for kw in ['business cycle', 'recession', 'expansion', 'gdp growth']):
        return 2
    elif any(kw in content_lower for kw in ['fiscal policy', 'government spending', 'tax', 'budget']):
        return 3
    elif any(kw in content_lower for kw in ['monetary policy', 'central bank', 'interest rate', 'money supply']):
        return 4
    elif any(kw in content_lower for kw in ['geopolit', 'political risk']):
        return 5
    elif any(kw in content_lower for kw in ['international trade', 'tariff', 'import', 'export', 'trade barrier']):
        return 6
    elif any(kw in content_lower for kw in ['capital flow', 'fx market', 'foreign exchange', 'balance of payment']):
        return 7
    elif any(kw in content_lower for kw in ['exchange rate', 'currency', 'spot rate', 'forward rate']):
        return 8

    return 1  # Default


def clean_text(text):
    """Clean extracted text."""
    if not text:
        return ""

    # Remove page numbers and copyright
    text = re.sub(r'©\s*\d{4}[-–]\d{4}\s*AnalystPrep\.?', '', text)
    text = re.sub(r'\n\d+\n', '\n', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


if __name__ == "__main__":
    input_file = "/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests/book2_economics.txt"
    output_file = "/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book2.json"

    result = parse_economics_pdf(input_file, output_file)
    print(f"Parsed {result['total_questions']} questions into {len(result['learning_modules'])} modules")

    for module in result['learning_modules']:
        print(f"  Module {module['module_id']}: {module['module_name']} - {len(module['questions'])} questions")
