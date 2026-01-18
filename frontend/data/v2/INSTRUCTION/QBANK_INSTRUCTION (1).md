# QBANK Creation Instruction v2.0

## Обзор задачи

Создание JSON файла с вопросами для CFA Level 1 тренажёра на основе PDF из AnalystPrep QBank.

**ВАЖНО:** Работаем по чекпоинтам. После каждого чекпоинта — git commit. Это снижает риск потери данных при зависании.

---

## 🛠️ ВАЛИДАТОР (ОБЯЗАТЕЛЬНО!)

**Запускай валидатор ПЕРЕД КАЖДЫМ чекпоинтом:**

```bash
python frontend/data/v2/scripts/validate_qbank.py qbank_module_X.json --fix
```

### Что авто-исправляет:
- ✅ `total_questions` (пересчитывает)
- ✅ Дублирующиеся `question_id` (добавляет суффикс)
- ✅ `has_table=true` без `table_data` (ставит false)
- ✅ `requires_calculator=true` без `keystrokes` (ставит false)

### Что требует ручного исправления:
- ❌ JSON синтаксис
- ❌ Пустые поля (question_text, explanation, options)
- ❌ Недостающие переводы EN/RU
- ❌ Неправильный `correct_option_id`

**Workflow каждого чекпоинта:**
```
1. Добавить вопросы
2. python scripts/validate_qbank.py file.json --fix
3. Убедиться что 100% ✓
4. git commit
```

**Путь к валидатору:** `scripts/validate_qbank.py`

---

# ============================================
# ОБНОВИТЬ СЕКЦИЮ ЧЕКПОИНТОВ:
# ============================================

## Чекпоинт 1: Metadata + первые 10 вопросов

1. Создай файл с metadata
2. Добавь вопросы Q001-Q010
3. **ВАЛИДАЦИЯ:** `python scripts/validate_qbank.py qbank_module_X.json --fix`
4. Убедись что 100% ✓
5. **GIT COMMIT:** `git add . && git commit -m "QBank Module X: checkpoint 1 - Q001-Q010"`

## Чекпоинт 2: Вопросы 11-20

1. Добавь вопросы Q011-Q020
2. **ВАЛИДАЦИЯ:** `python scripts/validate_qbank.py qbank_module_X.json --fix`
3. Убедись что 100% ✓
4. **GIT COMMIT:** `git add . && git commit -m "QBank Module X: checkpoint 2 - Q011-Q020"`

## Чекпоинт 3: Вопросы 21-30

1. Добавь вопросы Q021-Q030
2. **ВАЛИДАЦИЯ:** `python scripts/validate_qbank.py qbank_module_X.json --fix`
3. Убедись что 100% ✓
4. **GIT COMMIT:** `git add . && git commit -m "QBank Module X: checkpoint 3 - Q021-Q030"`

## Чекпоинт 4: Финализация

1. Добавь оставшиеся вопросы (Q031+)
2. **ФИНАЛЬНАЯ ВАЛИДАЦИЯ:** `python scripts/validate_qbank.py qbank_module_X.json --fix`
3. Убедись что 100% ✓
4. **GIT COMMIT:** `git add . && git commit -m "QBank Module X: complete - N questions"`
5. **GIT PUSH:** `git push`

---

## 🔄 ОБЯЗАТЕЛЬНО: Обновление meta.json

**После создания qbank файла — ОБЯЗАТЕЛЬНО обнови meta.json книги:**

1. Открой `frontend/data/v2/books/book{N}_{name}/meta.json`
2. Найди нужный модуль по `module_id`
3. Добавь/обнови поле: `"qbank_file": "qbank_module_X.json"`
4. Обнови статус:
   - Если glossary уже есть → `"status": "complete"`
   - Если glossary ещё нет → `"status": "in_progress"`
5. Сохрани файл
6. Включи meta.json в коммит

**Пример изменения:**
```json
{
  "module_id": 3,
  "module_name": "Statistical Measures of Asset Returns",
  "qbank_file": "qbank_module_3.json",  // ← ДОБАВИТЬ
  "glossary_file": "glossary_module_3.json",
  "status": "in_progress"  // ← ОБНОВИТЬ
}
```

**БЕЗ ЭТОГО ШАГА ФРОНТЕНД НЕ УВИДИТ НОВЫЙ QBANK!**

