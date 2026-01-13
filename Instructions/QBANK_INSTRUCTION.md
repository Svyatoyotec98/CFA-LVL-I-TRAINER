# QBANK_INSTRUCTION.md
# Инструкция по созданию JSON тестов из PDF QBank

**Версия:** 2.0 (Final)  
**Дата:** 13 января 2026

---

## ЦЕЛЬ

Пересоздать JSON файлы с тестовыми вопросами из PDF QBank для CFA Level 1 Trainer.

**Ключевые изменения от v1:**
- Options без букв A/B/C → используем `opt1`, `opt2`, `opt3`
- Shuffle на фронтенде по `id`, не по позиции
- Полные объяснения и формулы
- Calculator steps для всех расчётных задач

---

## СТРУКТУРА ПРОЕКТА

```
CFA-LVL-I-TRAINER/
├── frontend/
│   └── data/
│       └── books/
│           ├── book1.json    ← Quantitative Methods
│           ├── book2.json    ← Economics
│           ├── book3.json    ← FSA
│           └── ...
├── Materials/
│   ├── QBank/               ← Исходные PDF
│   ├── NOTES/               ← PDF с Notes
│   └── Instructions/        ← Эта инструкция
└── backend/
```

**Выходные файлы создаём в:** `frontend/data/books/book{N}.json`

---

## СТРУКТУРА JSON ФАЙЛА

```json
{
  "book_id": 1,
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  "total_questions": 236,
  
  "learning_modules": [
    {
      "module_id": 1,
      "module_name": "Rate and Return",
      "module_name_ru": "Ставки и доходности",
      "los_covered": ["LOS 1a", "LOS 1b", "LOS 1c", "LOS 1d", "LOS 1e"],
      
      "questions": [
        {
          // === ИДЕНТИФИКАЦИЯ ===
          "question_id": "QM-1-013",
          "question_number": 13,
          
          // === ТЕКСТ ВОПРОСА ===
          "question_text": "A bank offers you a Certificate of Deposit (CD) with a three-year maturity...",
          "question_text_ru": "Банк предлагает депозитный сертификат со сроком погашения 3 года...",
          "question_text_formula": null,
          "question_continuation": null,
          
          // === ТАБЛИЦА (если есть) ===
          "has_table": false,
          "table_data": null,
          
          // === ВАРИАНТЫ ОТВЕТОВ (БЕЗ БУКВ!) ===
          "options": [
            {"id": "opt1", "text": "$188,956.80", "text_ru": "$188,956.80"},
            {"id": "opt2", "text": "$189,797.85", "text_ru": "$189,797.85"},
            {"id": "opt3", "text": "$190,236.27", "text_ru": "$190,236.27"}
          ],
          "correct_option_id": "opt3",
          
          // === ОБЪЯСНЕНИЕ ===
          "explanation": "The question requires calculation of Future Value with quarterly compounding...",
          "explanation_ru": "Задача требует расчёта будущей стоимости с квартальным начислением...",
          "explanation_formula": "$FV_N = PV \\left[1 + \\frac{r_s}{m}\\right]^{mN}$",
          
          "explanation_wrong": {
            "opt1": {
              "text": "This represents FV with annual compounding instead of quarterly.",
              "text_ru": "Это FV с годовым начислением вместо квартального.",
              "formula": "$FV = 150,000(1.08)^3 = 188,956.80$"
            },
            "opt2": {
              "text": "This represents FV with semi-annual compounding.",
              "text_ru": "Это FV с полугодовым начислением.",
              "formula": "$FV = 150,000(1.04)^6 = 189,797.85$"
            }
          },
          
          // === КАЛЬКУЛЯТОР ===
          "requires_calculation": true,
          "calculator_steps": [
            "[2ND] [CLR TVM] — очистить TVM",
            "[2ND] [P/Y] 4 [ENTER] — 4 периода в год",
            "[2ND] [QUIT]",
            "150000 [+/-] [PV]",
            "8 [I/Y]",
            "12 [N]",
            "0 [PMT]",
            "[CPT] [FV] → 190,236.27"
          ],
          
          // === МЕТАДАННЫЕ ===
          "difficulty": "MEDIUM",
          "los_reference": "LOS 1d: Calculate and interpret annualized return measures",
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
QM-1-770   (Quants, Module 1, Question 770)
FI-3-045   (Fixed Income, Module 3, Question 45)
```

