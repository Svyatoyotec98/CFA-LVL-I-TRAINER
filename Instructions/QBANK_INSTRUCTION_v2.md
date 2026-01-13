# QBANK_INSTRUCTION.md
# Инструкция по созданию JSON тестов из PDF QBank

**Версия:** 2.0 (с чекпоинтами)  
**Дата:** 13 января 2026

---

## ⚠️ КРИТИЧЕСКИ ВАЖНО: СИСТЕМА ЧЕКПОИНТОВ

**Проблема:** Создание полного JSON за один раз приводит к зависаниям.

**Решение:** Работа разбита на 4 чекпоинта. После каждого — коммит, пуш, ожидание подтверждения.

### ЧЕКПОИНТ 1: Извлечение сырого текста (5-10 мин)
```
Задача: Извлечь текст из PDF → сохранить в .txt
Результат: Materials/QBank/{Book}/extracted/{chapter}_raw.txt
Коммит: "CHECKPOINT 1: Extract raw text from {chapter}"
```

### ЧЕКПОИНТ 2: Нарезка на вопросы (5-10 мин)
```
Задача: Разбить текст на отдельные вопросы (грубая нарезка)
Результат: Materials/QBank/{Book}/extracted/{chapter}_split.json
Формат: [{"number": "Q.13", "raw_text": "..."}, ...]
Коммит: "CHECKPOINT 2: Split into {N} questions"
```

### ЧЕКПОИНТ 3: Первые 10-15 вопросов в финальном формате (15-20 мин)
```
Задача: Оформить первые 10-15 вопросов по полной структуре
Результат: frontend/data/qbank/{book}_ch{chapter}_questions.json (частичный)
Коммит: "CHECKPOINT 3: Format questions 1-15"
```

### ЧЕКПОИНТ 4: Остальные вопросы + интеграция в систему (20-30 мин)
```
Задача A: Оформить оставшиеся вопросы, валидация
Результат: frontend/data/qbank/{book}_ch{chapter}_questions.json (полный)
Коммит: "CHECKPOINT 4: Complete {chapter} QBank - {N} questions total"

Задача B: Интегрировать модуль в book{N}.json
Результат: frontend/data/books/book{N}.json (обновлен с новым модулем)
Коммит: "Add Module {X} to Book {N}"
```

---

## ПРОЦЕСС РАБОТЫ

### Шаг 0: Подготовка
```bash
# Создать ветку для работы
git checkout -b qbank/{book_code}-ch{chapter}

# Создать папку для промежуточных файлов
mkdir -p Materials/QBank/{Book}/extracted
```

---

### ЧЕКПОИНТ 1: Извлечение текста

**Вход:** PDF файл  
**Выход:** `{chapter}_raw.txt`

```python
import pdfplumber

def extract_text(pdf_path, output_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n\n"
            
            # Извлечь таблицы отдельно
            tables = page.extract_tables()
            for table in tables:
                text += "[TABLE]\n"
                for row in table:
                    text += " | ".join(str(cell) for cell in row) + "\n"
                text += "[/TABLE]\n\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return len(text)
```

**После выполнения:**
```bash
git add Materials/QBank/{Book}/extracted/{chapter}_raw.txt
git commit -m "CHECKPOINT 1: Extract raw text from {chapter}"
git push -u origin qbank/{book_code}-ch{chapter}
```

**⏸️ СТОП — жду подтверждения от пользователя**

---

### ЧЕКПОИНТ 2: Нарезка на вопросы

**Вход:** `{chapter}_raw.txt`  
**Выход:** `{chapter}_split.json`

```python
import re
import json

def split_questions(raw_text_path, output_path):
    with open(raw_text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Паттерн для поиска вопросов (Q.13, Q.770, etc.)
    pattern = r'(Q\.\d+.*?)(?=Q\.\d+|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    questions = []
    for match in matches:
        # Извлечь номер вопроса
        num_match = re.search(r'Q\.(\d+)', match)
        if num_match:
            questions.append({
                "number": f"Q.{num_match.group(1)}",
                "raw_text": match.strip()
            })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    return len(questions)
```

**После выполнения:**
```bash
git add Materials/QBank/{Book}/extracted/{chapter}_split.json
git commit -m "CHECKPOINT 2: Split into {N} questions"
git push
```

**⏸️ СТОП — жду подтверждения от пользователя**

---

### ЧЕКПОИНТ 3: Первые 10-15 вопросов

