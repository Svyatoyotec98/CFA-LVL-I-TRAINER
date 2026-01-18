#!/usr/bin/env python3
"""
QBANK Validator v1.0
Проверяет и исправляет JSON файлы с тестами

Использование:
  python validate_qbank.py qbank_module_1.json          # Только проверка
  python validate_qbank.py qbank_module_1.json --fix    # Проверка + авто-исправление
"""

import json
import sys
import os
import shutil
from datetime import datetime
from typing import Dict, List, Tuple

# Цвета для терминала
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")


def print_result(check_name: str, passed: bool, details: str = ""):
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {status}  {check_name}")
    if details and not passed:
        print(f"         {YELLOW}→ {details}{RESET}")


def print_fix(action: str):
    print(f"  {CYAN}🔧 AUTO-FIX: {action}{RESET}")


def print_manual(action: str):
    print(f"  {YELLOW}📝 MANUAL FIX NEEDED: {action}{RESET}")


def backup_file(filepath: str) -> str:
    """Создаёт backup файла перед изменениями"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path


def validate_json_syntax(filepath: str) -> Tuple[bool, dict | None, str]:
    """Проверка 1: Валидный ли JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, data, ""
    except json.JSONDecodeError as e:
        return False, None, f"Line {e.lineno}, col {e.colno}: {e.msg}"
    except FileNotFoundError:
        return False, None, f"File not found: {filepath}"