**Book Codes:**
| Book | Code | ID |
|------|------|-----|
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

**Старая структура (НЕ использовать):**
```json
"options": {
  "A": "$188,956",
  "B": "$189,797",
  "C": "$190,236"
},
"correct_answer": "C"
```

**Новая структура (ИСПОЛЬЗОВАТЬ):**
```json
"options": [
  {"id": "opt1", "text": "$188,956.80", "text_ru": "$188,956.80"},
  {"id": "opt2", "text": "$189,797.85", "text_ru": "$189,797.85"},
  {"id": "opt3", "text": "$190,236.27", "text_ru": "$190,236.27"}
],
"correct_option_id": "opt3"
```

**Правила:**
- `opt1` = первый вариант в PDF (был A)
- `opt2` = второй вариант в PDF (был B)
- `opt3` = третий вариант в PDF (был C)
- `opt4` = четвёртый, если есть (был D)
- `correct_option_id` указывает на правильный по `id`

### 3. Таблицы

**Если вопрос содержит таблицу:**
```json
{
  "has_table": true,
  "table_data": {
    "headers": ["Year", "Return (%)"],
    "rows": [
      ["2011", "13"],
      ["2012", "19"],
      ["2013", "-11"],
      ["2014", "25"],
      ["2015", "30"]
    ],
    "caption": null
  }
}
```

**Правила парсинга таблиц:**
- Использовать `pdfplumber` для извлечения
- Все значения как строки (даже числа)
- Отрицательные в скобках сохранять: `"($1,750,000)"`
- Валюту сохранять: `"$7,945,600"`
- Проценты без знака %: `"13"`, не `"13%"`

### 4. Формулы

**Два формата:**
```json
{
  "explanation_formula": "$FV_N = PV \\left[1 + \\frac{r_s}{m}\\right]^{mN}$"
}
```

**Правила:**
- Использовать LaTeX синтаксис
- Обернуть в `$...$` для inline
- Экранировать backslash: `\\frac`, `\\left`, `\\right`
- Проверить рендеринг в MathJax

**Частые формулы:**
```latex
FV: $FV = PV(1+r)^n$
PV: $PV = \\frac{FV}{(1+r)^n}$
HPR: $HPR = \\frac{P_1 - P_0 + D}{P_0}$
TWRR: $TWRR = \\left[\\prod_{t=1}^{n}(1+HPR_t)\\right]^{1/n} - 1$
Geometric Mean: $G = \\left(\\prod_{i=1}^{n} x_i\\right)^{1/n}$
```

### 5. Объяснения неверных ответов

```json
"explanation_wrong": {
  "opt1": {
    "text": "This represents FV with annual compounding instead of quarterly.",
    "text_ru": "Это FV с годовым начислением вместо квартального.",
    "formula": "$FV = 150,000(1.08)^3 = 188,956.80$"
  },
  "opt2": {
    "text": "This represents FV with semi-annual compounding.",
    "text_ru": "Это FV с полугодовым начислением.",
    "formula": "$FV = 150,000(1.04)^6 = 189,797.85$"
  }
}
```

**Правила:**
- Ключ = `id` неверного варианта (`opt1`, `opt2`, ...)
- Для правильного варианта НЕ добавлять
- Включать формулу если она показывает ошибку

### 6. Calculator Steps

**Когда добавлять:**
- `requires_calculation: true`
- Любая задача с TVM (PV, FV, N, I/Y, PMT)
- IRR, NPV, MWRR расчёты
- Статистика (mean, std dev)
- Bond pricing

