#!/usr/bin/env python3
"""
Fix truncated options by re-extracting from PDF
"""

import fitz
import re
import json

PDF_PATH = "/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests/Copy of CH-1-Quantitative_Methods-Answers.pdf"
JSON_PATH = "/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book1.json"

def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

def find_question_block(text, q_num):
    pattern = rf'Q\.{q_num}\s+(.*?)(?=Q\.\d+\s+[A-Z]|© 2014-2024|$)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return None

def extract_options_improved(block):
    """Extract options with better handling of percentages and decimals"""
    options = {}

    # Find option patterns at end of block
    # Pattern: "A. value" where value can be percentage, currency, decimal, etc.

    # Try to find options section (usually after explanation)
    lines = block.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()

        # Match A. B. C. at start of line with various value formats
        for letter in ['A', 'B', 'C']:
            pattern = rf'^{letter}\.\s+(.+?)$'
            match = re.match(pattern, line)
            if match:
                value = match.group(1).strip()
                # Clean up value
                value = re.sub(r'\s+', ' ', value)
                # Remove trailing periods if any
                value = value.rstrip('.')
                if value and len(value) > 0:
                    options[letter] = value

    return options

def is_suspicious_option(opts):
    """Check if options look truncated"""
    if not opts:
        return True

    for v in opts.values():
        v_str = str(v).strip()
        # Suspicious if: all zeros, single digits, or very short without symbols
        if v_str in ['0', '-0']:
            return True
        # Short number without %, $, or other context
        if len(v_str) <= 2 and v_str.isdigit():
            # Could be legitimate but suspicious
            continue

    # Check if all options are suspiciously similar or all zeros
    values = [str(v).strip() for v in opts.values()]
    if all(v == '0' for v in values):
        return True

    return False

def main():
    print("Loading PDF...")
    pdf_text = extract_pdf_text(PDF_PATH)

    print("Loading JSON...")
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)

    # Find questions with suspicious options
    suspicious = []
    for module in data.get('learning_modules', []):
        for q in module.get('questions', []):
            opts = q.get('options', {})
            q_num = q.get('question_number')

            # Check if suspicious
            values = [str(v).strip() for v in opts.values()]

            # Suspicious conditions:
            # 1. All zeros
            # 2. Very short values that look truncated
            # 3. Values starting with [ (parsing error)

            is_susp = False
            if all(v == '0' for v in values):
                is_susp = True
            elif any(v.startswith('[') for v in values):
                is_susp = True
            elif len(opts) == 3:
                # Check if looks like truncated percentages/decimals
                all_short = all(len(v) <= 2 for v in values)
                no_symbols = all(not any(c in v for c in ['%', '$', '.', ',']) for v in values)
                if all_short and no_symbols:
                    is_susp = True

            if is_susp:
                suspicious.append(q_num)

    print(f"Found {len(suspicious)} suspicious questions")

    fixed_count = 0

    for module in data.get('learning_modules', []):
        for q in module.get('questions', []):
            q_num = q.get('question_number')
            if q_num not in suspicious:
                continue

            block = find_question_block(pdf_text, q_num)
            if not block:
                print(f"Q.{q_num}: Not found in PDF")
                continue

            new_opts = extract_options_improved(block)

            if len(new_opts) >= 3:
                old_opts = q.get('options', {})
                # Only update if new options look better
                new_values = [str(v) for v in new_opts.values()]

                # Check if new options are better
                has_symbols = any(any(c in v for c in ['%', '$', '.']) for v in new_values)
                longer = any(len(v) > 2 for v in new_values)

                if has_symbols or longer:
                    q['options'] = new_opts
                    print(f"Q.{q_num}: {old_opts} -> {new_opts}")
                    fixed_count += 1
                else:
                    print(f"Q.{q_num}: New options not better: {new_opts}")
            else:
                print(f"Q.{q_num}: Could not extract 3 options, got: {new_opts}")

    print(f"\nFixed {fixed_count} questions")

    # Save
    with open(JSON_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Saved!")

if __name__ == "__main__":
    main()