def validate_qbank(filepath: str, auto_fix: bool = False) -> Dict:
    """Полная валидация файла qbank"""
    
    results = {
        'file': filepath,
        'checks': [],
        'passed': 0,
        'failed': 0,
        'fixed': 0,
        'manual_fixes': []
    }
    
    print_header(f"QBANK: {os.path.basename(filepath)}")
    
    # ========== CHECK 1: JSON Syntax ==========
    valid, data, error = validate_json_syntax(filepath)
    results['checks'].append(('JSON синтаксис', valid, error))
    print_result('JSON синтаксис', valid, error)
    
    if not valid:
        results['failed'] += 1
        results['manual_fixes'].append(f"Исправь JSON синтаксис: {error}")
        print_manual(f"Открой файл и исправь ошибку: {error}")
        return results
    results['passed'] += 1
    
    modified = False  # Флаг что данные изменились
    
    # ========== CHECK 2: Metadata exists ==========
    has_metadata = 'metadata' in data
    results['checks'].append(('Metadata существует', has_metadata, ""))
    print_result('Metadata существует', has_metadata)
    
    if not has_metadata:
        results['failed'] += 1
        results['manual_fixes'].append("Добавь секцию metadata в JSON")
        print_manual("Добавь metadata: {book_id, book_code, module_id, module_name, ...}")
        return results
    results['passed'] += 1
    
    # ========== CHECK 3: Required metadata fields ==========
    required_meta = ['book_id', 'book_code', 'module_id', 'module_name', 'module_name_ru', 'total_questions']
    missing_meta = [f for f in required_meta if f not in data['metadata']]
    meta_ok = len(missing_meta) == 0
    
    results['checks'].append(('Metadata поля', meta_ok, f"Missing: {missing_meta}" if not meta_ok else ""))
    print_result('Metadata поля', meta_ok, f"Missing: {missing_meta}" if not meta_ok else "")
    
    if meta_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
        results['manual_fixes'].append(f"Добавь недостающие поля в metadata: {missing_meta}")
        print_manual(f"Добавь в metadata: {missing_meta}")
    
    # ========== CHECK 4: Questions array exists ==========
    has_questions = 'questions' in data and isinstance(data['questions'], list)
    results['checks'].append(('Questions массив существует', has_questions, ""))
    print_result('Questions массив существует', has_questions)
    
    if not has_questions:
        results['failed'] += 1
        results['manual_fixes'].append("Добавь массив 'questions' с вопросами")
        print_manual("Добавь структуру: \"questions\": [{...}, {...}]")
        return results
    results['passed'] += 1
    
    questions = data['questions']
    
    # ========== CHECK 5: Minimum questions count ==========
    min_questions = 15
    count_ok = len(questions) >= min_questions
    results['checks'].append((f'Минимум вопросов (>={min_questions})', count_ok, f"Found: {len(questions)}"))
    print_result(f'Минимум вопросов (>={min_questions})', count_ok, f"Found: {len(questions)}")
    
    if count_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
        results['manual_fixes'].append(f"Слишком мало вопросов ({len(questions)}). Добавь ещё из PDF.")
        print_manual(f"Только {len(questions)} вопросов. Вернись к qbank.pdf и добавь недостающие.")
    
    # ========== CHECK 6: total_questions matches ==========
    declared_total = data['metadata'].get('total_questions', 0)
    count_match = declared_total == len(questions)
    
    results['checks'].append(('total_questions совпадает', count_match,
                             f"Declared: {declared_total}, Actual: {len(questions)}"))
    print_result('total_questions совпадает', count_match,
                f"Declared: {declared_total}, Actual: {len(questions)}")
    
    if count_match:
        results['passed'] += 1
    else:
        if auto_fix:
            data['metadata']['total_questions'] = len(questions)
            print_fix(f"total_questions: {declared_total} → {len(questions)}")
            modified = True
            results['fixed'] += 1
        else:
            results['failed'] += 1
            results['manual_fixes'].append(f"Исправь total_questions: {declared_total} → {len(questions)}")
            print_manual(f"Измени total_questions с {declared_total} на {len(questions)}")
    
    # ========== CHECK 7: Required question fields ==========
    required_q_fields = ['question_id', 'question_text_en', 'question_text_ru', 'options', 'correct_option_id']
    q_issues = []
    
    for q in questions:
        for field in required_q_fields:
            if field not in q or not q[field]:
                q_issues.append((q.get('question_id', 'UNKNOWN'), field))
    
    q_fields_ok = len(q_issues) == 0
    details = f"{len(q_issues)} issues" if not q_fields_ok else ""
    results['checks'].append(('Вопросы: обязательные поля', q_fields_ok, details))
    print_result('Вопросы: обязательные поля', q_fields_ok, details)
    
    if q_fields_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
        for qid, field in q_issues[:5]:
            results['manual_fixes'].append(f"Заполни {field} для вопроса {qid}")
            print_manual(f"Вопрос {qid}: заполни поле '{field}'")
        if len(q_issues) > 5:
            print(f"         {YELLOW}... и ещё {len(q_issues) - 5} проблем{RESET}")
    
    # ========== CHECK 8: Unique question IDs ==========
    all_q_ids = [q.get('question_id') for q in questions]
    duplicates = list(set([qid for qid in all_q_ids if all_q_ids.count(qid) > 1]))
    unique_ok = len(duplicates) == 0
    
    results['checks'].append(('Уникальные question_id', unique_ok,
                             f"Duplicates: {duplicates}" if not unique_ok else ""))
    print_result('Уникальные question_id', unique_ok,
                f"Duplicates: {duplicates}" if not unique_ok else "")
    
    if unique_ok:
        results['passed'] += 1
    else:
        if auto_fix:
            seen = {}
            for q in questions:
                qid = q.get('question_id')
                if qid in seen:
                    seen[qid] += 1
                    new_id = f"{qid}_{seen[qid]}"
                    q['question_id'] = new_id
                    print_fix(f"Переименован {qid} → {new_id}")
                else:
                    seen[qid] = 1
            modified = True
            results['fixed'] += 1
        else:
            results['failed'] += 1
            results['manual_fixes'].append(f"Исправь дублирующиеся question_id: {duplicates}")
            print_manual(f"Переименуй дубликаты: {duplicates}")
    
    # ========== CHECK 9: Options structure ==========
    opt_issues = []
    for q in questions:
        options = q.get('options', [])
        if len(options) < 2:
            opt_issues.append((q.get('question_id'), 'less than 2 options'))
        for opt in options:
            if 'id' not in opt:
                opt_issues.append((q.get('question_id'), 'option missing id'))
            if 'text_en' not in opt or not opt.get('text_en'):
                opt_issues.append((q.get('question_id'), 'option missing text_en'))
            if 'text_ru' not in opt or not opt.get('text_ru'):
                opt_issues.append((q.get('question_id'), 'option missing text_ru'))
    
    opt_ok = len(opt_issues) == 0
    results['checks'].append(('Options структура', opt_ok, f"{len(opt_issues)} issues" if not opt_ok else ""))
    print_result('Options структура', opt_ok, f"{len(opt_issues)} issues" if not opt_ok else "")
    
    if opt_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
        for qid, issue in opt_issues[:5]:
            results['manual_fixes'].append(f"Вопрос {qid}: {issue}")
            print_manual(f"Вопрос {qid}: {issue}")
        if len(opt_issues) > 5:
            print(f"         {YELLOW}... и ещё {len(opt_issues) - 5} проблем{RESET}")
    
    # ========== CHECK 10: correct_option_id exists ==========
    correct_issues = []
    for q in questions:
        correct_id = q.get('correct_option_id')
        option_ids = [opt.get('id') for opt in q.get('options', [])]
        if correct_id not in option_ids:
            correct_issues.append((q.get('question_id'), correct_id, option_ids))
    
    correct_ok = len(correct_issues) == 0
    results['checks'].append(('correct_option_id валидный', correct_ok,
                             f"{len(correct_issues)} issues" if not correct_ok else ""))
    print_result('correct_option_id валидный', correct_ok,
                f"{len(correct_issues)} issues" if not correct_ok else "")
    
    if correct_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
        for qid, correct, opts in correct_issues[:3]:
            results['manual_fixes'].append(f"Вопрос {qid}: correct_option_id='{correct}' не существует в {opts}")
            print_manual(f"Вопрос {qid}: '{correct}' не в {opts}")
    
    # ========== CHECK 11: Explanations exist ==========
    exp_issues = []
    for q in questions:
        if not q.get('explanation_en'):
            exp_issues.append((q.get('question_id'), 'explanation_en'))
        if not q.get('explanation_ru'):
            exp_issues.append((q.get('question_id'), 'explanation_ru'))
    
    exp_ok = len(exp_issues) == 0
    results['checks'].append(('Explanations EN/RU', exp_ok,
                             f"{len(exp_issues)} missing" if not exp_ok else ""))
    print_result('Explanations EN/RU', exp_ok, f"{len(exp_issues)} missing" if not exp_ok else "")
    
    if exp_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
        for qid, field in exp_issues[:5]:
            results['manual_fixes'].append(f"Добавь {field} для вопроса {qid}")
            print_manual(f"Вопрос {qid}: добавь {field}")
    
    # ========== CHECK 12: Tables consistency ==========
    table_issues = []
    for q in questions:
        if q.get('has_table') == True and not q.get('table_data'):
            table_issues.append(q.get('question_id'))
    
    table_ok = len(table_issues) == 0
    results['checks'].append(('Tables консистентность', table_ok,
                             f"has_table=true but no data: {table_issues}" if not table_ok else ""))
    print_result('Tables консистентность', table_ok,
                f"has_table=true but no data: {table_issues}" if not table_ok else "")
    
    if table_ok:
        results['passed'] += 1
    else:
        if auto_fix:
            for q in questions:
                if q.get('has_table') == True and not q.get('table_data'):
                    q['has_table'] = False
                    print_fix(f"Вопрос {q.get('question_id')}: has_table → false")
            modified = True
            results['fixed'] += 1
        else:
            results['failed'] += 1
            for qid in table_issues:
                results['manual_fixes'].append(f"Вопрос {qid}: добавь table_data или поставь has_table: false")
                print_manual(f"Вопрос {qid}: добавь table_data или has_table: false")
    
    # ========== CHECK 13: Calculator consistency ==========
    calc_issues = []
    for q in questions:
        if q.get('requires_calculator') == True and not q.get('calculator_keystrokes'):
            calc_issues.append(q.get('question_id'))
    
    calc_ok = len(calc_issues) == 0
    results['checks'].append(('Calculator keystrokes', calc_ok,
                             f"Missing keystrokes: {calc_issues}" if not calc_ok else ""))
    print_result('Calculator keystrokes', calc_ok,
                f"Missing keystrokes: {calc_issues}" if not calc_ok else "")
    
    if calc_ok:
        results['passed'] += 1
    else:
        if auto_fix:
            for q in questions:
                if q.get('requires_calculator') == True and not q.get('calculator_keystrokes'):
                    q['requires_calculator'] = False
                    print_fix(f"Вопрос {q.get('question_id')}: requires_calculator → false")
            modified = True
            results['fixed'] += 1
        else:
            results['failed'] += 1
            for qid in calc_issues:
                results['manual_fixes'].append(f"Вопрос {qid}: добавь calculator_keystrokes или requires_calculator: false")
                print_manual(f"Вопрос {qid}: добавь keystrokes или requires_calculator: false")
    
    # ========== CHECK 14: EN/RU questions differ ==========
    copy_paste_q = []
    for q in questions:
        if q.get('question_text_en') == q.get('question_text_ru'):
            if q.get('question_text_en'):
                copy_paste_q.append(q.get('question_id'))
    
    no_copy_q = len(copy_paste_q) == 0
    results['checks'].append(('EN/RU вопросы различаются', no_copy_q,
                             f"Same text: {copy_paste_q[:3]}" if not no_copy_q else ""))
    print_result('EN/RU вопросы различаются', no_copy_q,
                f"Same text: {copy_paste_q[:3]}" if not no_copy_q else "")
    
    if no_copy_q:
        results['passed'] += 1
    else:
        results['failed'] += 1
        for qid in copy_paste_q[:3]:
            results['manual_fixes'].append(f"Переведи question_text_ru для вопроса {qid}")
            print_manual(f"Вопрос {qid}: question_text_en == question_text_ru (нужен перевод)")

    # ========== CHECK 15: Tables have data (WARNING) ==========
    table_warnings = []
    for q in questions:
        if q.get('has_table') == True:
            table_data = q.get('table_data', {})
            rows = table_data.get('rows', [])
            if len(rows) < 2:
                table_warnings.append((q.get('question_id'), len(rows)))

    if table_warnings:
        print(f"\n  {YELLOW}⚠️  WARNINGS (проверь вручную):{RESET}")
        for qid, row_count in table_warnings:
            print(f"     {YELLOW}Вопрос {qid}: таблица имеет только {row_count} строк — убедись что это полная таблица из PDF{RESET}")

    # ========== SAVE FIXES ==========
    if modified and auto_fix:
        backup = backup_file(filepath)
        print(f"\n  {CYAN}💾 Backup создан: {backup}{RESET}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  {CYAN}💾 Файл сохранён с исправлениями{RESET}")
    
    # ========== SUMMARY ==========
    total = results['passed'] + results['failed']
    pct = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"\n  {BOLD}Результат: {results['passed']}/{total} ({pct:.0f}%){RESET}")
    if results['fixed'] > 0:
        print(f"  {CYAN}Авто-исправлено: {results['fixed']} проблем{RESET}")
    
    if results['failed'] == 0:
        print(f"  {GREEN}{BOLD}✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ{RESET}")
    else:
        print(f"  {RED}{BOLD}✗ {results['failed']} ПРОВЕРОК НЕ ПРОЙДЕНО{RESET}")
        if results['manual_fixes']:
            print(f"\n  {YELLOW}{BOLD}ТРЕБУЕТСЯ РУЧНОЕ ИСПРАВЛЕНИЕ:{RESET}")
            for i, fix in enumerate(results['manual_fixes'][:10], 1):
                print(f"  {i}. {fix}")
    
    return results