---

## 📊 Статусы модулей в meta.json

| Статус | Значение | Когда ставить |
|--------|----------|---------------|
| `"pending"` | Контент не создан | По умолчанию |
| `"in_progress"` | Частично готов | QBank ИЛИ Glossary создан |
| `"complete"` | Полностью готов | QBank И Glossary оба готовы |

**Правило:** Модули со статусом `pending` НЕ загружаются на фронтенде.

---

## Входные данные

- **PDF файл:** `qbank.pdf` (загружается пользователем)
- **Модуль:** Указывается пользователем (например, "Module 2: Time Value of Money")
- **Book ID:** 1-10 (QM=1, Economics=2, FRA=3, и т.д.)

---

## Выходной файл

**Путь:** `frontend/data/v2/books/book{N}_{name}/module{M}/qbank_module_{M}.json`

**Пример:** `frontend/data/v2/books/book1_quants/module1/qbank_module_1.json`

---

## JSON Schema

```json
{
  "metadata": {
    "book_id": 1,
    "book_code": "QM",
    "book_name": "Quantitative Methods",
    "book_name_ru": "Количественные методы",
    "module_id": 1,
    "module_name": "Rates and Returns",
    "module_name_ru": "Ставки и доходность",
    "total_questions": 36,
    "version": "2.0",
    "source": "AnalystPrep QBank"
  },
  "questions": [...]
}
```

---

## Структура вопроса (ПОЛНАЯ)

```json
{
  "question_id": "QM-1-Q001",
  "original_question_number": 13,
  "los_id": "LOS_1d",
  "question_text_en": "Full question text in English...",
  "question_text_ru": "Полный текст вопроса на русском...",
  "has_table": false,
  "table_data": null,
  "question_continuation_en": null,
  "question_continuation_ru": null,
  "options": [
    {"id": "opt_a", "text_en": "Answer A", "text_ru": "Ответ A"},
    {"id": "opt_b", "text_en": "Answer B", "text_ru": "Ответ B"},
    {"id": "opt_c", "text_en": "Answer C", "text_ru": "Ответ C"}
  ],
  "correct_option_id": "opt_c",
  "explanation_en": "Full explanation in English...",
  "explanation_ru": "Полное объяснение на русском...",
  "explanation_formula": "$LaTeX formula$",
  "explanation_table": null,
  "explanation_wrong": {
    "opt_a": {"text_en": "Why A is wrong", "text_ru": "Почему A неверно"},
    "opt_b": {"text_en": "Why B is wrong", "text_ru": "Почему B неверно"}
  },
  "requires_calculator": true,
  "calculator_keystrokes": {
    "method": "TVM Worksheet",
    "steps_en": ["N = 12", "I/Y = 2", "PV = -150,000", "PMT = 0", "CPT → FV = 190,236.27"],
    "steps_ru": ["N = 12", "I/Y = 2", "PV = -150,000", "PMT = 0", "CPT → FV = 190,236.27"]
  },
  "difficulty": "medium",
  "topic_tags": ["future_value", "compound_interest"]
}
```

---

## Типы вопросов

### Тип 1: Простой вопрос (без таблицы)
```json
{
  "has_table": false,
  "table_data": null,
  "question_continuation_en": null,
  "question_continuation_ru": null
}
```

### Тип 2: Вопрос с таблицей в УСЛОВИИ
Таблица — это входные данные, показывается ПЕРЕД вариантами ответа.

```json
{
  "has_table": true,
  "table_data": {
    "headers": ["Year", "Return (%)"],
    "headers_ru": ["Год", "Доходность (%)"],
    "rows": [
      ["2011", "13"],
      ["2012", "19"],
      ["2013", "-11"]
    ]
  },
  "question_continuation_en": "The holding period return is closest to:",
  "question_continuation_ru": "Доходность за период владения ближе всего к:"
}
```

**ВАЖНО:** `question_continuation` — текст ПОСЛЕ таблицы, ПЕРЕД вариантами ответов.

### Тип 3: Вопрос с таблицей в РЕШЕНИИ (explanation_table)
Таблица — это часть решения, показывается ПОСЛЕ ответа пользователя (спойлер!).

