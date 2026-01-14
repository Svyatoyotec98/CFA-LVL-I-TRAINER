# QBANK_INSTRUCTION_v3.md
# Инструкция по созданию JSON тестов из AnalystPrep PDF QBank

**Версия:** 3.0 (исправлена под реальную структуру Module 1)
**Дата:** 14 января 2026

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

## 🗂️ РАСПОЛОЖЕНИЕ ФАЙЛОВ

### Входные PDF:
```
Materials/QBank/Tests/{Book_Name}/Chapters/{chapter_file}.pdf
```

**Пример:**
```
Materials/QBank/Tests/Quants/Chapters/Copy of CH-1-Quantitative_Methods-Answers-40-75.pdf
```

### Промежуточные файлы:
```
Materials/QBank/{Book_Name}/extracted/{chapter}_raw.txt
Materials/QBank/{Book_Name}/extracted/{chapter}_split.json
```

### Выходной JSON:
```
frontend/data/qbank/{book}_ch{chapter}_questions.json
```

**Пример:**
```
frontend/data/qbank/book1_ch1_questions.json
```

---

## 📐 СТРУКТУРА JSON (РЕАЛЬНАЯ из Module 1)

### Внешний уровень файла:
```json
{
  "book_id": 1,
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  "chapter_id": 1,
  "chapter_name": "Rate and Return",
  "chapter_name_ru": "Ставки и доходности",
  "total_questions": 26,
  "questions": [...]
}
```

### Структура одного вопроса (⚠️ ПЛОСКАЯ, НЕ ВЛОЖЕННАЯ!):

```json
{
  "question_id": "QM-1-013",
  "question_number": 13,
  "question_text": "A bank offers you a Certificate of Deposit...",
  "question_text_ru": "Банк предлагает...",
  "question_text_formula": null,
  "question_continuation": null,
  "has_table": false,
  "table_data": null,

  "options": [
    {"id": "opt1", "text": "$188,956.80"},
    {"id": "opt2", "text": "$189,797.85"},
    {"id": "opt3", "text": "$190,236.27"}
  ],
  "correct_option_id": "opt3",

  "explanation": "FV with quarterly compounding: FV = PV[1 + rs/m]^(mN) = $150,000[1 + 0.08/4]^12 = $190,236.27",
  "explanation_ru": "FV с квартальным начислением.",
  "explanation_formula": "$FV_N = PV \\left[1 + \\frac{r_s}{m}\\right]^{mN} = \\$150,000 \\left[1 + \\frac{0.08}{4}\\right]^{12} = \\$190,236.27$",
  "explanation_wrong": {
    "opt1": {
      "text": "FV with annual compounding instead of quarterly.",
      "formula": "$FV = \\$150,000(1.08)^3 = \\$188,956.80$"
    },
    "opt2": {
      "text": "FV with semi-annual compounding.",
      "formula": "$FV = \\$150,000(1.04)^6 = \\$189,797.85$"
    }
  },

  "requires_calculation": true,
  "calculator_steps": [
    "[2ND] [CLR TVM]",
    "[2ND] [P/Y] 4 [ENTER]",
    "[2ND] [QUIT]",
    "150000 [+/-] [PV]",
    "8 [I/Y]",
    "12 [N]",
    "0 [PMT]",
    "[CPT] [FV] → 190,236.27"
  ],

  "difficulty": "MEDIUM",
  "los_reference": "LOS 1d",
  "topic_tags": ["FV", "compounding", "quarterly", "TVM"]
}
```

---

## 🎯 КЛЮЧЕВЫЕ ОТЛИЧИЯ ОТ v2

### ❌ v2 (НЕПРАВИЛЬНО):
```json
"options": [
  {"option_id": "opt1", "text": "...", "text_ru": "..."}
],
"explanation": {
  "main": "...",
  "formula_latex": "...",
  "wrong_answers": {...}
},
"calculator_steps": {
  "applicable": true,
  "keystrokes": ["..."]
}
```

### ✅ v3 (ПРАВИЛЬНО как Module 1):
```json
"options": [
  {"id": "opt1", "text": "..."}
],
"explanation": "Short text with calculation",
"explanation_formula": "$LaTeX here$",
"explanation_wrong": {
  "opt1": {"text": "...", "formula": "..."}
},
"calculator_steps": ["[2ND] [CLR TVM]", "..."]
```

---

## 📄 ФОРМАТ AnalystPrep PDF

### Структура вопросов в PDF:

```
Q.8
If you invest $100,000 currently in a project paying an 8% interest
rate compounded annually, the amount of the investment after three
years is closest to:

The correct answer is C.     ← ОТВЕТ ИДЕТ ПЕРВЫМ!

The question requires the calculation of the future value...
[Explanation text]

A is incorrect. It represents...
B is incorrect. The calculation...

A. $108,000.00     ← ОПЦИИ ИДУТ ПОСЛЕ!
B. $108,215.23
C. $125,971.20

[Formulas разбиты построчно]
F
V
=
P
V
[
1
+
]
N
```

### ⚠️ ВАЖНО: Порядок парсинга для AnalystPrep

