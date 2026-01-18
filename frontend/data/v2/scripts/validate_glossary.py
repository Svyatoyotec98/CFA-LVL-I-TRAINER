#!/usr/bin/env python3
"""
GLOSSARY Validator v1.0
Проверяет и исправляет JSON файлы глоссария

Использование:
  python validate_glossary.py glossary_module_1.json          # Только проверка
  python validate_glossary.py glossary_module_1.json --fix    # Проверка + авто-исправление
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


def validate_glossary(filepath: str, auto_fix: bool = False) -> Dict:
    """Полная валидация файла глоссария"""
    
    results = {
        'file': filepath,
        'checks': [],
        'passed': 0,
        'failed': 0,
        'fixed': 0,
        'manual_fixes': []
    }
    
    print_header(f"GLOSSARY: {os.path.basename(filepath)}")
    
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
    required_meta = ['book_id', 'book_code', 'module_id', 'module_name', 'module_name_ru', 'total_terms']
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
    
    # ========== CHECK 4: LOS array exists ==========
    has_los = 'los' in data and isinstance(data['los'], list)
    results['checks'].append(('LOS массив существует', has_los, ""))
    print_result('LOS массив существует', has_los)
    
    if not has_los:
        results['failed'] += 1
        results['manual_fixes'].append("Добавь массив 'los' с терминами")
        print_manual("Добавь структуру: \"los\": [{\"los_id\": \"LOS_1a\", \"terms\": [...]}]")
        return results
    results['passed'] += 1
    
    # ========== CHECK 5: Minimum terms count ==========
    total_terms = 0
    for los in data['los']:
        if 'terms' in los:
            total_terms += len(los['terms'])
    
    min_terms = 10
    terms_ok = total_terms >= min_terms
    results['checks'].append((f'Минимум терминов (>={min_terms})', terms_ok, f"Found: {total_terms}"))
    print_result(f'Минимум терминов (>={min_terms})', terms_ok, f"Found: {total_terms}")
    
    if terms_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
        results['manual_fixes'].append(f"Слишком мало терминов ({total_terms}). Добавь ещё из исходного материала.")
        print_manual(f"Только {total_terms} терминов. Вернись к исходному PDF и добавь недостающие.")
    
    # ========== CHECK 6: Required term fields ==========
    required_term_fields = ['term_id', 'term_en', 'term_ru', 'definition_en', 'definition_ru']
    terms_issues = []
    
    for los in data['los']:
        for term in los.get('terms', []):
            for field in required_term_fields:
                if field not in term or not term[field]:
                    terms_issues.append((term.get('term_id', 'UNKNOWN'), field))
    
    terms_fields_ok = len(terms_issues) == 0
    details = f"{len(terms_issues)} issues" if not terms_fields_ok else ""
    results['checks'].append(('Термины: обязательные поля', terms_fields_ok, details))
    print_result('Термины: обязательные поля', terms_fields_ok, details)
    
    if terms_fields_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
        for term_id, field in terms_issues[:5]:  # Показываем первые 5
            results['manual_fixes'].append(f"Заполни {field} для термина {term_id}")
            print_manual(f"Термин {term_id}: заполни поле '{field}'")
        if len(terms_issues) > 5:
            print(f"         {YELLOW}... и ещё {len(terms_issues) - 5} проблем{RESET}")
    
    # ========== CHECK 7: Unique term IDs ==========
    all_term_ids = []
    for los in data['los']:
        for term in los.get('terms', []):
            all_term_ids.append(term.get('term_id'))
    
    duplicates = list(set([tid for tid in all_term_ids if all_term_ids.count(tid) > 1]))
    unique_ok = len(duplicates) == 0
    
    results['checks'].append(('Уникальные term_id', unique_ok, f"Duplicates: {duplicates}" if not unique_ok else ""))
    print_result('Уникальные term_id', unique_ok, f"Duplicates: {duplicates}" if not unique_ok else "")
    
    if unique_ok:
        results['passed'] += 1
    else:
        if auto_fix:
            # AUTO-FIX: Переименовать дубликаты
            seen = {}
            for los in data['los']:
                for term in los.get('terms', []):
                    tid = term.get('term_id')
                    if tid in seen:
                        seen[tid] += 1
                        new_id = f"{tid}_{seen[tid]}"
                        term['term_id'] = new_id
                        print_fix(f"Переименован {tid} → {new_id}")
                    else:
                        seen[tid] = 1
            modified = True
            results['fixed'] += 1
        else:
            results['failed'] += 1
            results['manual_fixes'].append(f"Исправь дублирующиеся term_id: {duplicates}")
            print_manual(f"Переименуй дубликаты: {duplicates}")
    
    # ========== CHECK 8: total_terms matches ==========
    declared_total = data['metadata'].get('total_terms', 0)
    count_match = declared_total == total_terms
    
    results['checks'].append(('total_terms совпадает', count_match, 
                             f"Declared: {declared_total}, Actual: {total_terms}"))
    print_result('total_terms совпадает', count_match, 
                f"Declared: {declared_total}, Actual: {total_terms}")
    
    if count_match:
        results['passed'] += 1
    else:
        if auto_fix:
            # AUTO-FIX: Исправить total_terms
            data['metadata']['total_terms'] = total_terms
            print_fix(f"total_terms: {declared_total} → {total_terms}")
            modified = True
            results['fixed'] += 1
        else:
            results['failed'] += 1
            results['manual_fixes'].append(f"Исправь total_terms: {declared_total} → {total_terms}")
            print_manual(f"Измени total_terms с {declared_total} на {total_terms}")
    
    # ========== CHECK 9: EN/RU definitions differ ==========
    copy_paste_issues = []
    for los in data['los']:
        for term in los.get('terms', []):
            if term.get('definition_en') == term.get('definition_ru'):
                if term.get('definition_en'):  # Not empty
                    copy_paste_issues.append(term.get('term_id'))
    
    no_copy_paste = len(copy_paste_issues) == 0
    results['checks'].append(('EN/RU определения различаются', no_copy_paste,
                             f"Same text: {copy_paste_issues[:3]}" if not no_copy_paste else ""))
    print_result('EN/RU определения различаются', no_copy_paste,
                f"Same text: {copy_paste_issues[:3]}" if not no_copy_paste else "")
    
    if no_copy_paste:
        results['passed'] += 1
    else:
        results['failed'] += 1
        for tid in copy_paste_issues[:3]:
            results['manual_fixes'].append(f"Переведи definition_ru для термина {tid}")
            print_manual(f"Термин {tid}: definition_en == definition_ru (нужен перевод)")
        if len(copy_paste_issues) > 3:
            print(f"         {YELLOW}... и ещё {len(copy_paste_issues) - 3} таких терминов{RESET}")
    
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
{BOLD}GLOSSARY Validator v1.0{RESET}

Использование:
  python validate_glossary.py <file.json>           # Только проверка
  python validate_glossary.py <file.json> --fix     # Проверка + авто-исправление

Примеры:
  python validate_glossary.py glossary_module_1.json
  python validate_glossary.py glossary_module_2.json --fix
        """)
        sys.exit(1)
    
    filepath = sys.argv[1]
    auto_fix = '--fix' in sys.argv
    
    if auto_fix:
        print(f"{CYAN}Режим авто-исправления включён{RESET}")
    
    results = validate_glossary(filepath, auto_fix)
    
    print()
    if results['failed'] == 0:
        print(f"{GREEN}{BOLD}═══ GLOSSARY ВАЛИДАЦИЯ ПРОЙДЕНА ═══{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}═══ ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ ═══{RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
