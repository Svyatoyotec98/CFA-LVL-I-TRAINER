#!/usr/bin/env python3
"""
AnalystPrep PDF Parser - v3
Parses QBank questions from AnalystPrep format into Module 1 structure
"""

import json
import re
from pathlib import Path


def clean_text(text):
    """Clean text from tabs and extra whitespace"""
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    # Collapse multiple spaces/newlines into single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_options(raw_text):
    """
    Extract options from AnalystPrep format

    Options appear near end in format:
    A.
    $108,000.00
    B.
    $108,215.23
    C.
    $125,971.20
    """
    options = []

    # Find all option markers (A. B. C.)
    # Pattern: Find "A." or "B." or "C." followed by newline/tab and value
    # Stop at next option or single letter on new line (formula start)

    # Split text into lines for processing
    lines = raw_text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check if line is option marker (A. or B. or C.)
        opt_match = re.match(r'^([A-C])\.\s*$', line)

        if opt_match:
            letter = opt_match.group(1)

            # Look ahead for the value on next line(s)
            value_lines = []
            j = i + 1

            while j < len(lines):
                next_line = lines[j].strip()

                # Stop conditions:
                # 1. Empty line
                # 2. Next option (A. B. C.)
                # 3. Single letter ONLY if it's formula variable (F, V, P, N, I, Y, not t, r, m, n)
                # 4. Copyright symbol
                # 5. "CFA Level"

                if not next_line:
                    break
                if re.match(r'^[A-C]\.\s*$', next_line):
                    break
                # Only stop on formula variables (not on small variables like t, r, m, n)
                if re.match(r'^([FPVNIY]|PV|FV|PMT|CPT)$', next_line):  # Formula keywords
                    break
                if next_line.startswith('©') or 'CFA Level' in next_line:
                    break

                value_lines.append(next_line)
                j += 1

                # Stop after first meaningful line (usually the value)
                if len(value_lines) >= 1 and re.match(r'^\$?[\d,\.\-]+', value_lines[0]):
                    break

            # Join value lines and clean
            if value_lines:
                option_text = ' '.join(value_lines)
                option_text = clean_text(option_text)

                # Take only the first "sentence" - stop at period or long space
                option_text = re.split(r'\.\s+[A-Z]', option_text)[0]

                # Remove any formula remnants
                option_text = re.split(r'\s+[FPV]\s+[VN]\s*=', option_text)[0]
                option_text = re.split(r'\s+[A-Z]\s+[a-z]+\s+[a-z]+', option_text)[0]  # Remove "Annuity due"

                # Clean trailing punctuation except currency/numbers
                option_text = re.sub(r'\s+[A-Z]$', '', option_text)
                option_text = re.sub(r'[\[\]\(\)]+', '', option_text)

                option_text = option_text.strip()
                option_text = option_text.rstrip('.')

                # Accept if looks like a valid answer (number, currency, short text)
                if option_text and 3 <= len(option_text) <= 100:
                    # Must start with $ or digit or letter
                    if re.match(r'^[\$\d\w]', option_text):
                        options.append({
                            "id": f"opt{ord(letter) - ord('A') + 1}",
                            "text": option_text
                        })

            i = j
        else:
            i += 1

    # Return first 3 unique options
    seen = set()
    unique = []
    for opt in options:
        if opt['id'] not in seen:
            unique.append(opt)
            seen.add(opt['id'])
            if len(unique) == 3:
                break

    # FALLBACK 1: If no options or incomplete, search ANYWHERE in text for A./B./C. patterns
    if len(unique) < 3:
        # Look for pattern: "A. $value" or "A. value" anywhere in text
        # This catches cases where options appear after formulas
        fallback_options = []

        # Split by lines and look for "Letter. Value" on same or next line
        lines = raw_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()

            # Check if line is just "A." or "B." or "C."
            letter_match = re.match(r'^([A-C])\.\s*$', line)
            if letter_match and i + 1 < len(lines):
                letter = letter_match.group(1)
                next_line = lines[i + 1].strip()

                # Extract value from next line
                value_match = re.match(r'^([\$£€¥]?[\d,]+\.?\d*)(?:\s|$)', next_line)
                if value_match:
                    value = value_match.group(1)
                    opt_id = f"opt{ord(letter) - ord('A') + 1}"

                    if opt_id not in [o['id'] for o in unique]:
                        fallback_options.append({
                            "id": opt_id,
                            "text": value
                        })

        # Add fallback options (prioritize unique letters)
        for opt in fallback_options:
            if opt['id'] not in [o['id'] for o in unique]:
                unique.append(opt)
                if len(unique) >= 3:
                    break

    # FALLBACK 2: If still no options, try to extract from "X is incorrect" text
    if len(unique) == 0:
        unique = extract_options_from_incorrect_text(raw_text)

    # FALLBACK 3: If still incomplete, extract ALL calculator output values
    if len(unique) < 3:
        unique = extract_options_from_calculator_output(raw_text, unique)

    return unique[:3]  # Only return first 3