**Вход:** `{chapter}_split.json`  
**Выход:** Частичный `{book}_ch{chapter}_questions.json`

**Обрабатывать только вопросы 1-15!**

Для каждого вопроса создать структуру:

```json
{
  "question_id": "Q-{BOOK}-{CH}-{NUM}",
  "original_number": "Q.{NUM}",
  "los_id": "LOS_{X}{letter}",
  "los_reference": "LOS ({letter}): ...",
  "difficulty": "EASY|MEDIUM|HARD",
  "requires_calculation": true|false,
  "topic_tags": ["tag1", "tag2"],
  
  "question_text": "...",
  "question_text_ru": "...",
  
  "has_table": false,
  "table_data": null,
  
  "options": [
    {"option_id": "opt1", "text": "...", "text_ru": "..."},
    {"option_id": "opt2", "text": "...", "text_ru": "..."},
    {"option_id": "opt3", "text": "...", "text_ru": "..."}
  ],
  "correct_option_id": "opt1",
  
  "explanation": {
    "main": "...",
    "main_ru": "...",
    "formula": "...",
    "formula_latex": "...",
    "solution_steps": ["..."],
    "wrong_answers": {...},
    "calculator_steps": {...}
  }
}
```

**После выполнения:**
```bash
git add frontend/data/qbank/{book}_ch{chapter}_questions.json
git commit -m "CHECKPOINT 3: Format questions 1-15"
git push
```

**⏸️ СТОП — жду подтверждения от пользователя**

---

### ЧЕКПОИНТ 4: Остальные вопросы + ИНТЕГРАЦИЯ В СИСТЕМУ

**Вход:** Частичный JSON + `{chapter}_split.json`
**Выход:**
1. Полный `{book}_ch{chapter}_questions.json`
2. Обновленный `frontend/data/books/book{N}.json` с новым модулем

#### Часть A: Завершить вопросы (15-20 мин)

1. Добавить оставшиеся вопросы (16+)
2. Обновить `total_questions`
3. Валидация JSON

**Валидация:**
```python
import json

def validate_qbank(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    errors = []
    seen_ids = set()

    for q in data['questions']:
        # Проверка уникальности ID
        if q['question_id'] in seen_ids:
            errors.append(f"Duplicate ID: {q['question_id']}")
        seen_ids.add(q['question_id'])

        # Проверка correct_option_id
        option_ids = [o['option_id'] for o in q['options']]
        if q['correct_option_id'] not in option_ids:
            errors.append(f"{q['question_id']}: invalid correct_option_id")

        # Проверка обязательных полей
        required = ['question_text', 'explanation', 'difficulty']
        for field in required:
            if not q.get(field):
                errors.append(f"{q['question_id']}: missing {field}")

    return errors
```

**Коммит после валидации:**
```bash
git add frontend/data/qbank/{book}_ch{chapter}_questions.json
git commit -m "CHECKPOINT 4: Complete {chapter} QBank - {N} questions total"
git push
```

#### Часть B: Интеграция в book{N}.json (5-10 мин)

**⚠️ КРИТИЧНО:** Без этого шага вопросы НЕ появятся во фронтенде!

**Задача:** Добавить новый модуль в `frontend/data/books/book{N}.json`

