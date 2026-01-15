#!/usr/bin/env python3
"""
Create questions.json for v2 structure following QBANK_INSTRUCTION_v4.md
"""

import json
import re
from docx import Document
from pathlib import Path

# ============== CONFIGURATION ==============
GLOSSARY_PATH = Path("frontend/data/v2/book1_quants/module1/glossary.json")
QBANK_PATH = Path("frontend/data/v2/book1_quants/module1/sources/qbank.docx")
OUTPUT_PATH = Path("frontend/data/v2/book1_quants/module1/questions.json")

# ============== TERM MAPPING (from glossary) ==============
TERM_KEYWORDS = {
    "QM-1-007": ["holding period return", "hpr"],
    "QM-1-008": ["arithmetic mean", "simple average"],
    "QM-1-009": ["geometric mean", "compound return"],
    "QM-1-010": ["harmonic mean"],
    "QM-1-011": ["trimmed mean"],
    "QM-1-012": ["winsorized mean"],
    "QM-1-013": ["money-weighted", "mwrr", "irr"],
    "QM-1-014": ["time-weighted", "twrr"],
    "QM-1-015": ["effective annual rate", "ear"],
    "QM-1-016": ["continuously compounded", "continuous return", "ln("],
    "QM-1-017": ["gross return"],
    "QM-1-018": ["net return"],
    "QM-1-019": ["real return", "inflation-adjusted"],
    "QM-1-020": ["nominal return"],
    "QM-1-021": ["leveraged return", "borrowed funds", "leverage"],
}

# ============== STEP 0: LOAD GLOSSARY ==============
def load_glossary():
    """Load glossary.json and extract term mapping"""
    with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
        glossary = json.load(f)

    term_map = {}
    for term in glossary['terms']:
        term_map[term['term_id']] = {
            'term_en': term['term_en'],
            'term_ru': term['term_ru'],
            'los_id': term['los_id'],
            'formula': term.get('formula'),
            'calculator': term.get('calculator')
        }

    print(f"✅ Loaded {len(term_map)} terms from glossary")
    return term_map, glossary


# ============== STEP 1: EXTRACT TEXT FROM DOCX ==============
def extract_questions_from_docx():
    """Extract all questions from qbank.docx"""
    doc = Document(QBANK_PATH)

    questions_raw = []
    current_question = None
    current_lines = []

    for para in doc.paragraphs:
        text = para.text.strip()

        # Start of new question
        if re.match(r'^Q\.\d+', text):
            # Save previous question
            if current_question is not None:
                questions_raw.append({
                    'number': current_question,
                    'lines': current_lines
                })

            # Extract question number
            match = re.match(r'^Q\.(\d+)', text)
            current_question = int(match.group(1))
            current_lines = [text]
        elif current_question is not None and text:
            current_lines.append(text)

    # Save last question
    if current_question is not None:
        questions_raw.append({
            'number': current_question,
            'lines': current_lines
        })

    print(f"✅ Extracted {len(questions_raw)} questions from DOCX")
    return questions_raw


# ============== STEP 2: FIND TERM_ID ==============
def find_term_id(question_text, explanation_text):
    """Find matching term_id based on keywords in question and explanation"""
    combined_text = (question_text + " " + explanation_text).lower()

    for term_id, keywords in TERM_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in combined_text:
                return term_id

    # Special cases - compounding questions might be EAR
    if "compounded" in combined_text and ("quarterly" in combined_text or "monthly" in combined_text):
        if "effective annual" in combined_text:
            return "QM-1-015"  # EAR

    return None


