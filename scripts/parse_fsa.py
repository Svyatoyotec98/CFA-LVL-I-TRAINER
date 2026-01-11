#!/usr/bin/env python3
"""Parser for CFA Financial Statement Analysis PDF (Book 4)"""

import re
import json

MODULES = {
    1: {"name": "Introduction to Financial Statement Analysis", "name_ru": "Введение в анализ финансовой отчётности"},
    2: {"name": "Analyzing Income Statements", "name_ru": "Анализ отчёта о прибылях и убытках"},
    3: {"name": "Analyzing Balance Sheet", "name_ru": "Анализ баланса"},
    4: {"name": "Analyzing Statements of Cash Flows 1", "name_ru": "Анализ отчёта о движении денежных средств 1"},
    5: {"name": "Analyzing Statements of Cash Flows 2", "name_ru": "Анализ отчёта о движении денежных средств 2"},
    6: {"name": "Analysis of Inventories", "name_ru": "Анализ запасов"},
    7: {"name": "Analysis of Long Term Assets", "name_ru": "Анализ долгосрочных активов"},
    8: {"name": "Topics in Long-Term Liabilities and Equity", "name_ru": "Долгосрочные обязательства и капитал"},
    9: {"name": "Analysis of Income Taxes", "name_ru": "Анализ налога на прибыль"},
    10: {"name": "Financial Reporting Quality", "name_ru": "Качество финансовой отчётности"},
    11: {"name": "Financial Analysis Techniques", "name_ru": "Методы финансового анализа"},
    12: {"name": "Introduction to Financial Statement Modeling", "name_ru": "Введение в финансовое моделирование"},
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
                q['question_id'] = f"FSA-{mid}-{idx:03d}"
            learning_modules.append({
                "module_id": mid,
                "module_name": MODULES[mid]["name"],
                "module_name_ru": MODULES[mid]["name_ru"],
                "questions": modules_data[mid]
            })

    output = {
        "book_id": 4,
        "book_name": "Financial Statement Analysis",
        "book_name_ru": "Анализ финансовой отчётности",
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
        "question_id": f"FSA-0-{q_num}",
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

    if len(options) < 3:
        abc_pattern = r'A\.\s*([^\n]+)\nB\.\s*([^\n]+)\nC\.\s*([^\n]+)'
        match = re.search(abc_pattern, content)
        if match:
            a_text, b_text, c_text = match.groups()
            if len(a_text) < 150 and len(b_text) < 150 and len(c_text) < 150:
                options = {'A': clean_text(a_text), 'B': clean_text(b_text), 'C': clean_text(c_text)}

    if len(options) < 3:
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('©') or len(line) > 150:
                continue
            opt_match = re.match(r'^([ABC])\.\s*(.+)$', line)
            if opt_match:
                letter, text = opt_match.groups()
                if letter not in options and len(text) < 150 and 'incorrect' not in text.lower():
                    options[letter] = clean_text(text)

    return options


def detect_module(content):
    module_match = re.search(r'Learning Module (\d+)', content)
    if module_match:
        return int(module_match.group(1))

    content_lower = content.lower()
    if any(kw in content_lower for kw in ['md&a', 'annual report', 'audit', 'footnote', 'sec filing']):
        return 1
    elif any(kw in content_lower for kw in ['income statement', 'revenue recognition', 'gross profit', 'operating income', 'eps']):
        return 2
    elif any(kw in content_lower for kw in ['balance sheet', 'current asset', 'current liabilit', 'working capital']):
        return 3
    elif any(kw in content_lower for kw in ['cash flow', 'cfo', 'cfi', 'cff', 'operating activities']):
        return 4
    elif any(kw in content_lower for kw in ['free cash flow', 'fcf', 'fcff', 'fcfe']):
        return 5
    elif any(kw in content_lower for kw in ['inventory', 'fifo', 'lifo', 'weighted average cost']):
        return 6
    elif any(kw in content_lower for kw in ['depreciation', 'amortization', 'impairment', 'ppe', 'intangible']):
        return 7
    elif any(kw in content_lower for kw in ['bond', 'lease', 'pension', 'debt', 'equity']):
        return 8
    elif any(kw in content_lower for kw in ['deferred tax', 'tax expense', 'valuation allowance', 'dta', 'dtl']):
        return 9
    elif any(kw in content_lower for kw in ['earnings quality', 'manipulation', 'fraud', 'aggressive accounting']):
        return 10
    elif any(kw in content_lower for kw in ['ratio', 'roe', 'roa', 'dupont', 'liquidity ratio']):
        return 11
    elif any(kw in content_lower for kw in ['forecasting', 'modeling', 'projection']):
        return 12
    return 1


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'©\s*\d{4}[-–]\d{4}\s*AnalystPrep\.?', '', text)
    text = re.sub(r'\n\d+\n', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


if __name__ == "__main__":
    input_file = "/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests/book4_fsa.txt"
    output_file = "/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book4.json"

    result = parse_pdf(input_file, output_file)
    print(f"Parsed {result['total_questions']} questions into {len(result['learning_modules'])} modules")
    for module in result['learning_modules']:
        print(f"  Module {module['module_id']}: {module['module_name']} - {len(module['questions'])} questions")