def main():
    if len(sys.argv) < 2:
        print(f"""
{BOLD}QBANK Validator v1.0{RESET}

Использование:
  python validate_qbank.py <file.json>           # Только проверка
  python validate_qbank.py <file.json> --fix     # Проверка + авто-исправление

Примеры:
  python validate_qbank.py qbank_module_1.json
  python validate_qbank.py qbank_module_2.json --fix

Авто-исправляет:
  ✓ total_questions (пересчитывает)
  ✓ Дублирующиеся question_id (добавляет суффикс)
  ✓ has_table=true без table_data (ставит false)
  ✓ requires_calculator=true без keystrokes (ставит false)

Требует ручного исправления:
  ✗ JSON синтаксис
  ✗ Пустые поля (question_text, explanation, options)
  ✗ Недостающие переводы EN/RU
  ✗ Неправильный correct_option_id
        """)
        sys.exit(1)
    
    filepath = sys.argv[1]
    auto_fix = '--fix' in sys.argv
    
    if auto_fix:
        print(f"{CYAN}Режим авто-исправления включён{RESET}")
    
    results = validate_qbank(filepath, auto_fix)
    
    print()
    if results['failed'] == 0:
        print(f"{GREEN}{BOLD}═══ QBANK ВАЛИДАЦИЯ ПРОЙДЕНА ═══{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}═══ ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ ═══{RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