def extract_options_from_incorrect_text(raw_text):
    """
    Fallback: Extract options from "A is incorrect. The value of $X" format
    Used when standard options extraction fails
    """
    options = []

    # Pattern: "X is incorrect. [optional text] $value" or "X is incorrect. [text] value"
    # Also look for correct answer in calculator output or explanation

    # Find wrong answers from "X is incorrect"
    for letter in ['A', 'B', 'C']:
        pattern = rf'{letter}\s+is\s+incorrect[.:]\s+(.*?)(?=[A-C]\s+is\s+incorrect|CFA\s+Level|©|$)'
        match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)

        if match:
            text = match.group(1)

            # Extract first $ value or number from:
            # 1. "The value of $X"
            # 2. "PMT = $X" or "FV = $X"
            # 3. Any $X.XX pattern

            value_match = None

            # Try calculator output first (more specific)
            calc_match = re.search(r'(?:PMT|FV|PV|NPV)\s*=\s*(\$?[\d,]+\.?\d*)', text)
            if calc_match:
                value_match = calc_match
            else:
                # Try any $ value
                value_match = re.search(r'(\$[\d,]+\.?\d*)', text)
                if not value_match:
                    # Try percentage
                    value_match = re.search(r'([\d,]+\.?\d*%)', text)

            if value_match:
                value = value_match.group(1)
                # Clean value
                if len(value) >= 3:  # At least $10 or 10%
                    options.append({
                        "id": f"opt{ord(letter) - ord('A') + 1}",
                        "text": value
                    })

    # Find correct answer (usually in calculator output or explanation)
    # Look for patterns like "CPT=>FV = $345,411.20" or "PMT = $X"
    calc_patterns = [
        r'CPT\s*[=⇒>]+\s*(?:PMT|FV|PV|NPV|IRR)\s*=\s*(\$?[\d,]+\.?\d*)',  # CPT=>PMT=$X
        r'(?:PMT|FV|PV|NPV|IRR)\s*=\s*(\$[\d,]+\.?\d*)',  # PMT=$X
        r'=\s*(\$[\d,]+\.?\d*)',  # =$X
    ]

    correct_answer = None
    for pattern in calc_patterns:
        matches = re.findall(pattern, raw_text)
        if matches:
            # Take the first substantial value that's not already in options
            existing_values = [opt['text'] for opt in options]
            for val in matches:
                if len(val) > 3 and val not in existing_values:  # At least $100
                    correct_answer = val
                    break
            if correct_answer:
                break

    # Add correct answer as third option if we found it
    if correct_answer and len(options) < 3:
        # Determine which letter is missing (correct answer)
        existing_letters = set(chr(ord('A') + int(opt['id'][-1]) - 1) for opt in options)
        for letter in ['A', 'B', 'C']:
            if letter not in existing_letters:
                options.append({
                    "id": f"opt{ord(letter) - ord('A') + 1}",
                    "text": correct_answer
                })
                break

    return options[:3]


def extract_options_from_calculator_output(raw_text, existing_options):
    """
    FALLBACK 3: Extract all calculator output values (PMT, FV, PV, etc.)
    and assign them as options A/B/C
    """
    options = list(existing_options)  # Copy existing

    # Find all calculator output values (including short ones like "0")
    # Pattern: PMT = $X, FV = $X, PV = $X, NPV = $X, IRR = X%, rate = X%
    calc_pattern = r'(?:PMT|FV|PV|NPV|IRR|rate)\s*=\s*(\$?[\d,]+\.?\d*%?)'

    all_values = re.findall(calc_pattern, raw_text, re.IGNORECASE)

    # Get unique values not already in options (including short values)
    existing_texts = [opt['text'] for opt in options]
    unique_values = []
    for val in all_values:
        # Accept even short values (like "0") if nothing else available
        if val not in existing_texts and val not in unique_values:
            unique_values.append(val)

    # Assign to missing option letters
    existing_ids = [opt['id'] for opt in options]
    for letter in ['A', 'B', 'C']:
        opt_id = f"opt{ord(letter) - ord('A') + 1}"

        if opt_id not in existing_ids:
            if unique_values:
                value = unique_values.pop(0)
            else:
                # LAST RESORT: Add placeholder if absolutely nothing found
                value = f"[Option {letter} - incomplete]"

            options.append({
                "id": opt_id,
                "text": value
            })

        if len(options) >= 3:
            break

    return options[:3]


