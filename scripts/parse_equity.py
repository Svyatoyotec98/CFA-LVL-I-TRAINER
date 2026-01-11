#!/usr/bin/env python3
"""Parser for CFA Equity PDF (Book 5)"""

import re
import json

MODULES = {
    1: {"name": "Market Organization & Structure", "name_ru": "Организация и структура рынка"},
    2: {"name": "Security Market Indices", "name_ru": "Рыночные индексы"},
    3: {"name": "Market Efficiency", "name_ru": "Эффективность рынка"},
    4: {"name": "Overview of Equity Securities", "name_ru": "Обзор долевых ценных бумаг"},
    5: {"name": "Company Analysis: Past and Present", "name_ru": "Анализ компании: прошлое и настоящее"},
    6: {"name": "Industry and Competitive Analysis", "name_ru": "Отраслевой и конкурентный анализ"},
    7: {"name": "Company Analysis: Forecasting", "name_ru": "Анализ компании: прогнозирование"},
    8: {"name": "Equity Valuation: Concepts & Basic Tools", "name_ru": "Оценка акций: концепции и инструменты"},
}

def parse_pdf(text_file_path, output_path):
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    parts = re.split(r'Q\.(\d+)\s+', text)
    questions = []

    for i in range(1, len(parts) - 1, 2):
        q_num, q_content = parts[i], parts[i + 1] if i + 1 < len(parts) else ""
        question = parse_single_question(q_num, q_content)
        if question:
            question['module_id'] = detect_module(q_content)
            questions.append(question)

    modules_data = {}
    for q in questions:
        mid = q.pop('module_id', 1)
        modules_data.setdefault(mid, []).append(q)

    learning_modules = []
    for mid in sorted(modules_data.keys()):
        if mid in MODULES:
            for idx, q in enumerate(modules_data[mid], 1):
                q['question_id'] = f"EQ-{mid}-{idx:03d}"
            learning_modules.append({
                "module_id": mid, "module_name": MODULES[mid]["name"],
                "module_name_ru": MODULES[mid]["name_ru"], "questions": modules_data[mid]
            })

    output = {
        "book_id": 5, "book_name": "Equity Investments",
        "book_name_ru": "Инвестиции в акции",
        "total_questions": len(questions), "learning_modules": learning_modules
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

    explanation_match = re.search(r'The correct answer is [ABC]\.\s*(.*?)(?=[ABC] is incorrect\.|A\.\s+[A-Z]|$)', content, re.DOTALL)
    explanation = clean_text(explanation_match.group(1)) if explanation_match else ""

    explanation_wrong = {}
    for letter in ['A', 'B', 'C']:
        if letter != correct_answer:
            match = re.search(rf'{letter} is incorrect\.\s*(.*?)(?=[ABC] is incorrect\.|CFA Level|A\.\s+[A-Z]|$)', content, re.DOTALL)
            if match:
                explanation_wrong[letter] = clean_text(match.group(1))

    return {
        "question_id": f"EQ-0-{q_num}", "question_text": question_text,
        "question_text_formula": None, "has_table": False, "has_image": False, "image_path": None,
        "options": extract_options(content), "correct_answer": correct_answer,
        "explanation": explanation, "explanation_wrong": explanation_wrong,
        "calculator_steps": None, "difficulty": "medium", "los_reference": None
    }


def extract_options(content):
    options = {}
    # Method 1: End of content
    match = re.search(r'(A\.[^\n]+\n(?:B\.[^\n]+\n)?(?:C\.[^\n]+)?)(?:\s*©|\s*$)', content)
    if match:
        for letter in ['A', 'B', 'C']:
            m = re.search(rf'^{letter}\.\s*(.+?)$', match.group(1), re.MULTILINE)
            if m and len(m.group(1)) < 150:
                options[letter] = clean_text(m.group(1))

    # Method 2: Consecutive lines
    if len(options) < 3:
        match = re.search(r'A\.\s*([^\n]+)\nB\.\s*([^\n]+)\nC\.\s*([^\n]+)', content)
        if match and all(len(g) < 150 for g in match.groups()):
            options = {'A': clean_text(match.group(1)), 'B': clean_text(match.group(2)), 'C': clean_text(match.group(3))}

    # Method 3: Scan lines
    if len(options) < 3:
        for line in content.split('\n'):
            m = re.match(r'^([ABC])\.\s*(.+)$', line.strip())
            if m and len(m.group(2)) < 150 and 'incorrect' not in m.group(2).lower():
                options.setdefault(m.group(1), clean_text(m.group(2)))
    return options


def detect_module(content):
    match = re.search(r'Learning Module (\d+)', content)
    if match:
        return int(match.group(1))

    c = content.lower()
    if any(k in c for k in ['margin', 'broker', 'order type', 'market order', 'limit order']):
        return 1
    elif any(k in c for k in ['index', 'price-weighted', 'value-weighted', 'market cap']):
        return 2
    elif any(k in c for k in ['efficient market', 'emh', 'anomal', 'random walk']):
        return 3
    elif any(k in c for k in ['common stock', 'preferred stock', 'adr', 'gdr']):
        return 4
    elif any(k in c for k in ['financial statement', 'ratio analysis', 'roe', 'dupont']):
        return 5
    elif any(k in c for k in ['industry', 'porter', 'competitive', 'five forces']):
        return 6
    elif any(k in c for k in ['forecast', 'growth rate', 'earnings estimate']):
        return 7
    elif any(k in c for k in ['ddm', 'dividend discount', 'p/e', 'valuation', 'intrinsic value']):
        return 8
    return 1


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'©\s*\d{4}[-–]\d{4}\s*AnalystPrep\.?', '', text)
    text = re.sub(r'\n\d+\n', '\n', text)
    return re.sub(r'\s+', ' ', text).strip()


if __name__ == "__main__":
    result = parse_pdf(
        "/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests/book5_equity.txt",
        "/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book5.json"
    )
    print(f"Parsed {result['total_questions']} questions into {len(result['learning_modules'])} modules")
    for m in result['learning_modules']:
        print(f"  Module {m['module_id']}: {m['module_name']} - {len(m['questions'])} questions")