```json
{
  "has_table": false,
  "table_data": null,
  "explanation_table": {
    "headers": ["Time", "Cash Flow"],
    "headers_ru": ["Время", "Денежный поток"],
    "rows": [
      ["Year 0", "-$1,100"],
      ["Year 1", "-$580"],
      ["Year 2", "$1,860"]
    ]
  }
}
```

---

## Calculator Keystrokes

### TVM Worksheet (Time Value of Money)
```json
"calculator_keystrokes": {
  "method": "TVM Worksheet",
  "steps_en": [
    "N = 12",
    "I/Y = 2",
    "PV = -150,000",
    "PMT = 0",
    "CPT → FV = 190,236.27"
  ],
  "steps_ru": [...]
}
```

### Cash Flow Worksheet (IRR/NPV)
```json
"calculator_keystrokes": {
  "method": "Cash Flow Worksheet",
  "steps_en": [
    "CF0 = -1,100",
    "CF1 = -580",
    "CF2 = 1,860",
    "CPT → IRR = 6.31%"
  ],
  "steps_ru": [...]
}
```

### Без калькулятора
```json
"requires_calculator": false,
"calculator_keystrokes": null
```

---

## Difficulty Levels

- `"easy"` — определения, простые концепции
- `"medium"` — стандартные расчёты
- `"hard"` — сложные многошаговые задачи, TWR/MWR

---

## Question ID Format

`{BOOK_CODE}-{MODULE_ID}-Q{SEQUENCE}`

Примеры:
- `QM-1-Q001` — Quantitative Methods, Module 1, Question 1
- `QM-2-Q015` — Quantitative Methods, Module 2, Question 15
- `ECO-3-Q008` — Economics, Module 3, Question 8

---

## Book Codes

| Book | Code | Name |
|------|------|------|
| 1 | QM | Quantitative Methods |
| 2 | ECO | Economics |
| 3 | FRA | Financial Statement Analysis |
| 4 | CF | Corporate Finance |
| 5 | EI | Equity Investments |
| 6 | FI | Fixed Income |
| 7 | DER | Derivatives |
| 8 | ALT | Alternative Investments |
| 9 | PM | Portfolio Management |
| 10 | ETH | Ethics |

---

## Валидация JSON

После каждого чекпоинта запускай:

```bash
python3 << 'EOF'
import json
with open('PATH_TO_FILE.json', 'r') as f:
    data = json.load(f)
    print(f"✅ Valid JSON")
    print(f"Questions: {len(data['questions'])}")
    print(f"Metadata total: {data['metadata']['total_questions']}")
EOF
```

---

## Частые ошибки (избегать!)

### ❌ Обрезанные таблицы
**Плохо:** Показать только 2 строки из 7
**Хорошо:** Показать ВСЮ таблицу как в оригинале

### ❌ Пропущенный question_continuation
**Плохо:** Нет текста после таблицы
**Хорошо:** Добавить `question_continuation_en/ru` с текстом "The return is closest to:"

### ❌ Таблица-решение в условии
**Плохо:** `has_table: true` для таблицы с cash flows (спойлер!)
**Хорошо:** `has_table: false` + `explanation_table` для таблиц-решений

### ❌ Пустые explanation_wrong
**Плохо:** `"text_en": "Incorrect."`
**Хорошо:** `"text_en": "Incorrect. This would be the result with annual compounding instead of quarterly."`

### ❌ Неполные calculator_keystrokes
**Плохо:** Только "Use TVM"
**Хорошо:** Полные шаги с конкретными значениями

---

## Пример полного вопроса с таблицей