**Формат:**
```json
"calculator_steps": [
  "[2ND] [CLR TVM] — очистить TVM",
  "[2ND] [P/Y] 4 [ENTER] — 4 периода в год",
  "[2ND] [QUIT]",
  "150000 [+/-] [PV]",
  "8 [I/Y]",
  "12 [N]",
  "0 [PMT]",
  "[CPT] [FV] → 190,236.27"
]
```

**Шаблоны по типам:**

**TVM (Future Value):**
```json
[
  "[2ND] [CLR TVM]",
  "[2ND] [P/Y] {periods} [ENTER]",
  "[2ND] [QUIT]",
  "{pv} [+/-] [PV]",
  "{rate} [I/Y]",
  "{n} [N]",
  "0 [PMT]",
  "[CPT] [FV] → {result}"
]
```

**Cash Flow (IRR/NPV):**
```json
[
  "[CF]",
  "[2ND] [CLR WORK]",
  "{cf0} [+/-] [ENTER] [↓]",
  "{cf1} [+/-] [ENTER] [↓] 1 [ENTER] [↓]",
  "{cf2} [ENTER] [↓] 1 [ENTER]",
  "[IRR] [CPT] → {result}"
]
```

**Direct Calculation (HPR, TWRR):**
```json
[
  "1.13 [×] 1.19 [×] 0.89 [×] 1.25 [×] 1.30 [=]",
  "[yˣ] 0.2 [=]",
  "[-] 1 [=] → {result}"
]
```

### 7. Difficulty

| Level | Критерии |
|-------|----------|
| EASY | Один шаг, концептуальный вопрос, прямое применение формулы |
| MEDIUM | 2-3 шага, стандартная задача с калькулятором |
| HARD | 4+ шагов, таблицы, несколько концепций, нестандартное применение |

### 8. Topic Tags

Добавлять релевантные теги для фильтрации:
```json
"topic_tags": ["FV", "compounding", "quarterly", "TVM"]
```

**Стандартные теги:**
- Расчёты: `FV`, `PV`, `HPR`, `TWRR`, `MWRR`, `IRR`, `NPV`, `EAR`
- Концепции: `arithmetic_mean`, `geometric_mean`, `harmonic_mean`
- Типы: `conceptual`, `calculation`, `table`
- Worksheets: `TVM`, `CF`, `BOND`, `STAT`

---

## ОЧИСТКА ОТ МУСОРА

При парсинге PDF удалять:
- `© 2014-2024 AnalystPrep`
- Номера страниц
- Headers/footers
- Пустые строки в середине текста
- Дублирующиеся пробелы

**Regex для очистки:**
```python
import re

def clean_text(text):
    # Remove copyright
    text = re.sub(r'©\s*\d{4}[-–]\d{4}\s*AnalystPrep\.?\s*\d*', '', text)
    # Remove page numbers
    text = re.sub(r'\n\d+\n', '\n', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```

---

## FRONTEND ИЗМЕНЕНИЯ

### Shuffle Options
```javascript
function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function displayQuestion() {
    const question = state.questions[state.currentQuestionIndex];
    
    // Shuffle options для каждого показа
    const shuffledOptions = shuffleArray(question.options);
    
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = shuffledOptions.map(opt => {
        const isSelected = state.answers[question.question_id] === opt.id;
        return `
            <button class="option ${isSelected ? 'selected' : ''}"
                    data-option-id="${opt.id}"
                    onclick="selectAnswer('${opt.id}')">
                ${opt.text}
            </button>
        `;
    }).join('');
}
```

### Check Answer
```javascript
function selectAnswer(optionId) {
    const question = state.questions[state.currentQuestionIndex];
    state.answers[question.question_id] = optionId;
    
    // Update UI
    document.querySelectorAll('.option').forEach(btn => {
        btn.classList.remove('selected');
        if (btn.dataset.optionId === optionId) {
            btn.classList.add('selected');
        }
    });
}

function showQuestionResult(question, userAnswer) {
    const isCorrect = userAnswer === question.correct_option_id;
    
    document.querySelectorAll('.option').forEach(btn => {
        const optId = btn.dataset.optionId;
        btn.disabled = true;
        
        if (optId === question.correct_option_id) {
            btn.classList.add('correct');
        } else if (optId === userAnswer && !isCorrect) {
            btn.classList.add('incorrect');
        }
    });
    
    // Show explanation
    // ...
}
```

