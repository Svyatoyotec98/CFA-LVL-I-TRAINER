#!/usr/bin/env python3
"""
Parser for CFA Corporate Issuers PDF (Book 3)
"""

import re
import json

MODULES = {
    1: {"name": "Organization Forms, Corporate Issuer Features and Ownership", "name_ru": "Формы организаций и корпоративные эмитенты"},
    2: {"name": "Investors and other Stakeholders", "name_ru": "Инвесторы и другие заинтересованные стороны"},
    3: {"name": "Corporate Governance: Conflicts, Mechanisms, Risks, and Benefits", "name_ru": "Корпоративное управление"},
    4: {"name": "Working Capital & Liquidity", "name_ru": "Оборотный капитал и ликвидность"},
    5: {"name": "Capital Investments and Capital Allocation", "name_ru": "Капитальные инвестиции и распределение капитала"},
    6: {"name": "Capital Structure", "name_ru": "Структура капитала"},
    7: {"name": "Business Models", "name_ru": "Бизнес-модели"},
}

def parse_pdf(text_file_path, output_path):
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    question_pattern = r'Q\.(\d+)\s+'
    parts = re.split(question_pattern, text)

    questions = []
    for i in range(1, len(parts) - 1, 2):
        q_num = parts[i]
        q_content = parts[i + 1] if i + 1 < len(parts) else ""
        question = parse_single_question(q_num, q_content)
        if question:
            module_id = detect_module(q_content)
            question['module_id'] = module_id
            questions.append(question)

    modules_data = {}
    for q in questions:
        mid = q.pop('module_id', 1)
        if mid not in modules_data:
            modules_data[mid] = []
        modules_data[mid].append(q)

    learning_modules = []
    for mid in sorted(modules_data.keys()):
        if mid in MODULES:
            for idx, q in enumerate(modules_data[mid], 1):
                q['question_id'] = f"CI-{mid}-{idx:03d}"
            learning_modules.append({
                "module_id": mid,
                "module_name": MODULES[mid]["name"],
                "module_name_ru": MODULES[mid]["name_ru"],
                "questions": modules_data[mid]
            })

    output = {
        "book_id": 3,
        "book_name": "Corporate Issuers",
        "book_name_ru": "Корпоративные эмитенты",
        "total_questions": len(questions),
        "learning_modules": learning_modules
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output


def parse_single_question(q_num, content):
    if len(content) < 100:
        return None

    question_match = re.search(r'^(.*?)(?=The correct answer is [ABC])', content, re.DOTALL)
    if not question_match:
        return None
    question_text = clean_text(question_match.group(1))

    correct_match = re.search(r'The correct answer is ([ABC])', content)
    if not correct_match:
        return None
    correct_answer = correct_match.group(1)

    explanation_match = re.search(
        r'The correct answer is [ABC]\.\s*(.*?)(?=[ABC] is incorrect\.|A\.\s+[A-Z]|$)',
        content, re.DOTALL
    )
    explanation = clean_text(explanation_match.group(1)) if explanation_match else ""

    explanation_wrong = {}
    for letter in ['A', 'B', 'C']:
        if letter != correct_answer:
            pattern = rf'{letter} is incorrect\.\s*(.*?)(?=[ABC] is incorrect\.|CFA Level|A\.\s+[A-Z]|$)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                explanation_wrong[letter] = clean_text(match.group(1))

    options = extract_options(content)

    los_match = re.search(r'LOS\s*\(?[a-z]\)?:?\s*(.*?)(?:\n|$)', content)
    los_reference = los_match.group(0).strip() if los_match else None

    return {
        "question_id": f"CI-0-{q_num}",
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


def extract_options(content):
    options = {}

    # Method 1: Options at the END (before copyright)
    end_section = re.search(r'(A\.[^\n]+\n(?:B\.[^\n]+\n)?(?:C\.[^\n]+)?)(?:\s*©|\s*$)', content, re.DOTALL)
    if end_section:
        options_text = end_section.group(1)
        for letter in ['A', 'B', 'C']:
            pattern = rf'^{letter}\.\s*(.+?)$'
            match = re.search(pattern, options_text, re.MULTILINE)
            if match:
                opt_text = clean_text(match.group(1))
                if len(opt_text) < 150:
                    options[letter] = opt_text

    # Method 2: Look for consecutive A. B. C. lines ANYWHERE in content
    if len(options) < 3:
        # Find pattern: A. <text>\nB. <text>\nC. <text>
        abc_pattern = r'A\.\s*([^\n]+)\nB\.\s*([^\n]+)\nC\.\s*([^\n]+)'
        match = re.search(abc_pattern, content)
        if match:
            a_text, b_text, c_text = match.groups()
            if len(a_text) < 150 and len(b_text) < 150 and len(c_text) < 150:
                options = {
                    'A': clean_text(a_text),
                    'B': clean_text(b_text),
                    'C': clean_text(c_text)
                }

    # Method 3: Scan all lines for short A. B. C. patterns
    if len(options) < 3:
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('©') or len(line) > 150:
                continue
            opt_match = re.match(r'^([ABC])\.\s*(.+)$', line)
            if opt_match:
                letter, text = opt_match.groups()
                if letter not in options and len(text) < 150:
                    # Skip if it looks like explanation (contains "incorrect")
                    if 'incorrect' not in text.lower():
                        options[letter] = clean_text(text)

    return options


def detect_module(content):
    module_match = re.search(r'Learning Module (\d+)', content)
    if module_match:
        return int(module_match.group(1))

    content_lower = content.lower()
    if any(kw in content_lower for kw in ['sole trader', 'partnership', 'corporation', 'organizational form', 'limited liability']):
        return 1
    elif any(kw in content_lower for kw in ['stakeholder', 'shareholder', 'creditor', 'bondholder', 'investor']):
        return 2
    elif any(kw in content_lower for kw in ['governance', 'board of director', 'agency', 'conflict of interest']):
        return 3
    elif any(kw in content_lower for kw in ['working capital', 'liquidity', 'cash conversion', 'receivable', 'inventory', 'payable']):
        return 4
    elif any(kw in content_lower for kw in ['npv', 'irr', 'capital budget', 'capital allocation', 'project evaluation']):
        return 5
    elif any(kw in content_lower for kw in ['capital structure', 'debt', 'equity', 'leverage', 'wacc', 'cost of capital']):
        return 6
    elif any(kw in content_lower for kw in ['business model', 'value chain', 'network effect']):
        return 7
    return 1


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'©\s*\d{4}[-–]\d{4}\s*AnalystPrep\.?', '', text)
    text = re.sub(r'\n\d+\n', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


if __name__ == "__main__":
    input_file = "/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests/book3_corporate.txt"
    output_file = "/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book3.json"

    result = parse_pdf(input_file, output_file)
    print(f"Parsed {result['total_questions']} questions into {len(result['learning_modules'])} modules")
    for module in result['learning_modules']:
        print(f"  Module {module['module_id']}: {module['module_name']} - {len(module['questions'])} questions")
