#!/usr/bin/env python3
"""
Create questions.json for v2 structure following QBANK_INSTRUCTION_v4.md
Enhanced with calculator_steps generation from glossary
"""

import json
import re
from docx import Document
from pathlib import Path

# ============== CONFIGURATION ==============
GLOSSARY_PATH = Path("frontend/data/v2/book1_quants/module1/glossary.json")
QBANK_PATH = Path("frontend/data/v2/book1_quants/module1/sources/qbank.docx")
TEMPLATES_PATH = Path("frontend/data/v2/calculator_templates.json")
OUTPUT_PATH = Path("frontend/data/v2/book1_quants/module1/questions.json")

# ============== TERM MAPPING (from glossary) ==============
TERM_KEYWORDS = {
    "QM-1-007": ["holding period return", "hpr", "total return earned from holding"],
    "QM-1-008": ["arithmetic mean", "simple average", "arithmetic average"],
    "QM-1-009": ["geometric mean", "compound return", "compound growth rate", "geometric average"],
    "QM-1-010": ["harmonic mean"],
    "QM-1-011": ["trimmed mean"],
    "QM-1-012": ["winsorized mean"],
    "QM-1-013": ["money-weighted", "mwrr", "internal rate of return", " irr"],
    "QM-1-014": ["time-weighted", "twrr"],
    "QM-1-015": ["effective annual rate", " ear ", "effective interest rate"],
    "QM-1-016": ["continuously compounded", "continuous return", "ln(", "natural logarithm"],
    "QM-1-017": ["gross return"],
    "QM-1-018": ["net return"],
    "QM-1-019": ["real return", "inflation-adjusted"],
    "QM-1-020": ["nominal return"],
    "QM-1-021": ["leveraged return", "borrowed funds", "leverage"],
}

# ============== STEP 0: LOAD GLOSSARY AND TEMPLATES ==============
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