1. **Question text** — от "Q.X" до "The correct answer is"
2. **Correct answer** — извлечь букву после "The correct answer is"
3. **Explanation** — от answer letter до "A is incorrect" или до options
4. **Options A/B/C** — в конце блока
5. **Formulas** — разбросаны, могут быть построчно разбиты

---

## 🔧 ПРОЦЕСС РАБОТЫ

### Шаг 0: Подготовка
```bash
# Создать ветку для работы
git checkout -b qbank/{book_code}-ch{chapter}

# Создать папку для промежуточных файлов
mkdir -p Materials/QBank/{Book}/extracted
```

---

### ЧЕКПОИНТ 1: Извлечение текста

**Вход:** PDF из `Materials/QBank/Tests/{Book}/Chapters/`
**Выход:** `Materials/QBank/{Book}/extracted/{chapter}_raw.txt`

```python
import pdfplumber

def extract_text(pdf_path, output_path):
    """Извлекает текст из PDF"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    return len(text)

# Использование:
extract_text(
    'Materials/QBank/Tests/Quants/Chapters/Copy of CH-1-Quantitative_Methods-Answers-40-75.pdf',
    'Materials/QBank/Quants/extracted/ch2_module2_raw.txt'
)
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

def split_questions_analystprep(raw_text_path, output_path):
    """Разбивает AnalystPrep текст на отдельные вопросы"""
    with open(raw_text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Паттерн для поиска вопросов (Q.8, Q.13, etc.)
    pattern = r'(Q\.\d+\s+.*?)(?=Q\.\d+\s+|$)'
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
**Выход:** Частичный `frontend/data/qbank/{book}_ch{chapter}_questions.json`

**Обрабатывать только вопросы 1-15!**

#### Парсинг одного вопроса (AnalystPrep формат):

```python
import re

def parse_analystprep_question(raw_text, question_num, book_code, chapter_id):
    """
    Парсит один вопрос из AnalystPrep формата

    Порядок в PDF:
    1. Question text
    2. "The correct answer is X"
    3. Explanation
    4. Options A/B/C
    """

    # 1. Извлечь question text (до "The correct answer is")
    q_match = re.search(
        r'Q\.\d+\s+(.*?)(?=The\s+correct\s+answer\s+is)',
        raw_text,
        re.DOTALL | re.IGNORECASE
    )
    question_text = q_match.group(1).strip() if q_match else ""

    # Очистить question_text от артефактов
    question_text = re.sub(r'\s+', ' ', question_text)  # Убрать лишние пробелы
    question_text = re.sub(r':\s*$', ':', question_text)  # Оставить двоеточие в конце

    # 2. Извлечь правильный ответ
    ans_match = re.search(
        r'The\s+correct\s+answer\s+is\s+([A-C])',
        raw_text,
        re.IGNORECASE
    )
    correct_letter = ans_match.group(1) if ans_match else "A"

    # 3. Извлечь опции (в конце текста)
    options_pattern = r'([A-C])\.\s*\$?([\d,\.]+(?:\s+[A-Za-z]+)?)'
    option_matches = re.findall(options_pattern, raw_text)

    options = []
    for letter, text in option_matches[:3]:  # Только первые 3
        options.append({
            "id": f"opt{ord(letter) - ord('A') + 1}",
            "text": text.strip()
        })

    # Определить correct_option_id
    correct_option_id = f"opt{ord(correct_letter) - ord('A') + 1}"

    # 4. Извлечь explanation (между answer и "A is incorrect")
    expl_match = re.search(
        r'The\s+correct\s+answer\s+is\s+[A-C]\.\s+(.*?)(?=A\s+is\s+incorrect|B\s+is\s+incorrect|$)',
        raw_text,
        re.DOTALL | re.IGNORECASE
    )
    explanation = expl_match.group(1).strip() if expl_match else ""
    explanation = re.sub(r'\s+', ' ', explanation)

    # 5. Извлечь формулы (если есть LaTeX-подобный текст)
    formula_match = re.search(r'(FV|PV|NPV|IRR)[\s=]+.*?\d', explanation)
    explanation_formula = None
    if formula_match:
        # Конвертировать в LaTeX (упрощенно)
        explanation_formula = f"${formula_match.group(0)}$"

    # 6. Извлечь explanation_wrong
    explanation_wrong = {}
    for opt in options:
        if opt["id"] != correct_option_id:
            letter = chr(ord('A') + int(opt["id"][-1]) - 1)
            wrong_match = re.search(
                rf'{letter}\s+is\s+incorrect\.(.*?)(?=[A-C]\s+is\s+incorrect|$)',
                raw_text,
                re.DOTALL | re.IGNORECASE
            )
            if wrong_match:
                explanation_wrong[opt["id"]] = {
                    "text": re.sub(r'\s+', ' ', wrong_match.group(1).strip()[:100]),
                    "formula": ""
                }

    # 7. Создать структуру вопроса
    question = {
        "question_id": f"{book_code}-{chapter_id}-{str(question_num).zfill(3)}",
        "question_number": question_num,
        "question_text": question_text,
        "question_text_ru": "",
        "question_text_formula": None,
        "question_continuation": None,
        "has_table": False,
        "table_data": None,
        "options": options,
        "correct_option_id": correct_option_id,
        "explanation": explanation[:200],  # Первые 200 символов
        "explanation_ru": "",
        "explanation_formula": explanation_formula,
        "explanation_wrong": explanation_wrong,
        "requires_calculation": bool(formula_match),
        "calculator_steps": [],
        "difficulty": "MEDIUM",
        "los_reference": "",
        "topic_tags": []
    }

    return question
