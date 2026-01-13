# QBANK_INSTRUCTION.md
# Инструкция по созданию JSON тестов из PDF QBank

**Версия:** 3.0 (Production)
**Дата:** 13 января 2026

---

## ЦЕЛЬ

Создавать JSON файлы с тестовыми вопросами из PDF QBank для CFA Level 1 Trainer.

**Ключевые особенности:**
- Options без букв A/B/C → используем `opt1`, `opt2`, `opt3`
- Shuffle на фронтенде по `id`
- Learning Mode с объяснениями после каждого ответа
- Calculator steps для всех расчётных задач
- LaTeX формулы через MathJax

---

## СТРУКТУРА ПРОЕКТА

```
CFA-LVL-I-TRAINER/
├── frontend/
│   ├── data/
│   │   └── books/
│   │       ├── book1.json    ← Quantitative Methods (ГОТОВ)
│   │       ├── book2.json    ← Economics
│   │       └── ...
│   ├── css/styles.css
│   ├── js/app.js
│   └── index.html
├── backend/
│   └── routers/tests.py     ← Читает JSON напрямую
├── Materials/
│   └── Tests/Tests/         ← Исходные PDF (QBank)
├── Instructions/            ← Документация
│   ├── QBANK_INSTRUCTION.md ← Эта инструкция
│   ├── APP_JS_PATCH.md
│   ├── BA_II_PLUS_*.md
│   └── ...
└── CLAUDE.md
```

---

## ПОШАГОВЫЙ ПРОЦЕСС СОЗДАНИЯ МОДУЛЯ

### Шаг 1: Извлечение текста из PDF

```bash
# Установка PyMuPDF (если нет)
pip install pymupdf

# Конвертация PDF в текст
python3 << 'EOF'
import fitz  # PyMuPDF
doc = fitz.open("Materials/Tests/Tests/CH-1-Quantitative_Methods-Answers.pdf")
text = ""
for page in doc:
    text += page.get_text()
with open("extracted.txt", "w", encoding="utf-8") as f:
    f.write(text)
print(f"Extracted {len(doc)} pages")
EOF
```

### Шаг 2: Найти границы модуля в тексте

```bash
# Найти где начинается и заканчивается модуль
grep -n "Learning Module" extracted.txt
```

Пример вывода:
```
69: Learning Module 1: Rate and Return
1232: Learning Module 2: Time Value of Money
```

### Шаг 3: Создать JSON файл

Использовать структуру ниже. Можно использовать Claude для парсинга текста.

---

## СТРУКТУРА JSON ФАЙЛА

```json
{
  "book_id": 1,
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  "total_questions": 26,

  "learning_modules": [
    {
      "module_id": 1,
      "module_name": "Rate and Return",
      "module_name_ru": "Ставки и доходности",
      "los_covered": ["LOS 1a", "LOS 1b", "LOS 1c", "LOS 1d", "LOS 1e"],

      "questions": [
        {
          "question_id": "QM-1-013",
          "question_number": 13,

          "question_text": "A bank offers you a Certificate of Deposit...",
          "question_text_ru": "Банк предлагает депозитный сертификат...",
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

          "explanation": "FV with quarterly compounding...",
          "explanation_ru": "FV с квартальным начислением...",
          "explanation_formula": "$FV = PV \\left[1 + \\frac{r_s}{m}\\right]^{mN}$",

          "explanation_wrong": {
            "opt1": {"text": "Annual compounding.", "formula": "$FV = 150,000(1.08)^3$"},
            "opt2": {"text": "Semi-annual compounding.", "formula": "$FV = 150,000(1.04)^6$"}
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
      ]
    }
  ]
}
```

---

## ПРАВИЛА ИЗВЛЕЧЕНИЯ

### 1. Question ID

```
{BOOK_CODE}-{MODULE}-{ORIGINAL_NUMBER}

Примеры:
QM-1-013   (Quants, Module 1, Question 13)
EC-2-045   (Economics, Module 2, Question 45)
```

**Book Codes:**
| Book | Code | book_id |
|------|------|---------|
| Quantitative Methods | QM | 1 |
| Economics | EC | 2 |
| Financial Statement Analysis | FSA | 3 |
| Corporate Issuers | CI | 4 |
| Equity Investments | EQ | 5 |
| Fixed Income | FI | 6 |
| Derivatives | DER | 7 |
| Alternative Investments | ALT | 8 |
| Portfolio Management | PM | 9 |
| Ethics | ETH | 10 |

### 2. Options (КРИТИЧНО!)

**ПРАВИЛЬНО:**
```json
"options": [
  {"id": "opt1", "text": "$188,956.80"},
  {"id": "opt2", "text": "$189,797.85"},
  {"id": "opt3", "text": "$190,236.27"}
],
"correct_option_id": "opt3"
```

**НЕПРАВИЛЬНО (старый формат):**
```json
"options": {
  "A": "$188,956",
  "B": "$189,797",
  "C": "$190,236"
},
"correct_answer": "C"
```

**Маппинг:**
- A в PDF → `opt1`
- B в PDF → `opt2`
- C в PDF → `opt3`

### 3. Формулы LaTeX

**Inline формула:** `$FV = PV(1+r)^n$`
**Display формула:** `$$FV = PV(1+r)^n$$`