# ============== STEP 3: PARSE SINGLE QUESTION ==============
def parse_question(raw_question, term_map):
    """Parse a single raw question into structured format"""
    lines = raw_question['lines']
    q_num = raw_question['number']

    # Extract question text (first line)
    question_text = re.sub(r'^Q\.\d+\s+', '', lines[0])

    # Find options and correct answer
    options = []
    correct_letter = None

    # Join all lines to find options (they might be on same line)
    full_text = " ".join(lines)

    # Extract options A, B, C
    opt_a_match = re.search(r'A\.\s+([^\n]+?)(?=\s+B\.|The correct)', full_text)
    opt_b_match = re.search(r'B\.\s+([^\n]+?)(?=\s+C\.|The correct)', full_text)
    opt_c_match = re.search(r'C\.\s+([^\n]+?)(?=\s+The correct)', full_text)

    if opt_a_match:
        options.append({'id': 'opt1', 'text': opt_a_match.group(1).strip()})
    if opt_b_match:
        options.append({'id': 'opt2', 'text': opt_b_match.group(1).strip()})
    if opt_c_match:
        options.append({'id': 'opt3', 'text': opt_c_match.group(1).strip()})

    # Find correct answer
    for line in lines:
        if 'correct answer is' in line.lower():
            match = re.search(r'correct answer is\s+([ABC])', line, re.IGNORECASE)
            if match:
                correct_letter = match.group(1)

    # Map correct letter to opt ID
    correct_option_id = f'opt{ord(correct_letter) - ord("A") + 1}' if correct_letter else None

    # Extract explanation
    explanation = ""
    explanation_lines = []
    calculator_steps = []
    capture_explanation = False

    for i, line in enumerate(lines):
        if 'correct answer is' in line.lower():
            capture_explanation = True
            continue

        if capture_explanation:
            if re.match(r'^[ABC]\s+is incorrect', line):
                break
            # Skip copyright and meta lines
            if line.startswith('©') or line.startswith('CFA Level') or line.isdigit():
                continue
            # Extract calculator steps if present
            if 'using the' in line.lower() and 'calculator' in line.lower():
                # This is calculator steps
                calc_match = re.search(r'(?:Using|BA II).*?:\s*(.+)', line, re.IGNORECASE)
                if calc_match:
                    steps_text = calc_match.group(1)
                    # Parse calculator steps
                    if ';' in steps_text:
                        calculator_steps = [s.strip() for s in steps_text.split(';') if s.strip()]
                continue
            if line and len(line) > 5:  # Skip very short lines
                explanation_lines.append(line)

    explanation = " ".join(explanation_lines).strip()
    # Clean up explanation
    explanation = re.sub(r'\s+', ' ', explanation)
    explanation = re.sub(r'Where;\s+', '', explanation)

    # Extract wrong explanations
    explanation_wrong = {}

    for i, line in enumerate(lines):
        match = re.match(r'^([ABC])\s+is incorrect', line)
        if match:
            letter = match.group(1)
            opt_id = f'opt{ord(letter) - ord("A") + 1}'

            # Get explanation text
            wrong_text = line
            # Look for formula in next lines
            formula = None
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if '=' in next_line and '$' in next_line:
                    formula = f"${next_line}$"

            explanation_wrong[opt_id] = {
                'text': wrong_text,
                'text_ru': "",  # Will be filled later
                'formula': formula
            }

    # Extract LOS
    los_id = None
    for line in lines:
        if 'LOS' in line:
            # Extract LOS (d) or similar
            match = re.search(r'LOS\s+\(([a-e])\)', line, re.IGNORECASE)
            if match:
                letter = match.group(1)
                los_id = f"LOS_1{letter}"

    # Find term_id
    term_id = find_term_id(question_text, explanation)

    # Determine if requires calculation
    requires_calculation = any(word in question_text.lower() for word in ['calculate', 'closest to', 'value', 'return', 'rate'])

    # Determine difficulty
    difficulty = "MEDIUM"  # Default
    if len(question_text.split()) < 30:
        difficulty = "EASY"
    elif "and" in question_text and len(question_text.split()) > 50:
        difficulty = "HARD"

    # Build question object
    question = {
        'question_id': f'QM-1-Q{q_num:03d}',
        'question_number': q_num,
        'term_id': term_id,
        'los_id': los_id or "LOS_1d",  # Default
        'question_text': question_text,
        'question_text_ru': "",  # Will be filled later
        'question_text_formula': None,
        'question_continuation': None,
        'has_table': False,
        'table_data': None,
        'options': options,
        'correct_option_id': correct_option_id,
        'explanation': explanation,
        'explanation_ru': "",
        'explanation_formula': None,
        'explanation_wrong': explanation_wrong,
        'requires_calculation': requires_calculation,
        'calculator_steps': calculator_steps,
        'difficulty': difficulty,
        'topic_tags': []
    }

    return question


# ============== MAIN ==============
def main():
    print("=" * 60)
    print("CREATE QUESTIONS.JSON v4.0")
    print("=" * 60)

    # STEP 0: Load glossary
    term_map, glossary = load_glossary()

    # STEP 1: Extract questions from DOCX
    questions_raw = extract_questions_from_docx()

    # STEP 2-5: Parse each question
    questions = []
    for raw_q in questions_raw[:5]:  # First 5 for testing
        try:
            q = parse_question(raw_q, term_map)
            questions.append(q)
            print(f"✅ Parsed Q.{raw_q['number']} - term_id: {q['term_id']}")
        except Exception as e:
            print(f"❌ Failed Q.{raw_q['number']}: {e}")

    # Build output structure
    output = {
        'book_id': glossary['book_id'],
        'book_code': glossary['book_code'],
        'book_name': glossary['book_name'],
        'book_name_ru': glossary['book_name_ru'],
        'module_id': glossary['module_id'],
        'module_name': glossary['module_name'],
        'module_name_ru': glossary['module_name_ru'],
        'total_questions': len(questions),
        'questions': questions
    }

    # Save to file
    output_path = OUTPUT_PATH.parent / "questions_preview.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"✅ SAVED: {output_path}")
    print(f"   Total questions: {len(questions)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