```python
import json

def integrate_module_to_book(qbank_path, book_path, module_id):
    """
    Интегрирует модуль из qbank в book{N}.json

    Args:
        qbank_path: frontend/data/qbank/book1_ch2_questions.json
        book_path: frontend/data/books/book1.json
        module_id: номер модуля (обычно совпадает с chapter_id)
    """
    # Загрузить qbank и book
    with open(qbank_path, 'r', encoding='utf-8') as f:
        qbank = json.load(f)

    with open(book_path, 'r', encoding='utf-8') as f:
        book = json.load(f)

    # Конвертировать вопросы в формат book
    converted_questions = []
    for q in qbank['questions']:
        # Конвертировать новый формат explanation в старый
        if isinstance(q['explanation'], dict):
            explanation_text = q['explanation'].get('main', '')
            explanation_formula = q['explanation'].get('formula_latex', '')
            calc_steps = q['explanation'].get('calculator_steps', {})
            if isinstance(calc_steps, dict):
                calc_steps = calc_steps.get('keystrokes', [])
        else:
            explanation_text = q['explanation']
            explanation_formula = None
            calc_steps = None

        converted_q = {
            'question_id': q['question_id'],
            'question_number': int(q['original_number'].replace('Q.', '')),
            'question_text': q['question_text'],
            'question_text_ru': q.get('question_text_ru', ''),
            'question_text_formula': None,
            'question_continuation': None,
            'has_table': q.get('has_table', False),
            'table_data': q.get('table_data'),
            'options': q['options'],
            'correct_option_id': q['correct_option_id'],
            'explanation': explanation_text,
            'explanation_ru': '',
            'explanation_formula': explanation_formula,
            'explanation_wrong': q['explanation'].get('wrong_answers', {}) if isinstance(q['explanation'], dict) else {},
            'requires_calculation': q.get('requires_calculation', False),
            'calculator_steps': calc_steps,
            'difficulty': q.get('difficulty', 'MEDIUM'),
            'los_reference': q.get('los_id', ''),
            'topic_tags': q.get('topic_tags', [])
        }
        converted_questions.append(converted_q)

    # Создать новый модуль
    new_module = {
        'module_id': module_id,
        'module_name': qbank['chapter_name'],
        'module_name_ru': qbank.get('chapter_name_ru', ''),
        'los_covered': list(set([q.get('los_id', '') for q in qbank['questions'] if q.get('los_id')])),
        'questions': converted_questions
    }

    # Проверить, что модуль еще не существует
    existing_modules = {m['module_id'] for m in book['learning_modules']}
    if module_id in existing_modules:
        print(f"⚠️ Module {module_id} already exists! Replacing...")
        book['learning_modules'] = [m for m in book['learning_modules'] if m['module_id'] != module_id]
        book['total_questions'] -= len([q for m in book['learning_modules'] if m['module_id'] == module_id for q in m['questions']])

    # Добавить модуль
    book['learning_modules'].append(new_module)
    book['total_questions'] += len(converted_questions)

    # Сохранить обновленный book
    with open(book_path, 'w', encoding='utf-8') as f:
        json.dump(book, f, indent=2, ensure_ascii=False)

    print(f"✓ Added Module {module_id} with {len(converted_questions)} questions")
    print(f"✓ Total questions in book: {book['total_questions']}")
    return True

# Пример использования:
integrate_module_to_book(
    'frontend/data/qbank/book1_ch2_questions.json',
    'frontend/data/books/book1.json',
    module_id=2
)
```

**Финальный коммит:**
```bash
git add frontend/data/books/book{N}.json
git commit -m "Add Module {X} ({ModuleName}) to Book {N}

- Integrated {N} questions into book{N}.json
- Module now visible in frontend
- Total book questions: {total}"
git push
```

**✅ ГОТОВО — merge в main**

---

## ЦЕЛЬ

Создать JSON файл с тестовыми вопросами из PDF QBank одной главы CFA Level 1.

**Ключевые требования:**
- Полное извлечение контента (таблицы, формулы, символы)
- Shuffle вариантов ответов (без букв A/B/C)
- Полные объяснения с пагинацией для длинных
- Калькуляторные инструкции BA II Plus для вычислительных задач

---

## ВХОДНЫЕ ДАННЫЕ

**Расположение PDF файлов:**
```
Materials/QBank/{Book_Name}/Chapters/{chapter_file}.pdf
```

**Пример:**
```
Materials/QBank/Quants/Chapters/Copy_of_CH-1-Quantitative_Methods-Answers-3-39.pdf
```

---

## ВЫХОДНЫЕ ДАННЫЕ

**Расположение JSON файлов:**
```
frontend/data/qbank/{book_id}_ch{chapter_id}_questions.json
```

**Пример:**
```
frontend/data/qbank/book1_ch1_questions.json
```

---

## СТРУКТУРА JSON ФАЙЛА

```json
{
  "book_id": 1,
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  "chapter_id": 1,
  "chapter_name": "Rate and Return",
  "chapter_name_ru": "Ставки и доходности",
  "total_questions": 35,
  
  "questions": [...]
}
```

---

## ПРАВИЛА ИЗВЛЕЧЕНИЯ ВОПРОСОВ

### 1. Идентификация вопроса

**Обязательные поля из PDF:**
- `original_number` — номер вопроса (Q.13, Q.770, и т.д.)
- `question_text` — полный текст вопроса
- `options` — все варианты ответов
- `correct_option_id` — какой вариант правильный
- `explanation` — полное объяснение из PDF
- `los_reference` — ссылка на LOS (обычно в конце объяснения)

### 2. Таблицы (КРИТИЧНО!)