**Экранирование:**
- `\frac` → `\\frac`
- `\left` → `\\left`
- `\times` → `\\times`

**Частые формулы:**
```latex
$FV = PV(1+r)^n$
$PV = \\frac{FV}{(1+r)^n}$
$HPR = \\frac{P_1 - P_0 + D}{P_0}$
$TWRR = \\left[\\prod_{t=1}^{n}(1+HPR_t)\\right]^{1/n} - 1$
$EAR = \\left(1 + \\frac{r_s}{m}\\right)^m - 1$
$FV_{continuous} = PV \\cdot e^{rN}$
```

### 4. Таблицы

```json
{
  "has_table": true,
  "table_data": {
    "headers": ["Year", "Return (%)"],
    "rows": [
      ["2011", "13"],
      ["2012", "19"],
      ["2013", "-11"]
    ]
  }
}
```

### 5. Calculator Steps (BA II Plus)

**TVM задачи:**
```json
"calculator_steps": [
  "[2ND] [CLR TVM]",
  "[2ND] [P/Y] 4 [ENTER]",
  "[2ND] [QUIT]",
  "150000 [+/-] [PV]",
  "8 [I/Y]",
  "12 [N]",
  "0 [PMT]",
  "[CPT] [FV] → 190,236.27"
]
```

**Cash Flow (IRR):**
```json
"calculator_steps": [
  "[CF]",
  "[2ND] [CLR WORK]",
  "1000 [+/-] [ENTER] [↓]",
  "300 [ENTER] [↓] [↓]",
  "500 [ENTER] [↓] [↓]",
  "400 [ENTER]",
  "[IRR] [CPT] → 14.49%"
]
```

**Прямой расчёт (TWRR):**
```json
"calculator_steps": [
  "1.13 [×] 1.19 [×] 0.89 [=]",
  "[yˣ] 0.333333 [=]",
  "[-] 1 [=] → 5.7%"
]
```

### 6. Difficulty

| Level | Критерии |
|-------|----------|
| EASY | Концептуальный, один шаг |
| MEDIUM | 2-3 шага, стандартный расчёт |
| HARD | 4+ шагов, таблицы, нестандартное |

---

## FRONTEND: 3 РЕЖИМА ТЕСТОВ

### 1. Learning Mode (НОВЫЙ)
- Без таймера
- Кнопка "Проверить" после выбора ответа
- Объяснение сразу после проверки:
  - Статус (Правильно/Неправильно)
  - Текст объяснения
  - Формула LaTeX
  - Почему неверный ответ неверен
  - Шаги калькулятора

### 2. Standard Mode
- Общий таймер на весь тест
- Навигация между вопросами
- Результаты после завершения

### 3. 90-Second Mode
- 90 секунд на вопрос
- Таймер может уходить в минус
- Объяснение сразу после ответа

---

## ВАЛИДАЦИЯ JSON

```bash
# Проверить валидность JSON
python3 -c "import json; json.load(open('frontend/data/books/book1.json'))"

# Посчитать вопросы
python3 -c "
import json
d = json.load(open('frontend/data/books/book1.json'))
total = sum(len(m['questions']) for m in d['learning_modules'])
print(f'Total questions: {total}')
for m in d['learning_modules']:
    print(f'  Module {m[\"module_id\"]}: {len(m[\"questions\"])} questions')
"
```

---

## ЧЕКЛИСТ

### Контент
- [ ] Все вопросы модуля извлечены
- [ ] question_id уникальны (QM-1-XXX)
- [ ] Формулы в LaTeX рендерятся
- [ ] Мусор удалён (©, page numbers)

### Структура
- [ ] options как массив `[{id, text}]`
- [ ] correct_option_id указывает на правильный
- [ ] explanation_wrong ключи = opt1/opt2 (не opt3 если он правильный)

### Калькулятор
- [ ] requires_calculation = true для расчётных
- [ ] calculator_steps заполнены
- [ ] Шаги проверены на BA II Plus

### Тестирование
- [ ] JSON валиден
- [ ] Сервер перезапущен
- [ ] Hard refresh в браузере (Ctrl+Shift+R)
- [ ] Learning Mode работает
- [ ] Формулы отображаются

---

## ГОТОВЫЕ МОДУЛИ

| Book | Module | Status | Questions |
|------|--------|--------|-----------|
| QM (1) | Module 1: Rate and Return | ✅ DONE | 26 |
| QM (1) | Module 2: Time Value of Money | ⏳ TODO | - |
| QM (1) | Module 3-11 | ⏳ TODO | - |

---

## TROUBLESHOOTING

### Формулы не рендерятся
MathJax настроен на `$...$` и `$$...$$`. Проверить:
- Экранирование: `\\frac`, не `\frac`
- Hard refresh браузера

### Старые данные в браузере
1. Перезапустить backend сервер
2. DevTools → Application → Clear site data
3. Ctrl+Shift+R

### 42 вопроса вместо 26
Кэш. Перезапустить сервер, очистить браузер.

---

## КОНТАКТЫ

При проблемах — проверить:
1. `frontend/js/app.js` — логика отображения
2. `frontend/index.html` — HTML структура
3. `frontend/css/styles.css` — стили
4. `backend/routers/tests.py` — API загрузки данных