def load_calculator_templates():
    """Load calculator_templates.json"""
    with open(TEMPLATES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    templates = data.get('templates', {})
    print(f"✅ Loaded {len(templates)} calculator templates")
    return templates


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

    # Special cases - compounding questions might be EAR but might also be just FV
    if "compounded" in combined_text and ("quarterly" in combined_text or "monthly" in combined_text or "annually" in combined_text):
        if "effective annual" in combined_text or "ear" in combined_text:
            return "QM-1-015"  # EAR
        # Otherwise it's just a general compounding question, return None

    return None


# ============== GENERATE LaTeX FORMULAS ==============
def generate_latex_formula(question_text, explanation_text, correct_option_text, term_id):
    """Generate LaTeX formula based on question content"""

    combined = (question_text + " " + explanation_text).lower()

    # FV with compounding
    if "future value" in combined or "fv" in combined:
        if "quarterly" in combined:
            return r"$FV_N = PV \left[1 + \frac{r_s}{m}\right]^{mN}$"
        elif "monthly" in combined:
            return r"$FV_N = PV \left[1 + \frac{r_s}{m}\right]^{mN}$"
        elif "continuously" in combined:
            return r"$FV_N = PV \cdot e^{r_s \cdot N}$"
        else:
            return r"$FV_N = PV \left[1 + \frac{r_s}{m}\right]^{mN}$"

    # EAR
    if term_id == "QM-1-015" or "effective annual" in combined:
        return r"$EAR = \left[1 + \frac{r_s}{m}\right]^{m} - 1$"

    # HPR
    if term_id == "QM-1-007" or "holding period return" in combined:
        return r"$HPR = \frac{P_1 - P_0 + D_1}{P_0}$"

    # Geometric mean
    if term_id == "QM-1-009" or "geometric mean" in combined:
        return r"$R_G = \sqrt[n]{\prod_{i=1}^{n}(1+R_i)} - 1$"

    # Arithmetic mean
    if term_id == "QM-1-008" or "arithmetic mean" in combined:
        return r"$\bar{R} = \frac{1}{n}\sum_{i=1}^{n}R_i$"

    # TWRR
    if term_id == "QM-1-014" or "time-weighted" in combined:
        return r"$TWRR = [(1+HPR_1)(1+HPR_2)\cdots(1+HPR_n)]^{1/n} - 1$"

    # MWRR/IRR
    if term_id == "QM-1-013" or "money-weighted" in combined or " irr" in combined:
        return r"$\sum_{t=0}^{n} \frac{CF_t}{(1+IRR)^t} = 0$"

    # Continuously compounded return
    if term_id == "QM-1-016" or "continuously compounded" in combined:
        return r"$r_{cc} = \ln\left(\frac{P_1}{P_0}\right)$"

    # Default: no formula
    return None


# ============== CALCULATOR STEPS GENERATION ==============

def extract_numbers_from_question(question_text, options_text, explanation_text):
    """Extract numerical values from question text"""
    combined = question_text + " " + options_text + " " + explanation_text

    numbers = {}

    # Extract percentages: 8%, 10.5%, -3%
    percent_matches = re.findall(r'([-+]?\d+\.?\d*)\s*%', combined)
    if percent_matches:
        numbers['percentages'] = [float(p) for p in percent_matches]

    # Extract money values: $150,000, $1,000, €5000
    money_matches = re.findall(r'[\$€£¥]\s?([\d,]+(?:\.\d+)?)', combined)
    if money_matches:
        numbers['money_values'] = [float(m.replace(',', '')) for m in money_matches]

    # Extract years/periods: "3 years", "5-year", "10 periods"
    year_matches = re.findall(r'(\d+)[-\s](?:year|yr|period)', combined, re.IGNORECASE)
    if year_matches:
        numbers['years'] = [int(y) for y in year_matches]

    # Determine compounding frequency
    combined_lower = combined.lower()
    if 'quarterly' in combined_lower or 'quarter' in combined_lower:
        numbers['compounding_frequency'] = 4
        numbers['compounding_name'] = 'quarterly'
    elif 'monthly' in combined_lower or 'month' in combined_lower:
        numbers['compounding_frequency'] = 12
        numbers['compounding_name'] = 'monthly'
    elif 'semiannual' in combined_lower or 'semi-annual' in combined_lower:
        numbers['compounding_frequency'] = 2
        numbers['compounding_name'] = 'semiannually'
    elif 'annual' in combined_lower and 'semi' not in combined_lower:
        numbers['compounding_frequency'] = 1
        numbers['compounding_name'] = 'annually'
    elif 'daily' in combined_lower:
        numbers['compounding_frequency'] = 365
        numbers['compounding_name'] = 'daily'

    # Extract return values for geometric/arithmetic mean calculations
    return_matches = re.findall(r'([-+]?\d+\.?\d*)%', combined)
    if len(return_matches) >= 2:
        numbers['returns'] = [float(r) for r in return_matches]

    return numbers


def determine_calculation_type(question_text, explanation_text, term_id):
    """Determine what type of calculation is needed based on question content"""
    combined = (question_text + " " + explanation_text).lower()

    # TVM calculations
    if any(word in combined for word in ['future value', ' fv ', 'worth at maturity', 'value in', 'maturity value']):
        return 'TVM_FV'

    if any(word in combined for word in ['present value', ' pv ', 'worth today', 'invest today', 'initial investment']):
        return 'TVM_PV'

    # Direct calculations from term_id
    if term_id == 'QM-1-007' or 'holding period return' in combined:
        return 'DIRECT_HPR'

    if term_id == 'QM-1-015' or ('effective annual rate' in combined and 'future value' not in combined):
        return 'DIRECT_EAR'

    if term_id == 'QM-1-016' or 'continuously compounded' in combined or 'continuous return' in combined:
        return 'DIRECT_continuous_return'

    if term_id == 'QM-1-008' or 'arithmetic mean' in combined:
        return 'STAT_mean'

    if term_id == 'QM-1-009' or 'geometric mean' in combined:
        return 'DIRECT_geometric_mean'

    if term_id == 'QM-1-013' or any(word in combined for word in ['money-weighted', 'mwrr', 'internal rate of return', ' irr ']):
        return 'CF_IRR'

    if term_id == 'QM-1-014' or 'time-weighted' in combined:
        return 'MULTI_STEP_TWRR'

    if term_id == 'QM-1-019' or 'real return' in combined:
        return 'DIRECT_real_return'

    if term_id == 'QM-1-021' or 'leveraged return' in combined:
        return 'DIRECT_leveraged_return'

    return None


def generate_calculator_steps(question_text, options_text, explanation_text, term_id, term_map, templates):
    """Generate calculator steps based on term_id and question content"""

    # Extract numbers from question
    numbers = extract_numbers_from_question(question_text, options_text, explanation_text)

    # Determine calculation type
    calc_type = determine_calculation_type(question_text, explanation_text, term_id)

    if not calc_type:
        return []

    # Get calculator data from glossary if term exists
    calc_from_glossary = None
    if term_id and term_id in term_map:
        calc_from_glossary = term_map[term_id].get('calculator')

    # Generate steps based on calculation type
    steps = []

    # TVM calculations
    if calc_type == 'TVM_FV':
        steps.append("[2ND] [CLR TVM]")

        # Set P/Y and C/Y if compounding frequency is known
        if 'compounding_frequency' in numbers:
            m = numbers['compounding_frequency']
            steps.append(f"[2ND] [P/Y] {m} [ENTER] [↓] {m} [ENTER]")
            steps.append("[2ND] [QUIT]")

        # Input known values
        if 'money_values' in numbers and len(numbers['money_values']) > 0:
            pv = numbers['money_values'][0]
            steps.append(f"{pv:,.0f} [+/-] [PV]")

        if 'percentages' in numbers and len(numbers['percentages']) > 0:
            rate = numbers['percentages'][0]
            steps.append(f"{rate} [I/Y]")

        if 'years' in numbers and 'compounding_frequency' in numbers:
            n = numbers['years'][0] * numbers['compounding_frequency']
            steps.append(f"{n} [N]")
        elif 'years' in numbers:
            n = numbers['years'][0]
            steps.append(f"{n} [N]")

        steps.append("0 [PMT]")
        steps.append("[CPT] [FV]")
        return steps

    elif calc_type == 'TVM_PV':
        steps.append("[2ND] [CLR TVM]")

        if 'compounding_frequency' in numbers:
            m = numbers['compounding_frequency']
            steps.append(f"[2ND] [P/Y] {m} [ENTER] [↓] {m} [ENTER]")
            steps.append("[2ND] [QUIT]")

        if 'money_values' in numbers and len(numbers['money_values']) > 0:
            fv = numbers['money_values'][0]
            steps.append(f"{fv:,.0f} [FV]")

        if 'percentages' in numbers and len(numbers['percentages']) > 0:
            rate = numbers['percentages'][0]
            steps.append(f"{rate} [I/Y]")

        if 'years' in numbers and 'compounding_frequency' in numbers:
            n = numbers['years'][0] * numbers['compounding_frequency']
            steps.append(f"{n} [N]")
        elif 'years' in numbers:
            n = numbers['years'][0]
            steps.append(f"{n} [N]")

        steps.append("0 [PMT]")
        steps.append("[CPT] [PV]")
        return steps

    # Template-based calculations
    elif calc_type in templates:
        template = templates[calc_type]
        # Return template steps directly (we could substitute values here, but that's complex)
        if 'steps' in template:
            return template['steps']

    # Try to get from glossary calculator
    elif calc_from_glossary:
        if 'template_id' in calc_from_glossary:
            template_id = calc_from_glossary['template_id']
            if template_id in templates:
                template = templates[template_id]
                if 'steps' in template:
                    return template['steps']
        elif 'steps' in calc_from_glossary:
            return calc_from_glossary['steps']

    return []


# ============== STEP 3: PARSE SINGLE QUESTION ==============
def parse_question(raw_question, term_map, templates):
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
            # Skip calculator step lines (we'll generate them later)
            if 'using the' in line.lower() and 'calculator' in line.lower():
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

    # Generate LaTeX formula
    correct_opt_text = next((opt['text'] for opt in options if opt['id'] == correct_option_id), "")
    explanation_formula = generate_latex_formula(question_text, explanation, correct_opt_text, term_id)

    # Generate calculator steps from glossary + question numbers
    options_text = " ".join([opt['text'] for opt in options])
    calculator_steps = generate_calculator_steps(question_text, options_text, explanation, term_id, term_map, templates)

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
        'explanation_formula': explanation_formula,
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
    print("CREATE QUESTIONS.JSON v4.1 (with Calculator Steps)")
    print("=" * 60)

    # STEP 0: Load glossary and templates
    term_map, glossary = load_glossary()
    templates = load_calculator_templates()

    # STEP 1: Extract questions from DOCX
    questions_raw = extract_questions_from_docx()

    # STEP 2-5: Parse each question
    questions = []
    for raw_q in questions_raw:  # All questions
        try:
            q = parse_question(raw_q, term_map, templates)
            questions.append(q)
            calc_status = f"calc:{len(q['calculator_steps'])} steps" if q['calculator_steps'] else "calc:none"
            print(f"✅ Q.{raw_q['number']:02d} - term:{q['term_id'] or 'None':12s} - formula:{'Yes' if q['explanation_formula'] else 'No ':3s} - {calc_status}")
        except Exception as e:
            print(f"❌ Failed Q.{raw_q['number']}: {e}")
            import traceback
            traceback.print_exc()

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
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"✅ SAVED: {OUTPUT_PATH}")
    print(f"   Total questions: {len(questions)}")
    print(f"   Questions with formulas: {sum(1 for q in questions if q['explanation_formula'])} ({sum(1 for q in questions if q['explanation_formula'])/len(questions)*100:.1f}%)")
    print(f"   Questions with term_id: {sum(1 for q in questions if q['term_id'])} ({sum(1 for q in questions if q['term_id'])/len(questions)*100:.1f}%)")
    print(f"   Questions with calculator_steps: {sum(1 for q in questions if q['calculator_steps'])} ({sum(1 for q in questions if q['calculator_steps'])/len(questions)*100:.1f}%)")
    print("=" * 60)


if __name__ == '__main__':
    main()
