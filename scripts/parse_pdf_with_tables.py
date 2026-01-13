#!/usr/bin/env python3
"""
Enhanced PDF parser for CFA Level 1 books.
Extracts questions WITH tables and formulas from PDF files.

Key improvements:
- Extracts tables from text patterns (Year/Return, Period/Value, etc.)
- Preserves formula text in explanation_formula field
- Generates proper calculator_steps in BA II Plus format

Usage:
    python parse_pdf_with_tables.py <book_id> <input_pdf> <output_json>

Example:
    python parse_pdf_with_tables.py 1 "CH-1-Quantitative_Methods-Answers.pdf" book1.json
"""

import re
import json
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Please install PyMuPDF: pip install pymupdf")
    sys.exit(1)


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
    # Add more books as needed...
}


def extract_table_from_block(block_text):
    """
    Extract table data from entire question block.
    Handles patterns like:
    - Year / Return (%) followed by year-value pairs
    - Period / Value patterns
    - Multi-column numeric data

    Returns: table_data dict or None
    """
    lines = block_text.split('\n')

    # Pattern 1: Look for "Year" header followed by data
    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Check for Year/Return header pattern
        if line_stripped.lower() == 'year':
            # Look for second header
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if 'return' in next_line.lower() or '%' in next_line:
                    headers = [line_stripped, next_line]
                    rows = []
                    idx = i + 2

                    # Collect rows (pairs of values)
                    while idx + 1 < len(lines):
                        row_key = lines[idx].strip()
                        row_val = lines[idx + 1].strip() if idx + 1 < len(lines) else ""

                        # Check if this looks like table data
                        if re.match(r'^\d{4}$', row_key):
                            if re.match(r'^-?\d+\.?\d*%?$', row_val):
                                rows.append([row_key, row_val])
                                idx += 2
                                continue

                        # Not table data anymore
                        break

                    if rows:
                        return {
                            "headers": headers,
                            "rows": rows
                        }

        # Pattern 2: Period/Time headers
        if line_stripped.lower() in ['period', 'time', 'quarter']:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if any(x in next_line.lower() for x in ['value', 'return', 'rate', 'amount', '%']):
                    headers = [line_stripped, next_line]
                    rows = []
                    idx = i + 2

                    while idx + 1 < len(lines):
                        row_key = lines[idx].strip()
                        row_val = lines[idx + 1].strip() if idx + 1 < len(lines) else ""

                        if re.match(r'^(Period|Q|Year|T)?\s*\d+$', row_key, re.I):
                            if re.match(r'^-?\$?[\d,\.]+%?$', row_val):
                                rows.append([row_key, row_val])
                                idx += 2
                                continue
                        break

                    if rows:
                        return {
                            "headers": headers,
                            "rows": rows
                        }

    # Pattern 3: Inline pattern in text (Year Return (%) 2011 13 2012 19...)
    inline_pattern = r'Year\s+Return\s*\(?%?\)?\s*((?:\d{4}\s+-?\d+\.?\d*\s*)+)'
    match = re.search(inline_pattern, block_text, re.I)
    if match:
        data_str = match.group(1)
        pairs = re.findall(r'(\d{4})\s+(-?\d+\.?\d*)', data_str)
        if pairs:
            return {
                "headers": ["Year", "Return (%)"],
                "rows": [[p[0], p[1]] for p in pairs]
            }

    return None