```

**После выполнения:**
```bash
git add frontend/data/qbank/{book}_ch{chapter}_questions.json
git commit -m "CHECKPOINT 3: Format questions 1-15"
git push
```

**⏸️ СТОП — жду подтверждения от пользователя**

---

### ЧЕКПОИНТ 4: Завершение

#### Часть A: Оставшиеся вопросы

1. Обработать вопросы 16+ тем же способом
2. Обновить `total_questions`
3. Валидация JSON

**Валидация:**
```python
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
        option_ids = [o['id'] for o in q['options']]
        if q['correct_option_id'] not in option_ids:
            errors.append(f"{q['question_id']}: invalid correct_option_id")

        # Проверка "The correct answer is" в question_text
        if 'correct answer' in q['question_text'].lower():
            errors.append(f"{q['question_id']}: dirty question_text")

    return errors
```

**Коммит:**
```bash
git add frontend/data/qbank/{book}_ch{chapter}_questions.json
git commit -m "CHECKPOINT 4: Complete {chapter} QBank - {N} questions total"
git push
```

#### Часть B: Интеграция в book{N}.json

**⚠️ КРИТИЧНО:** Без этого шага вопросы НЕ появятся во фронтенде!

```python
import json

def integrate_module_to_book(qbank_path, book_path, module_id):
    """Интегрирует модуль из qbank в book{N}.json"""

    # Загрузить qbank и book
    with open(qbank_path, 'r', encoding='utf-8') as f:
        qbank = json.load(f)

    with open(book_path, 'r', encoding='utf-8') as f:
        book = json.load(f)

    # Создать новый модуль (вопросы уже в правильном формате!)
    new_module = {
        'module_id': module_id,
        'module_name': qbank['chapter_name'],
        'module_name_ru': qbank.get('chapter_name_ru', ''),
        'los_covered': list(set([q.get('los_reference', '') for q in qbank['questions'] if q.get('los_reference')])),
        'questions': qbank['questions']  # Копируем как есть!
    }

    # Проверить, что модуль еще не существует
    existing_ids = {m['module_id'] for m in book['learning_modules']}
    if module_id in existing_ids:
        print(f"⚠️ Module {module_id} already exists! Replacing...")
        book['learning_modules'] = [m for m in book['learning_modules'] if m['module_id'] != module_id]

    # Добавить модуль
    book['learning_modules'].append(new_module)
    book['total_questions'] = sum(len(m['questions']) for m in book['learning_modules'])

    # Сохранить
    with open(book_path, 'w', encoding='utf-8') as f:
        json.dump(book, f, indent=2, ensure_ascii=False)

    print(f"✓ Added Module {module_id} with {len(qbank['questions'])} questions")
    print(f"✓ Total questions in book: {book['total_questions']}")
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

## ✅ ЧЕКЛИСТ КАЧЕСТВА

### Контент
- [ ] question_text БЕЗ "The correct answer is"
- [ ] options БЕЗ формул (только чистые значения)
- [ ] explanation полное (не обрезано)
- [ ] Все вопросы из PDF извлечены

### Структура
- [ ] options используют "id" (НЕ "option_id")
- [ ] explanation — строка (НЕ объект)
- [ ] explanation_formula — отдельное поле с LaTeX
- [ ] explanation_wrong — отдельное поле на верхнем уровне
- [ ] calculator_steps — массив строк (НЕ объект)
- [ ] question_id формата "QM-1-013" (БЕЗ префикса "Q-")

### Валидация
- [ ] JSON валиден
- [ ] Все correct_option_id существуют
- [ ] Нет дубликатов question_id
- [ ] Модуль интегрирован в book{N}.json

---

## 📋 NAMING CONVENTIONS

### question_id
```
{BOOK_CODE}-{CHAPTER}-{NUM}

Примеры:
QM-1-013    (Quantitative Methods, Chapter 1, Q.13)
QM-1-770    (Quantitative Methods, Chapter 1, Q.770)
FI-3-045    (Fixed Income, Chapter 3, Q.45)
```

### option_id
```
opt1, opt2, opt3  (НЕ A, B, C!)
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

## 🎯 ИТОГ

Эта инструкция основана на **реальной структуре Module 1**, которая работает отлично.

**Ключевые принципы:**
1. ✅ Плоская структура данных (не вложенная)
2. ✅ Правильные пути к PDF (`Materials/QBank/Tests/...`)
3. ✅ Парсинг под AnalystPrep формат (answer-first)
4. ✅ Чекпоинты для избежания зависаний
5. ✅ Интеграция в book{N}.json обязательна

Следуя этой инструкции, вы получите качество как у Module 1.