def extract_correct_answer(raw_text):
    """Extract correct answer letter (A, B, or C)"""
    match = re.search(
        r'The\s+correct\s+answer\s+is\s+([A-C])',
        raw_text,
        re.IGNORECASE
    )

    if match:
        letter = match.group(1).upper()
        return f"opt{ord(letter) - ord('A') + 1}"

    return "opt1"  # Default fallback


def extract_question_text(raw_text):
    """
    Extract question text (before "The correct answer is")
    """
    # Remove Q.XX at the start
    text = re.sub(r'^Q\.\d+\s+', '', raw_text)

    # Extract everything before "The correct answer is"
    match = re.search(
        r'^(.*?)(?=The\s+correct\s+answer\s+is)',
        text,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        question_text = clean_text(match.group(1))

        # Remove trailing colons or "is closest to:"
        question_text = re.sub(r':?\s*$', '', question_text)

        # Add colon at end if appropriate
        if re.search(r'(closest\s+to|equal\s+to|amount|value|rate|is)$', question_text, re.IGNORECASE):
            question_text += ':'

        return question_text

    return ""


def extract_explanation(raw_text):
    """
    Extract explanation (after "The correct answer is X." and before "A is incorrect")
    """
    # Find explanation between answer and first "X is incorrect"
    match = re.search(
        r'The\s+correct\s+answer\s+is\s+[A-C]\.\s+(.*?)(?=[A-C]\s+is\s+incorrect|$)',
        raw_text,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        explanation = clean_text(match.group(1))

        # Remove formula parts (they'll go in explanation_formula)
        explanation = re.sub(r'\s*F\s+V\s+=.*?(?=Where|Therefore|The|[A-C]\s+is|$)', '', explanation, flags=re.DOTALL)
        explanation = re.sub(r'\s*P\s+V\s+=.*?(?=Where|Therefore|The|[A-C]\s+is|$)', '', explanation, flags=re.DOTALL)

        # Limit to reasonable length
        if len(explanation) > 300:
            explanation = explanation[:300] + '...'

        return explanation

    return ""


def extract_formula(raw_text):
    """Extract formula and convert to LaTeX"""
    # Look for common TVM formulas
    formulas = []

    # FV formula
    if 'FV' in raw_text or 'future value' in raw_text.lower():
        if 'compounding' in raw_text.lower():
            formulas.append(r'$FV_N = PV \left[1 + \frac{r_s}{m}\right]^{mN}$')
        else:
            formulas.append(r'$FV = PV(1 + r)^N$')

    # PV formula
    if 'PV' in raw_text and 'annuity' in raw_text.lower():
        formulas.append(r'$PV = A \left[\frac{1 - \frac{1}{(1+r)^N}}{r}\right]$')
    elif 'PV' in raw_text:
        formulas.append(r'$PV = \frac{FV}{(1+r)^N}$')

    # Perpetuity
    if 'perpetuity' in raw_text.lower():
        formulas.append(r'$PV = \frac{A}{r}$')

    return formulas[0] if formulas else None


def extract_wrong_explanations(raw_text, options, correct_option_id):
    """Extract explanations for wrong answers"""
    wrong_explanations = {}

    for opt in options:
        if opt["id"] == correct_option_id:
            continue

        letter = chr(ord('A') + int(opt["id"][-1]) - 1)

        # Find "X is incorrect. [explanation]"
        pattern = rf'{letter}\s+is\s+incorrect[.:]?\s+(.*?)(?=[A-C]\s+is\s+incorrect|CFA\s+Level|©|$)'
        match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)

        if match:
            wrong_text = clean_text(match.group(1))

            # Limit length
            if len(wrong_text) > 150:
                wrong_text = wrong_text[:150] + '...'

            wrong_explanations[opt["id"]] = {
                "text": wrong_text,
                "formula": ""
            }

    return wrong_explanations


def extract_calculator_steps(raw_text):
    """Extract calculator steps if present"""
    steps = []

    # Look for BA II Plus calculator instructions
    # Pattern: "N=10; I/Y=6; PMT=$7,000; FV=0; CPT=>PV=$51,520.61"
    calc_match = re.search(
        r'(?:Using\s+the\s+)?BA\s+II\s+.*?Calculator[;:]?\s*(.*?)(?=[A-C]\s+is\s+incorrect|CFA\s+Level|©|$)',
        raw_text,
        re.DOTALL | re.IGNORECASE
    )

    if calc_match:
        calc_text = calc_match.group(1)

        # Parse calculator steps
        # Convert "N=10; I/Y=6; PMT=$7,000; FV=0; CPT=>PV" format to individual steps
        if 'N=' in calc_text or 'I/Y=' in calc_text:
            steps.append("[2ND] [CLR TVM]")

            # Extract values
            n_match = re.search(r'N\s*=\s*(\d+)', calc_text)
            iy_match = re.search(r'I/Y\s*=\s*([\d.]+)', calc_text)
            pmt_match = re.search(r'PMT\s*=\s*\$?([\d,]+)', calc_text)
            pv_match = re.search(r'PV\s*=\s*[-+]?\$?([\d,]+)', calc_text)
            fv_match = re.search(r'FV\s*=\s*[-+]?\$?([\d,]+)', calc_text)

            if pv_match and pv_match.group(1) != '0':
                steps.append(f"{pv_match.group(1)} [+/-] [PV]")
            if iy_match:
                steps.append(f"{iy_match.group(1)} [I/Y]")
            if n_match:
                steps.append(f"{n_match.group(1)} [N]")
            if pmt_match and pmt_match.group(1) != '0':
                steps.append(f"{pmt_match.group(1)} [PMT]")
            if fv_match and fv_match.group(1) == '0':
                steps.append("0 [FV]")

            # Add CPT step
            if 'CPT' in calc_text:
                if 'PV' in calc_text.split('CPT')[1]:
                    steps.append("[CPT] [PV]")
                elif 'FV' in calc_text.split('CPT')[1]:
                    steps.append("[CPT] [FV]")
                elif 'PMT' in calc_text.split('CPT')[1]:
                    steps.append("[CPT] [PMT]")

    return steps


def extract_los_reference(raw_text):
    """Extract LOS reference"""
    # Look for "LOS (a)" or "LOS 1d" patterns
    match = re.search(r'LOS\s+[(\[]?([a-z]|\d[a-z])[)\]]?', raw_text, re.IGNORECASE)
    if match:
        los = match.group(1).lower()
        # Format as "LOS 1d" or "LOS a"
        if len(los) == 2:
            return f"LOS {los[0]}{los[1]}"
        else:
            return f"LOS {los}"
    return ""


def determine_difficulty(raw_text, requires_calc):
    """Determine difficulty level"""
    # Count calculation steps
    calc_indicators = len(re.findall(r'\$[\d,]+', raw_text))
    has_annuity = 'annuity' in raw_text.lower()
    has_perpetuity = 'perpetuity' in raw_text.lower()

    if has_perpetuity or calc_indicators > 5 or has_annuity:
        return "HARD"
    elif requires_calc and calc_indicators > 2:
        return "MEDIUM"
    else:
        return "EASY"


def extract_topic_tags(raw_text):
    """Extract topic tags"""
    tags = []

    text_lower = raw_text.lower()

    # TVM concepts
    if 'future value' in text_lower or 'FV' in raw_text:
        tags.append('FV')
    if 'present value' in text_lower or 'PV' in raw_text:
        tags.append('PV')
    if 'annuity' in text_lower:
        tags.append('annuity')
    if 'perpetuity' in text_lower:
        tags.append('perpetuity')

    # Compounding
    if 'quarterly' in text_lower:
        tags.append('quarterly')
    elif 'monthly' in text_lower:
        tags.append('monthly')
    elif 'semi-annual' in text_lower:
        tags.append('semi-annual')
    elif 'continuous' in text_lower:
        tags.append('continuous')
    elif 'compound' in text_lower:
        tags.append('compounding')

    # General
    if 'calculator' in text_lower or 'BA II' in raw_text:
        tags.append('TVM')

    return tags[:4]  # Limit to 4 tags


def parse_question(raw_question, book_code="QM", chapter_id=2):
    """
    Parse a single question from AnalystPrep format to Module 1 structure

    Args:
        raw_question: dict with 'number' and 'raw_text' keys
        book_code: book code (e.g., 'QM')
        chapter_id: chapter number

    Returns:
        dict in Module 1 format
    """
    raw_text = raw_question['raw_text']
    q_number = int(re.search(r'\d+', raw_question['number']).group())

    # Extract all components
    question_text = extract_question_text(raw_text)
    options = extract_options(raw_text)
    correct_option_id = extract_correct_answer(raw_text)
    explanation = extract_explanation(raw_text)
    explanation_formula = extract_formula(raw_text)
    explanation_wrong = extract_wrong_explanations(raw_text, options, correct_option_id)
    calculator_steps = extract_calculator_steps(raw_text)
    los_reference = extract_los_reference(raw_text)
    requires_calc = bool(calculator_steps) or bool(explanation_formula)
    difficulty = determine_difficulty(raw_text, requires_calc)
    topic_tags = extract_topic_tags(raw_text)

    # Build question structure (Module 1 format - FLAT, not nested)
    question = {
        "question_id": f"{book_code}-{chapter_id}-{str(q_number).zfill(3)}",
        "question_number": q_number,
        "question_text": question_text,
        "question_text_ru": "",
        "question_text_formula": None,
        "question_continuation": None,
        "has_table": False,
        "table_data": None,
        "options": options,
        "correct_option_id": correct_option_id,
        "explanation": explanation,
        "explanation_ru": "",
        "explanation_formula": explanation_formula,
        "explanation_wrong": explanation_wrong,
        "requires_calculation": requires_calc,
        "calculator_steps": calculator_steps,
        "difficulty": difficulty,
        "los_reference": los_reference,
        "topic_tags": topic_tags
    }

    return question


def validate_question(question):
    """Validate parsed question quality"""
    errors = []

    # Check for "The correct answer" in question_text
    if 'correct answer' in question['question_text'].lower():
        errors.append(f"{question['question_id']}: Dirty question_text contains 'correct answer'")

    # Check options are clean (no formulas)
    for opt in question['options']:
        if re.search(r'[FP]\s+[VN]\s+=|[\[\]\(\)]+', opt['text']):
            errors.append(f"{question['question_id']}: Dirty option {opt['id']}: {opt['text'][:50]}")

    # Check correct_option_id exists
    option_ids = [o['id'] for o in question['options']]
    if question['correct_option_id'] not in option_ids:
        errors.append(f"{question['question_id']}: Invalid correct_option_id")

    # Check explanation not truncated mid-sentence
    if question['explanation'] and not question['explanation'].endswith(('.', '!', '?', '...')):
        errors.append(f"{question['question_id']}: Explanation may be truncated")

    return errors


def main():
    """Main parser function"""
    # Load split questions
    split_file = Path('Materials/QBank/Quants/extracted/ch2_module2_split.json')
    with open(split_file, 'r', encoding='utf-8') as f:
        raw_questions = json.load(f)

    print(f"Loaded {len(raw_questions)} questions from {split_file}")

    # Parse questions
    parsed_questions = []
    errors = []

    for raw_q in raw_questions:
        try:
            question = parse_question(raw_q, book_code="QM", chapter_id=2)
            parsed_questions.append(question)

            # Validate
            q_errors = validate_question(question)
            errors.extend(q_errors)

        except Exception as e:
            print(f"ERROR parsing {raw_q['number']}: {e}")
            errors.append(f"{raw_q['number']}: Parse exception: {e}")

    print(f"\nParsed {len(parsed_questions)} questions")
    print(f"Validation errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for err in errors[:10]:  # Show first 10
            print(f"  - {err}")

    # Create output JSON
    output = {
        "book_id": 1,
        "book_name": "Quantitative Methods",
        "book_name_ru": "Количественные методы",
        "chapter_id": 2,
        "chapter_name": "Time Value of Money",
        "chapter_name_ru": "Временная стоимость денег",
        "total_questions": len(parsed_questions),
        "questions": parsed_questions
    }

    # Save
    output_file = Path('frontend/data/qbank/book1_ch2_questions.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to {output_file}")
    print(f"✓ Total questions: {len(parsed_questions)}")

    return len(errors) == 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