def extract_formula_from_text(text):
    """
    Extract mathematical formulas from text.
    Returns LaTeX-formatted formula string or None.
    """
    formulas = []

    # Pattern: Various formula types
    formula_patterns = [
        # HPR = (1 + r1) × (1 + r2) × ... - 1 = result
        r'(HPR\s*=\s*\(1\s*[+]\s*[\d\.]+\)\s*[×x\*]\s*.*?[=]\s*[\d\.]+\s*(?:or\s*[\d\.]+%)?)',
        # FV = PV × (1 + r)^n type formulas
        r'(FV\s*[=]\s*PV\s*[×x\*]\s*\([^)]+\)\s*[\^]?\s*\d*)',
        r'(PV\s*[=]\s*FV\s*/\s*\([^)]+\)\s*[\^]?\s*\d*)',
        # FV_N = PV[1 + rs/m]^(mN) = calculations
        r'(FV[_N]*\s*=\s*\$?[\d,]+\s*[\[\(][^=]+[\]\)]\s*[\^]?\s*\d*\s*=\s*\$?[\d,\.]+)',
        r'(NPV\s*[=][^©\n]{10,100})',
        r'(IRR\s*[=][^©\n]{10,100})',
        # General calculation pattern
        r'(\$[\d,]+\s*[×x\*]\s*[\d\.]+\s*[=]\s*\$[\d,\.]+)',
        r'([\d,]+\s*[×x\*]\s*\([^)]+\)\s*[=]\s*[\d,\.]+)',
    ]

    for pattern in formula_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if len(m) > 10:  # Filter out too short matches
                formulas.append(m)

    if formulas:
        # Take the longest/most complete formula
        result = max(formulas, key=len)
        # Clean and convert to LaTeX format
        result = result.replace('×', ' \\times ')
        result = result.replace('−', '-')
        result = re.sub(r'\s+', ' ', result).strip()
        return f"${result}$"

    return None


def extract_calculator_steps(text):
    """
    Extract and format calculator steps for BA II Plus.
    Converts raw text into structured step-by-step instructions.
    """
    steps = []

    # Look for TVM variable patterns
    tvm_vars = {
        'PV': 'Present Value',
        'FV': 'Future Value',
        'N': 'Number of periods',
        'I/Y': 'Interest rate per period',
        'PMT': 'Payment amount'
    }

    # Pattern: PV=-XXX; I/Y=X; N=X; CPT => FV
    tvm_pattern = r'(PV\s*=\s*-?[\d,\.]+).*?(I/Y\s*=\s*[\d\.\/]+).*?(N\s*=\s*[\d\.×x\*]+).*?(PMT\s*=\s*-?[\d,\.]+)?.*?(CPT\s*=>?\s*(FV|PV|PMT)?\s*=?\s*[\d,\.]*)?'
    match = re.search(tvm_pattern, text, re.I | re.DOTALL)

    if match:
        # Start with clearing TVM
        steps.append("[2ND] [CLR TVM] — очистить TVM worksheet")

        # Extract values
        if match.group(1):
            pv_val = re.search(r'=\s*(-?[\d,\.]+)', match.group(1))
            if pv_val:
                val = pv_val.group(1).replace(',', '')
                if val.startswith('-'):
                    steps.append(f"{val[1:]} [+/-] [PV] — ввести начальную сумму (отрицательная)")
                else:
                    steps.append(f"{val} [PV] — ввести начальную сумму")

        if match.group(2):
            iy_val = re.search(r'=\s*([\d\.\/]+)', match.group(2))
            if iy_val:
                val = iy_val.group(1)
                if '/' in val:
                    parts = val.split('/')
                    steps.append(f"{parts[0]} [÷] {parts[1]} [=] [I/Y] — ввести ставку ({parts[0]}%/{parts[1]})")
                else:
                    steps.append(f"{val} [I/Y] — ввести ставку процента")

        if match.group(3):
            n_val = re.search(r'=\s*([\d\.×x\*]+)', match.group(3))
            if n_val:
                val = n_val.group(1)
                if '×' in val or 'x' in val or '*' in val:
                    val = re.sub(r'[×x\*]', ' × ', val)
                    steps.append(f"{val} [=] [N] — ввести количество периодов")
                else:
                    steps.append(f"{val} [N] — ввести количество периодов")

        if match.group(4):
            pmt_val = re.search(r'=\s*(-?[\d,\.]+)', match.group(4))
            if pmt_val:
                val = pmt_val.group(1).replace(',', '')
                steps.append(f"{val} [PMT] — ввести периодический платёж")
        else:
            steps.append("0 [PMT] — нет периодических платежей")

        if match.group(5):
            result_match = re.search(r'(FV|PV|PMT)\s*=?\s*([\d,\.]+)?', match.group(5))
            if result_match:
                calc_var = result_match.group(1)
                result_val = result_match.group(2) if result_match.group(2) else ""
                steps.append(f"[CPT] [{calc_var}] — рассчитать {tvm_vars.get(calc_var, calc_var)}")
                if result_val:
                    steps.append(f"Результат: {result_val}")

    return steps if steps else None


