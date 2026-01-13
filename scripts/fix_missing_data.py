#!/usr/bin/env python3
"""
Fix missing options and explanations in book1.json by re-extracting from PDF
"""

import fitz
import re
import json
from pathlib import Path

PDF_PATH = "/home/user/CFA-LVL-I-TRAINER/Materials/Tests/Tests/Copy of CH-1-Quantitative_Methods-Answers.pdf"
JSON_PATH = "/home/user/CFA-LVL-I-TRAINER/frontend/data/books/book1.json"

def extract_all_text(pdf_path):
    """Extract all text from PDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

def find_question_block(text, q_num):
    """Find the full question block for a given question number"""
    # Pattern to match Q.XXX and capture until next Q.XXX or end
    pattern = rf'Q\.{q_num}\s+(.*?)(?=Q\.\d+\s+[A-Z]|© 2014|$)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_options(block):
    """Extract options A, B, C from question block"""
    options = {}

    # Find options section - usually at the end after explanations
    # Pattern: A. ... B. ... C. ...
    lines = block.split('\n')

    # Look for option patterns
    for i, line in enumerate(lines):
        line = line.strip()

        # Match "A. text" at the start of a line
        if re.match(r'^A\.\s+', line):
            # Get option A - may span multiple lines until B.
            opt_text = re.sub(r'^A\.\s+', '', line)
            # Check if continues on next lines
            for j in range(i+1, len(lines)):
                next_line = lines[j].strip()
                if re.match(r'^[BC]\.\s+', next_line):
                    break
                if next_line and not next_line.startswith('©'):
                    opt_text += ' ' + next_line
            options['A'] = opt_text.strip()

        elif re.match(r'^B\.\s+', line):
            opt_text = re.sub(r'^B\.\s+', '', line)
            for j in range(i+1, len(lines)):
                next_line = lines[j].strip()
                if re.match(r'^[AC]\.\s+', next_line):
                    break
                if next_line and not next_line.startswith('©'):
                    opt_text += ' ' + next_line
            options['B'] = opt_text.strip()

        elif re.match(r'^C\.\s+', line):
            opt_text = re.sub(r'^C\.\s+', '', line)
            for j in range(i+1, len(lines)):
                next_line = lines[j].strip()
                if re.match(r'^[AB]\.\s+', next_line) or next_line.startswith('©'):
                    break
                if next_line:
                    opt_text += ' ' + next_line
            options['C'] = opt_text.strip()

    return options

def extract_explanation(block, correct_answer):
    """Extract explanation from question block"""
    # Find "The correct answer is X." and text after
    pattern = rf'The correct answer is {correct_answer}\.?\s*(.*?)(?=[ABC] is incorrect|$)'
    match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
    if match:
        explanation = match.group(1).strip()
        # Clean up
        explanation = re.sub(r'\s+', ' ', explanation)
        return explanation
    return ""

def extract_wrong_explanations(block):
    """Extract explanations for wrong answers"""
    wrong = {}

    # Pattern: "X is incorrect. explanation"
    for letter in ['A', 'B', 'C']:
        pattern = rf'{letter} is incorrect\.?\s*(.*?)(?=[ABC] is incorrect|A\.\s|B\.\s|C\.\s|$)'
        match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
        if match:
            expl = match.group(1).strip()
            expl = re.sub(r'\s+', ' ', expl)
            if expl:
                wrong[letter] = expl

    return wrong

def main():
    print("Loading PDF...")
    pdf_text = extract_all_text(PDF_PATH)

    print("Loading JSON...")
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)

    # Questions to fix
    problems = [
        778, 2755, 2835, 43, 3429, 3719, 993, 425, 1110, 1901,
        2777, 2778, 2779, 2781, 3474, 3823, 4447, 4707, 4727,
        4730, 3426, 3707, 3709,
        # Empty explanations
        221, 1305, 1319, 1325, 2674, 2676, 2680, 2836, 2839
    ]

    fixed_count = 0

    for module in data.get('learning_modules', []):
        for q in module.get('questions', []):
            q_num = q.get('question_number')
            if q_num not in problems:
                continue

            print(f"\nProcessing Q.{q_num}...")

            block = find_question_block(pdf_text, q_num)
            if not block:
                print(f"  Could not find Q.{q_num} in PDF")
                continue

            # Extract options
            current_opts = q.get('options', {})
            if len(current_opts) < 3:
                new_opts = extract_options(block)
                if len(new_opts) >= 3:
                    q['options'] = new_opts
                    print(f"  Fixed options: {list(new_opts.keys())}")
                    fixed_count += 1
                elif new_opts:
                    # Merge what we found
                    current_opts.update(new_opts)
                    q['options'] = current_opts
                    print(f"  Partially fixed options: {list(current_opts.keys())}")

            # Extract explanation if empty
            current_expl = q.get('explanation', '') or ''
            if len(current_expl.strip()) < 20:
                correct = q.get('correct_answer', 'A')
                new_expl = extract_explanation(block, correct)
                if new_expl:
                    q['explanation'] = new_expl
                    print(f"  Fixed explanation: {len(new_expl)} chars")
                    fixed_count += 1

            # Extract wrong explanations
            wrong = extract_wrong_explanations(block)
            if wrong:
                q['explanation_wrong'] = wrong
                print(f"  Fixed wrong explanations: {list(wrong.keys())}")

    # Save
    print(f"\nSaving {fixed_count} fixes...")
    with open(JSON_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Done!")

if __name__ == "__main__":
    main()