```json
{
  "question_id": "QM-1-Q012",
  "original_question_number": 770,
  "los_id": "LOS_1b",
  "question_text_en": "Rick Hassler earned the following annual rates of return by holding shares of XYZ Inc. for a period of five years:",
  "question_text_ru": "Рик Хасслер получил следующие годовые доходности, владея акциями XYZ Inc. пять лет:",
  "has_table": true,
  "table_data": {
    "headers": ["Year", "Return (%)"],
    "headers_ru": ["Год", "Доходность (%)"],
    "rows": [
      ["2011", "13"],
      ["2012", "19"],
      ["2013", "-11"],
      ["2014", "25"],
      ["2015", "30"]
    ]
  },
  "question_continuation_en": "The share's holding period return over the five-year period is closest to:",
  "question_continuation_ru": "Доходность за период владения за пять лет ближе всего к:",
  "options": [
    {"id": "opt_a", "text_en": "94%", "text_ru": "94%"},
    {"id": "opt_b", "text_en": "21%", "text_ru": "21%"},
    {"id": "opt_c", "text_en": "14%", "text_ru": "14%"}
  ],
  "correct_option_id": "opt_a",
  "explanation_en": "HPR = (1.13)(1.19)(0.89)(1.25)(1.30) - 1 = 0.94 or 94%",
  "explanation_ru": "HPR = (1.13)(1.19)(0.89)(1.25)(1.30) - 1 = 0.94 или 94%",
  "explanation_formula": "$HPR = \\prod_{i=1}^{n}(1 + R_i) - 1$",
  "explanation_table": null,
  "explanation_wrong": {
    "opt_b": {
      "text_en": "Incorrect. Simple average without compounding.",
      "text_ru": "Неверно. Простое среднее без сложного процента."
    },
    "opt_c": {
      "text_en": "Incorrect. Significantly underestimates the compounded return.",
      "text_ru": "Неверно. Значительно недооценивает составную доходность."
    }
  },
  "requires_calculator": false,
  "calculator_keystrokes": null,
  "difficulty": "medium",
  "topic_tags": ["holding_period_return"]
}
```

---

## Пример вопроса с explanation_table

```json
{
  "question_id": "QM-1-Q022",
  "original_question_number": 2670,
  "los_id": "LOS_1g",
  "question_text_en": "Jane Sonam purchases 10 shares of Solar Inc. at $110. One year later, she purchased an additional 5 shares at $120. The stock paid a dividend of $2 per share each year. Calculate the money-weighted return if she sold all 15 shares for $122 at the end of the second year.",
  "question_text_ru": "Джейн Сонам покупает 10 акций Solar Inc. по $110. Год спустя ещё 5 по $120. Дивиденд $2 на акцию. MWR если продала все 15 по $122:",
  "has_table": false,
  "table_data": null,
  "options": [
    {"id": "opt_a", "text_en": "6.31%", "text_ru": "6.31%"},
    {"id": "opt_b", "text_en": "10.58%", "text_ru": "10.58%"},
    {"id": "opt_c", "text_en": "12.35%", "text_ru": "12.35%"}
  ],
  "correct_option_id": "opt_a",
  "explanation_en": "CF0=-1100; CF1=-580; CF2=1860; IRR=6.31%",
  "explanation_ru": "CF0=-1100; CF1=-580; CF2=1860; IRR=6.31%",
  "explanation_formula": null,
  "explanation_table": {
    "headers": ["Time", "Share Value", "Dividend", "Net Cash Flow"],
    "headers_ru": ["Время", "Стоимость", "Дивиденд", "Чистый поток"],
    "rows": [
      ["Year 0", "-$1,100", "$0", "-$1,100"],
      ["Year 1", "-$600", "$20", "-$580"],
      ["Year 2", "$1,830", "$30", "$1,860"]
    ]
  },
  "explanation_wrong": {
    "opt_b": {"text_en": "Incorrect.", "text_ru": "Неверно."},
    "opt_c": {"text_en": "Incorrect.", "text_ru": "Неверно."}
  },
  "requires_calculator": true,
  "calculator_keystrokes": {
    "method": "Cash Flow Worksheet",
    "steps_en": ["CF0 = -1,100", "CF1 = -580", "CF2 = 1,860", "CPT → IRR = 6.31%"],
    "steps_ru": ["CF0 = -1,100", "CF1 = -580", "CF2 = 1,860", "CPT → IRR = 6.31%"]
  },
  "difficulty": "hard",
  "topic_tags": ["money_weighted_return", "irr"]
}
```

---

## Финальный checklist перед push

- [ ] JSON валиден (no syntax errors)
- [ ] `total_questions` в metadata совпадает с реальным количеством
- [ ] Все вопросы имеют уникальные `question_id`
- [ ] Все `correct_option_id` существуют в options
- [ ] Таблицы в условии: `has_table: true` + `table_data`
- [ ] Таблицы в решении: `has_table: false` + `explanation_table`
- [ ] Все поля `_en` и `_ru` заполнены
- [ ] Calculator keystrokes для вопросов с `requires_calculator: true`