**Если в вопросе есть таблица:**
```json
{
  "has_table": true,
  "table_data": {
    "headers": ["Column1", "Column2", ...],
    "rows": [
      ["value1", "value2", ...],
      ["value3", "value4", ...]
    ],
    "caption": "Optional caption"
  }
}
```

**Правила извлечения таблиц:**
- Использовать pdfplumber для извлечения
- Проверять, что все ячейки заполнены
- Числа сохранять как строки с форматированием ("$7,945,600")
- Отрицательные значения в скобках: "($1,750,000)"

### 3. Варианты ответов (БЕЗ БУКВ!)

**В JSON хранить без A/B/C:**
```json
"options": [
  {"option_id": "opt1", "text": "First option"},
  {"option_id": "opt2", "text": "Second option"},
  {"option_id": "opt3", "text": "Third option"}
]
```

### 4. Объяснения (ПОЛНЫЕ!)

**Структура explanation:**
```json
{
  "main": "Основное объяснение правильного ответа",
  "main_ru": "Перевод на русский",
  
  "formula": "Формула текстом",
  "formula_latex": "Формула в LaTeX",
  
  "solution_steps": ["Шаг 1", "Шаг 2", ...],
  
  "wrong_answers": {
    "opt1": {
      "reason": "Почему opt1 неверен",
      "reason_ru": "Перевод",
      "calculation": "Какой расчёт даёт этот неверный ответ"
    }
  },
  
  "calculator_steps": {...}
}
```

### 5. Калькуляторные инструкции

**Когда добавлять `calculator_steps`:**
- `requires_calculation: true`
- Вопрос содержит TVM расчёты (PV, FV, N, I/Y, PMT)
- Вопрос содержит IRR/NPV расчёты
- Вопрос требует статистических расчётов

**Структура:**
```json
"calculator_steps": {
  "applicable": true,
  "calculator_model": "BA II Plus Professional",
  "method": "TVM Worksheet | Cash Flow Worksheet | Statistics | Direct",
  "preparation": ["Подготовительные шаги"],
  "keystrokes": ["Последовательность нажатий"],
  "display_result": "Что покажет дисплей",
  "alternative_method": {...},
  "note": "Дополнительные пояснения"
}
```

### 6. Difficulty

- **EASY**: Концептуальный вопрос, один шаг расчёта
- **MEDIUM**: 2-3 шага расчёта, стандартное применение формулы
- **HARD**: Многошаговый расчёт, таблицы, несколько концепций

### 7. Topic Tags

Добавлять релевантные теги:
- Тип расчёта: `FV`, `PV`, `HPR`, `TWRR`, `MWRR`, `IRR`, `NPV`
- Концепции: `compounding`, `arithmetic mean`, `geometric mean`
- Характеристики: `table`, `conceptual`, `multi-year`

---

## NAMING CONVENTIONS

### question_id
```
Q-{BOOK}-{CHAPTER}-{ORIGINAL_NUMBER}

Примеры:
Q-QM-1-013    (Quantitative Methods, Chapter 1, Q.13)
Q-QM-1-770    (Quantitative Methods, Chapter 1, Q.770)
Q-FI-3-045    (Fixed Income, Chapter 3, Q.45)
```

### option_id
```
opt1, opt2, opt3, opt4  (НЕ A, B, C, D!)
```

### Book Codes
| Book | Code |
|------|------|
| Quantitative Methods | QM |
| Economics | EC |
| Financial Statement Analysis | FSA |
| Corporate Issuers | CI |
| Equity Investments | EQ |
| Fixed Income | FI |
| Derivatives | DER |
| Alternative Investments | ALT |
| Portfolio Management | PM |
| Ethics | ETH |

---

## ЧЕКЛИСТ ПЕРЕД ЗАВЕРШЕНИЕМ

### Контент
- [ ] Все вопросы из PDF извлечены
- [ ] Таблицы корректно парсятся
- [ ] Формулы сохранены в двух форматах
- [ ] Объяснения полные (не обрезаны)

### Структура
- [ ] question_id уникальны
- [ ] option_id без букв (opt1, opt2, opt3)
- [ ] correct_option_id указывает на правильный вариант
- [ ] difficulty присвоен каждому вопросу

### Калькулятор
- [ ] requires_calculation установлен корректно
- [ ] calculator_steps добавлены для вычислительных задач

### Валидация
- [ ] JSON валиден
- [ ] Все ссылки на option_id существуют