---

## ЧЕКЛИСТ ПЕРЕД ЗАВЕРШЕНИЕМ

### Контент
- [ ] Все вопросы из PDF извлечены
- [ ] question_id уникальны и следуют формату
- [ ] Таблицы корректно парсятся
- [ ] Формулы в LaTeX, рендерятся в MathJax
- [ ] Объяснения полные (не обрезаны)
- [ ] Мусор удалён (©, page numbers)

### Структура
- [ ] options как массив объектов с `id`
- [ ] correct_option_id указывает на правильный
- [ ] explanation_wrong ключи соответствуют opt1/opt2/opt3
- [ ] los_reference заполнен
- [ ] difficulty присвоен

### Калькулятор
- [ ] requires_calculation установлен
- [ ] calculator_steps для всех расчётных задач
- [ ] Keystrokes проверены

### Валидация
- [ ] JSON валиден
- [ ] Все ссылки существуют
- [ ] Frontend работает с новой структурой

---

## ПРИМЕР ПОЛНОГО ВОПРОСА

```json
{
  "question_id": "QM-1-221",
  "question_number": 221,
  "question_text": "An investor buys 4 shares of UUA stock at $44. During the year, the company pays a $3 special dividend per share. Then, at the end of the first year, the investor buys 5 more shares at $46. Lastly, at the end of the second year, he sold all the shares for $57. If there was no dividend during the second year, what is the time-weighted rate of return of this investment?",
  "question_text_ru": "Инвестор покупает 4 акции UUA по $44. В течение года компания выплачивает специальный дивиденд $3 на акцию. В конце первого года инвестор покупает ещё 5 акций по $46. В конце второго года он продаёт все акции по $57. Если во втором году дивидендов не было, какова взвешенная по времени доходность (TWRR)?",
  "question_text_formula": null,
  "question_continuation": null,
  "has_table": false,
  "table_data": null,
  
  "options": [
    {"id": "opt1", "text": "11.4%", "text_ru": "11.4%"},
    {"id": "opt2", "text": "15.2%", "text_ru": "15.2%"},
    {"id": "opt3", "text": "17.4%", "text_ru": "17.4%"}
  ],
  "correct_option_id": "opt3",
  
  "explanation": "The time-weighted rate of return (TWRR) measures portfolio performance independent of external cash flows. First calculate HPR for each period, then geometrically link them.",
  "explanation_ru": "Взвешенная по времени доходность (TWRR) измеряет результативность портфеля независимо от внешних денежных потоков. Сначала рассчитываем HPR для каждого периода, затем геометрически связываем.",
  "explanation_formula": "$TWRR = \\left[(1+HPR_1)(1+HPR_2)\\right]^{1/2} - 1$",
  
  "explanation_wrong": {
    "opt1": {
      "text": "11.4% considers only the first year's performance without the geometric linking.",
      "text_ru": "11.4% учитывает только результат первого года без геометрического связывания.",
      "formula": "$HPR_1 = \\frac{46-44+3}{44} = 11.36\\%$"
    },
    "opt2": {
      "text": "15.2% underestimates the combined effect of both periods.",
      "text_ru": "15.2% недооценивает совокупный эффект обоих периодов.",
      "formula": null
    }
  },
  
  "requires_calculation": true,
  "calculator_steps": [
    "HPR Year 1: (46-44+3)/44 = 0.1136",
    "HPR Year 2: (57-46)/46 = 0.2391",
    "1.1136 [×] 1.2391 [=]",
    "[yˣ] 0.5 [=]",
    "[-] 1 [=] → 0.174 = 17.4%"
  ],
  
  "difficulty": "MEDIUM",
  "los_reference": "LOS 1c: Compare money-weighted and time-weighted rates of return",
  "topic_tags": ["TWRR", "HPR", "geometric_linking"]
}
```