def extract_module_from_text(text, book_id):
    """Extract module number from LOS or Learning Module reference."""
    module_match = re.search(r'(?:Learning\s+)?Module\s*(\d+)', text, re.IGNORECASE)
    if module_match:
        mod_num = int(module_match.group(1))
        max_modules = len(BOOK_CONFIGS.get(book_id, {}).get("modules", {}))
        if 1 <= mod_num <= max(max_modules, 11):
            return mod_num
    return 1


def parse_question_block(block_text, book_id):
    """Parse a single question block from PDF text."""
    config = BOOK_CONFIGS.get(book_id, {"prefix": f"B{book_id}", "modules": {}})
    prefix = config["prefix"]

    # Extract question number
    q_num_match = re.search(r'Q\.(\d+)', block_text)
    if not q_num_match:
        return None
    q_num = q_num_match.group(1)

    # Find "The correct answer is X"
    correct_match = re.search(r'The correct answer is\s*([ABC])\.?\s*', block_text, re.IGNORECASE)
    if not correct_match:
        return None
    correct_answer = correct_match.group(1).upper()

    # Extract question text (from Q.XX to "The correct answer")
    q_start = q_num_match.end()
    q_end = correct_match.start()

    # Extract table from ENTIRE block (it might be anywhere)
    table_data = extract_table_from_block(block_text)

    # Extract raw question text
    question_text = block_text[q_start:q_end].strip()

    # Clean question text
    question_text = re.sub(r'\n+', ' ', question_text)
    question_text = re.sub(r'\s+', ' ', question_text).strip()

    # Extract question continuation if table exists
    question_continuation = None
    if table_data:
        # Look for continuation pattern after table mention
        cont_patterns = [
            r"(The\s+(?:share's|stock's|portfolio's|investment's)?\s*(?:holding\s+period\s+)?return[^:]*?closest to:)",
            r"(is closest to:)",
            r"(What is[^?]+\?)",
            r"(Which[^?]+\?)",
        ]
        for pattern in cont_patterns:
            cont_match = re.search(pattern, question_text, re.I)
            if cont_match:
                question_continuation = cont_match.group(1).strip()
                break

    # Extract options
    options = {}
    options_pattern = r'(?:^|\n)\s*([ABC])\.\s*(.+?)(?=\n\s*[ABC]\.|\n\s*The correct|\Z)'

    # Look for options after the explanation typically
    for match in re.finditer(options_pattern, block_text, re.DOTALL):
        letter = match.group(1)
        value = match.group(2).strip()
        # Clean the value
        value = re.sub(r'\n+', ' ', value)
        value = value.split('.')[0] if '.' in value and len(value.split('.')[0]) < 50 else value
        value = value.strip()

        # Filter out explanation text
        if 'incorrect' not in value.lower() and len(value) < 200 and len(value) > 0:
            # Check if it's a reasonable option (number, percentage, short text)
            if re.match(r'^[$€£¥]?[\d,\.\-]+%?$', value) or len(value) < 100:
                options[letter] = value

    # Alternative: find options at the end of the block
    if len(options) < 3:
        # Pattern for percentage/currency options
        end_options = re.findall(r'([ABC])\.\s*([$€£¥]?[\d,\.\-]+%?\.?)(?:\s|$)', block_text)
        for letter, value in end_options:
            if letter not in options:
                options[letter] = value.rstrip('.')

    if correct_answer not in options or len(options) < 2:
        return None

    # Extract explanation
    explanation = ""
    exp_start = correct_match.end()

    # Find where explanation ends
    incorrect_match = re.search(r'[ABC]\s+is incorrect', block_text[exp_start:], re.IGNORECASE)
    if incorrect_match:
        explanation = block_text[exp_start:exp_start + incorrect_match.start()].strip()

    # Clean explanation
    explanation = re.sub(r'\n+', ' ', explanation)
    explanation = re.sub(r'\s+', ' ', explanation).strip()

    # Extract formula from ENTIRE block (formulas often appear after options)
    explanation_formula = extract_formula_from_text(block_text)

    # Extract calculator steps
    calculator_steps = extract_calculator_steps(block_text)

    # Extract wrong explanations
    explanation_wrong = {}
    for letter in ['A', 'B', 'C']:
        if letter != correct_answer:
            wrong_pattern = rf'{letter}\s+is incorrect\.?\s*(.*?)(?=[ABC]\s+is incorrect|\n\s*Year\n|\n\s*[ABC]\.\s*[$\d]|\Z)'
            wrong_match = re.search(wrong_pattern, block_text, re.DOTALL | re.IGNORECASE)
            if wrong_match:
                wrong_exp = wrong_match.group(1).strip()
                wrong_exp = re.sub(r'\n+', ' ', wrong_exp)
                wrong_exp = re.sub(r'\s+', ' ', wrong_exp).strip()
                # Remove table data that might have been captured
                if table_data:
                    for row in table_data.get('rows', []):
                        for cell in row:
                            wrong_exp = re.sub(rf'\b{re.escape(cell)}\b', '', wrong_exp)
                    for header in table_data.get('headers', []):
                        wrong_exp = wrong_exp.replace(header, '')
                wrong_exp = re.sub(r'\s+', ' ', wrong_exp).strip()
                if wrong_exp and len(wrong_exp) > 5:
                    explanation_wrong[letter] = wrong_exp[:1000]

    # Extract LOS reference
    los_match = re.search(r'(CFA Level[^©]+?LOS[^©\n]+)', block_text, re.IGNORECASE | re.DOTALL)
    los_text = ""
    if los_match:
        los_text = los_match.group(1).strip()
        los_text = re.sub(r'\n+', ' ', los_text)
        los_text = re.sub(r'\s+', ' ', los_text).strip()

    # Determine module
    module_id = extract_module_from_text(los_text or block_text, book_id)

    return {
        "question_id": f"{prefix}-{module_id}-{q_num.zfill(3)}",
        "question_number": int(q_num),
        "question_text": question_text,
        "question_text_formula": None,
        "question_continuation": question_continuation,
        "has_table": table_data is not None,
        "table_data": table_data,
        "has_image": False,
        "image_path": None,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation[:2000] if explanation else "",
        "explanation_formula": explanation_formula,
        "explanation_wrong": explanation_wrong,
        "calculator_steps": calculator_steps,
        "difficulty": "medium",
        "los_reference": los_text if los_text else None,
        "module_id": module_id
    }


