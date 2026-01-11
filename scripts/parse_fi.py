#!/usr/bin/env python3
"""Parser for CFA Fixed Income PDF (Book 6)"""

import re, json

MODULES = {
    1: {"name": "Fixed Income Instrument Features", "name_ru": "Характеристики инструментов с фиксированным доходом"},
    2: {"name": "Fixed Income Cash Flows and Types", "name_ru": "Денежные потоки и типы облигаций"},
    3: {"name": "Fixed Income Issuance and Trading", "name_ru": "Выпуск и торговля облигациями"},
    4: {"name": "Fixed Income Market for Corporate Issuers", "name_ru": "Рынок корпоративных облигаций"},
    5: {"name": "Fixed Income Market for Government Issuers", "name_ru": "Рынок государственных облигаций"},
    6: {"name": "Fixed Income Bond Valuations: Prices and Yields", "name_ru": "Оценка облигаций: цены и доходности"},
    7: {"name": "Yield and Yield Spread Measures for Fixed Rate Bonds", "name_ru": "Показатели доходности облигаций"},
    8: {"name": "Yield Measures for Floating Rate Instruments", "name_ru": "Доходность плавающих инструментов"},
    9: {"name": "The Term Structure of Interest Rates", "name_ru": "Временная структура процентных ставок"},
    10: {"name": "Interest Rate Risk and Return", "name_ru": "Процентный риск и доходность"},
    11: {"name": "Yield Based Bond Duration Measures", "name_ru": "Дюрация облигаций"},
    12: {"name": "Yield Based Bond Convexity", "name_ru": "Выпуклость облигаций"},
    13: {"name": "Curve Based Fixed Income Risk Measures", "name_ru": "Кривые риска облигаций"},
    14: {"name": "Credit Risk", "name_ru": "Кредитный риск"},
    15: {"name": "Credit Analysis for Government Issuers", "name_ru": "Кредитный анализ государств"},
}

def parse_pdf(text_file_path, output_path):
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    parts = re.split(r'Q\.(\d+)\s+', text)
    questions = []
    for i in range(1, len(parts) - 1, 2):
        q = parse_single_question(parts[i], parts[i + 1] if i + 1 < len(parts) else "")
        if q:
            q['module_id'] = detect_module(parts[i + 1])
            questions.append(q)

    modules_data = {}
    for q in questions:
        mid = q.pop('module_id', 1)
        modules_data.setdefault(mid, []).append(q)

    learning_modules = []
    for mid in sorted(modules_data.keys()):
        if mid in MODULES:
            for idx, q in enumerate(modules_data[mid], 1):
                q['question_id'] = f"FI-{mid}-{idx:03d}"
            learning_modules.append({"module_id": mid, "module_name": MODULES[mid]["name"],
                "module_name_ru": MODULES[mid]["name_ru"], "questions": modules_data[mid]})

    output = {"book_id": 6, "book_name": "Fixed Income", "book_name_ru": "Облигации",
        "total_questions": len(questions), "learning_modules": learning_modules}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    return output

def parse_single_question(q_num, content):
    if len(content) < 100: return None
    qm = re.search(r'^(.*?)(?=The correct answer is [ABC])', content, re.DOTALL)
    if not qm: return None
    cm = re.search(r'The correct answer is ([ABC])', content)
    if not cm: return None
    em = re.search(r'The correct answer is [ABC]\.\s*(.*?)(?=[ABC] is incorrect\.|A\.\s+[A-Z]|$)', content, re.DOTALL)
    ew = {}
    for l in ['A', 'B', 'C']:
        if l != cm.group(1):
            m = re.search(rf'{l} is incorrect\.\s*(.*?)(?=[ABC] is incorrect\.|CFA Level|A\.\s+[A-Z]|$)', content, re.DOTALL)
            if m: ew[l] = clean_text(m.group(1))
    return {"question_id": f"FI-0-{q_num}", "question_text": clean_text(qm.group(1)),
        "question_text_formula": None, "has_table": False, "has_image": False, "image_path": None,
        "options": extract_options(content), "correct_answer": cm.group(1),
        "explanation": clean_text(em.group(1)) if em else "", "explanation_wrong": ew,
        "calculator_steps": None, "difficulty": "medium", "los_reference": None}

def extract_options(content):
    opts = {}
    m = re.search(r'(A\.[^\n]+\n(?:B\.[^\n]+\n)?(?:C\.[^\n]+)?)(?:\s*©|\s*$)', content)
    if m:
        for l in ['A','B','C']:
            x = re.search(rf'^{l}\.\s*(.+?)$', m.group(1), re.MULTILINE)
            if x and len(x.group(1)) < 150: opts[l] = clean_text(x.group(1))
    if len(opts) < 3:
        m = re.search(r'A\.\s*([^\n]+)\nB\.\s*([^\n]+)\nC\.\s*([^\n]+)', content)
        if m and all(len(g) < 150 for g in m.groups()):
            opts = {'A': clean_text(m.group(1)), 'B': clean_text(m.group(2)), 'C': clean_text(m.group(3))}
    if len(opts) < 3:
        for line in content.split('\n'):
            x = re.match(r'^([ABC])\.\s*(.+)$', line.strip())
            if x and len(x.group(2)) < 150 and 'incorrect' not in x.group(2).lower():
                opts.setdefault(x.group(1), clean_text(x.group(2)))
    return opts

def detect_module(content):
    m = re.search(r'Learning Module (\d+)', content)
    if m: return int(m.group(1))
    c = content.lower()
    if 'coupon' in c or 'maturity' in c or 'par value' in c: return 1
    elif 'amortizing' in c or 'bullet' in c: return 2
    elif 'primary market' in c or 'secondary market' in c: return 3
    elif 'corporate bond' in c: return 4
    elif 'government bond' in c or 'treasury' in c: return 5
    elif 'ytm' in c or 'yield to maturity' in c or 'bond price' in c: return 6
    elif 'spread' in c and 'yield' in c: return 7
    elif 'floating' in c or 'frn' in c: return 8
    elif 'spot rate' in c or 'forward rate' in c or 'term structure' in c: return 9
    elif 'interest rate risk' in c: return 10
    elif 'duration' in c: return 11
    elif 'convexity' in c: return 12
    elif 'key rate' in c: return 13
    elif 'credit risk' in c or 'default' in c: return 14
    elif 'sovereign' in c: return 15
    return 1

def clean_text(t):
    if not t: return ""
    t = re.sub(r'©\s*\d{4}[-–]\d{4}\s*AnalystPrep\.?', '', t)
    return re.sub(r'\s+', ' ', t).strip()

if __name__ == "__main__":
    r = parse_pdf("/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests/book6_fi.txt",
                  "/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book6.json")
    print(f"Parsed {r['total_questions']} questions into {len(r['learning_modules'])} modules")
    for m in r['learning_modules']:
        print(f"  Module {m['module_id']}: {m['module_name']} - {len(m['questions'])} q")