def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text() + "\n"

    doc.close()
    return full_text


def parse_all_questions(pdf_path, book_id):
    """Parse all questions from the PDF file."""
    print(f"Reading PDF: {pdf_path}")
    text_content = extract_text_from_pdf(pdf_path)

    # Split by Q.XXX pattern
    question_pattern = r'(Q\.\d+\s+.*?)(?=Q\.\d+\s+|\Z)'
    question_blocks = re.findall(question_pattern, text_content, re.DOTALL)

    print(f"Found {len(question_blocks)} question blocks")

    questions = []
    tables_found = 0
    formulas_found = 0
    calc_steps_found = 0
    failed = 0

    for block in question_blocks:
        q = parse_question_block(block, book_id)
        if q and len(q['options']) >= 2:
            questions.append(q)
            if q.get('has_table'):
                tables_found += 1
            if q.get('explanation_formula'):
                formulas_found += 1
            if q.get('calculator_steps'):
                calc_steps_found += 1
        else:
            failed += 1

    print(f"Successfully parsed {len(questions)} questions")
    print(f"  - With tables: {tables_found}")
    print(f"  - With formulas: {formulas_found}")
    print(f"  - With calculator steps: {calc_steps_found}")
    print(f"  - Failed: {failed}")

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
        print("Usage: python parse_pdf_with_tables.py <book_id> <input_pdf> <output_json>")
        print("Example: python parse_pdf_with_tables.py 1 CH-1-Quantitative_Methods-Answers.pdf book1.json")
        sys.exit(1)

    book_id = int(sys.argv[1])
    input_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    config = BOOK_CONFIGS.get(book_id, {"name": f"Book {book_id}", "name_ru": f"Книга {book_id}"})

    print(f"Parsing Book {book_id}: {config['name']}")

    questions = parse_all_questions(input_path, book_id)
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
