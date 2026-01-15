# QBANK INSTRUCTION v4.0

**Версия:** 4.0  
**Дата:** 15 января 2026  
**Для структуры:** `frontend/data/v2/`

---

## ЦЕЛЬ

Создать `questions.json` для одного модуля CFA Level 1.  
Файл содержит вопросы, варианты ответов, объяснения и привязки к glossary.

---

## ПРИНЦИП РАБОТЫ

```
glossary.json (уже создан)
    ↓
qbank.docx/pdf (исходник) + glossary.json
    ↓
questions.json (результат)
```

**ВАЖНО:** Glossary создаётся ПЕРВЫМ. QBANK берёт из него:
- `term_id` — для привязки вопроса к термину
- `formula` — для отображения в explanation
- `calculator` — шаги калькулятора

---

## ФАЙЛОВАЯ СТРУКТУРА

**Входные данные:**
```
frontend/data/v2/{book}/module{N}/sources/qbank.docx
frontend/data/v2/{book}/module{N}/glossary.json
```

**Выходные данные:**
```
frontend/data/v2/{book}/module{N}/questions.json
```

**Пример:**
```
frontend/data/v2/book1_quants/module1/sources/qbank.docx
frontend/data/v2/book1_quants/module1/glossary.json
    ↓
frontend/data/v2/book1_quants/module1/questions.json
```

---

## СТРУКТУРА questions.json

```json
{
  "book_id": 1,
  "book_code": "QM",
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  
  "module_id": 1,
  "module_name": "Rate and Return",
  "module_name_ru": "Ставки и доходность",
  
  "total_questions": 25,
  
  "questions": [
    { ... }
  ]
}
```

---

## СТРУКТУРА ОДНОГО ВОПРОСА

```json
{
  "question_id": "QM-1-Q013",
  "question_number": 13,
  
  "term_id": "QM-1-015",
  "los_id": "LOS_1d",
  
  "question_text": "A bank offers you a Certificate of Deposit (CD) with a three-year maturity...",
  "question_text_ru": "Банк предлагает депозитный сертификат со сроком 3 года...",
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
  
  "explanation": "FV with quarterly compounding: FV = PV[1 + rs/m]^(mN)",
  "explanation_ru": "FV с квартальным начислением.",
  "explanation_formula": "$FV_N = PV \\left[1 + \\frac{r_s}{m}\\right]^{mN} = \\$150,000 \\left[1 + \\frac{0.08}{4}\\right]^{12} = \\$190,236.27$",
  
  "explanation_wrong": {
    "opt1": {
      "text": "FV with annual compounding instead of quarterly.",
      "text_ru": "FV с годовым начислением вместо квартального.",
      "formula": "$FV = \\$150,000(1.08)^3 = \\$188,956.80$"
    },
    "opt2": {
      "text": "FV with semi-annual compounding.",
      "text_ru": "FV с полугодовым начислением.",
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
  
  "topic_tags": ["FV", "compounding", "quarterly", "TVM"]
}
```

---

## ПОЛЯ ВОПРОСА

| Поле | Обязательное | Описание |
|------|--------------|----------|
| `question_id` | ✅ Да | Уникальный ID: `{BOOK_CODE}-{MODULE}-Q{NUMBER}` |
| `question_number` | ✅ Да | Номер вопроса из исходника |
| `term_id` | ⚠️ Если есть | ID термина из glossary.json этого модуля |
| `los_id` | ✅ Да | LOS из исходника (формат `LOS_1a`) |
| `question_text` | ✅ Да | Текст вопроса на английском |
| `question_text_ru` | ✅ Да | Текст вопроса на русском |
| `question_text_formula` | ⚠️ Если есть | LaTeX формула в тексте вопроса |
| `question_continuation` | ⚠️ Если есть | Продолжение вопроса после таблицы |
| `has_table` | ✅ Да | `true` если есть таблица |
| `table_data` | ⚠️ Если есть | Данные таблицы (см. формат ниже) |
| `options` | ✅ Да | Массив вариантов ответа |
| `correct_option_id` | ✅ Да | ID правильного варианта |
| `explanation` | ✅ Да | Объяснение правильного ответа (EN) |
| `explanation_ru` | ✅ Да | Объяснение правильного ответа (RU) |
| `explanation_formula` | ⚠️ Если есть | LaTeX формула решения |
| `explanation_wrong` | ✅ Да | Объяснения неправильных вариантов |
| `requires_calculation` | ✅ Да | `true` если нужен калькулятор |
| `calculator_steps` | ⚠️ Если calculation | Шаги на BA II Plus |
| `difficulty` | ✅ Да | `EASY`, `MEDIUM`, `HARD` |
| `topic_tags` | ⚠️ Опционально | Теги для фильтрации |

---

## ⚠️ АЛГОРИТМ СОЗДАНИЯ QUESTIONS.JSON (СТРОГО ОБЯЗАТЕЛЬНЫЙ)

### ШАГ 0: ЗАГРУЗИТЬ GLOSSARY

```
⚠️ КРИТИЧЕСКИ ВАЖНО ⚠️
Перед парсингом QBANK загрузить glossary.json этого модуля!
Извлечь список всех term_id и их term_en для поиска соответствий.
```

**Пример списка терминов из glossary Module 1:**
```
QM-1-001: Interest Rate
QM-1-007: Holding Period Return (HPR)
QM-1-008: Arithmetic Mean Return
QM-1-009: Geometric Mean Return
QM-1-013: Money-Weighted Rate of Return (MWRR)
QM-1-014: Time-Weighted Rate of Return (TWRR)
QM-1-015: Effective Annual Rate (EAR)
QM-1-016: Continuously Compounded Return
...
```

---

### ШАГ 1: ИЗВЛЕЧЬ ТЕКСТ ИЗ DOCX

Прочитать qbank.docx и найти все вопросы по паттерну:
```
Q.{номер} {текст вопроса}
A. {вариант A}
B. {вариант B}
C. {вариант C}
The correct answer is {буква}.
{объяснение правильного ответа}
A is incorrect. {объяснение}
B is incorrect. {объяснение}
```

---

### ШАГ 2: ДЛЯ КАЖДОГО ВОПРОСА НАЙТИ term_id

**Алгоритм поиска term_id:**

1. Извлечь ключевые слова из текста вопроса:
   - "time-weighted" → TWRR
   - "money-weighted" → MWRR
   - "holding period return" или "HPR" → HPR
   - "effective annual rate" или "EAR" → EAR
   - "continuously compounded" → Continuous Return
   - "geometric mean" → Geometric Mean Return
   - "arithmetic mean" → Arithmetic Mean Return
   - "compounded quarterly/monthly/annually" → часто связано с FV/PV/EAR

2. Найти соответствующий термин в glossary.json по `term_en`

3. Записать `term_id` в вопрос

**Пример:**
```
Вопрос: "what is the time-weighted rate of return?"
→ Ключевое слово: "time-weighted rate of return"
→ Находим в glossary: "Time-Weighted Rate of Return (TWRR)" = QM-1-014
→ term_id: "QM-1-014"
```

```
⛔ ЕСЛИ ТЕРМИН НЕ НАЙДЕН:
- Оставить term_id: null
- Но это редкий случай — большинство вопросов привязаны к терминам
```

---

### ШАГ 3: ИЗВЛЕЧЬ ОБЪЯСНЕНИЯ НЕПРАВИЛЬНЫХ ОТВЕТОВ

В DOCX после правильного объяснения идут:
```
A is incorrect. {текст объяснения}
{формула если есть}

B is incorrect. {текст объяснения}
{формула если есть}
```

**Формат в JSON:**
```json
"explanation_wrong": {
  "opt1": {
    "text": "A is incorrect. The amount represents the future value with annual and not with quarterly compounding.",
    "text_ru": "Вариант A неверен. Сумма представляет будущую стоимость с годовым, а не квартальным начислением.",
    "formula": "$FV = \\$150,000(1.08)^3 = \\$188,956.80$"
  },
  "opt2": {
    "text": "B is incorrect. The amount represents the future value with semi-annual compounding.",
    "text_ru": "Вариант B неверен. Сумма представляет будущую стоимость с полугодовым начислением.",
    "formula": "$FV = \\$150,000(1.04)^6 = \\$189,797.85$"
  }
}
```

```
⚠️ ВАЖНО:
- opt1 = вариант A в исходнике
- opt2 = вариант B в исходнике
- opt3 = вариант C в исходнике
- Если правильный ответ C, то explanation_wrong содержит только opt1 и opt2
```

---

### ШАГ 4: ИЗВЛЕЧЬ/НАПИСАТЬ CALCULATOR_STEPS

**Если в исходнике есть шаги калькулятора:**
- Скопировать их
- Привести к формату `[кнопка]`

**Если шагов нет, но requires_calculation = true:**
- Посмотреть `calculator` в glossary.json для соответствующего `term_id`
- Адаптировать под конкретные числа вопроса

**Формат кнопок:**
```
[2ND] [CLR TVM]
[2ND] [P/Y] 4 [ENTER]
[2ND] [QUIT]
150000 [+/-] [PV]
8 [I/Y]
12 [N]
0 [PMT]
[CPT] [FV] → 190,236.27
```

---

### ШАГ 5: ОПРЕДЕЛИТЬ DIFFICULTY

| Difficulty | Критерии |
|------------|----------|
| EASY | Прямое применение одной формулы, простые числа |
| MEDIUM | Несколько шагов вычислений, промежуточные результаты |
| HARD | Сложные условия, несколько концепций, нестандартные ситуации |

---

### ШАГ 6: ВАЛИДАЦИЯ

```
ЧЕКЛИСТ ПЕРЕД СОХРАНЕНИЕМ:

□ Все question_id уникальны
□ Все correct_option_id соответствуют существующим options
□ explanation_wrong содержит ВСЕ неправильные варианты
□ term_id существует в glossary.json (если указан)
□ los_id в правильном формате (LOS_1a, LOS_1b...)
□ calculator_steps есть для всех requires_calculation: true
□ JSON валиден
```

---

## ФОРМАТ ТАБЛИЦ

Если вопрос содержит таблицу:

```json
"has_table": true,
"table_data": {
  "headers": ["Year", "Beginning Value", "Ending Value", "Cash Flow"],
  "rows": [
    ["1", "$100,000", "$95,000", "$5,000"],
    ["2", "$95,000", "$110,000", "$0"],
    ["3", "$110,000", "$125,000", "$10,000"]
  ]
}
```

---

## ФОРМУЛЫ В LaTeX

**Формат:** `$...$`

**Примеры:**
```
$FV_N = PV \\left[1 + \\frac{r_s}{m}\\right]^{mN}$

$HPR = \\frac{P_1 - P_0 + D_1}{P_0}$

$TWRR = \\left[\\prod_{t=1}^{T}(1+HPR_t)\\right]^{1/T} - 1$
```

**Правила экранирования в JSON:**
- `\` → `\\`
- `$` остаётся как есть

---

## NAMING CONVENTIONS

### question_id
```
{BOOK_CODE}-{MODULE}-Q{NUMBER}
```
Примеры: `QM-1-Q013`, `QM-1-Q015`, `EC-2-Q001`

### term_id (из glossary)
```
{BOOK_CODE}-{MODULE}-{NUMBER}
```
Примеры: `QM-1-015` (EAR), `QM-1-007` (HPR)

### los_id
```
LOS_{module}{letter}
```
Примеры: `LOS_1a`, `LOS_1d`, `LOS_2c`

---

## МАППИНГ КЛЮЧЕВЫХ СЛОВ → ТЕРМИНОВ

| Ключевые слова в вопросе | term_en в glossary | Пример term_id |
|--------------------------|-------------------|----------------|
| "holding period return", "HPR" | Holding Period Return (HPR) | QM-1-007 |
| "arithmetic mean", "simple average" | Arithmetic Mean Return | QM-1-008 |
| "geometric mean", "compound return" | Geometric Mean Return | QM-1-009 |
| "money-weighted", "MWRR", "IRR" | Money-Weighted Rate of Return | QM-1-013 |
| "time-weighted", "TWRR" | Time-Weighted Rate of Return | QM-1-014 |
| "effective annual rate", "EAR" | Effective Annual Rate (EAR) | QM-1-015 |
| "continuously compounded", "ln" | Continuously Compounded Return | QM-1-016 |
| "compounded quarterly/monthly" | может быть EAR или FV | зависит от контекста |
| "gross return" | Gross Return | QM-1-017 |
| "net return" | Net Return | QM-1-018 |
| "real return", "inflation-adjusted" | Real Return | QM-1-019 |
| "leveraged return", "borrowed funds" | Leveraged Return | QM-1-021 |

---

## ПРИМЕР ПОЛНОГО ВОПРОСА

```json
{
  "question_id": "QM-1-Q221",
  "question_number": 221,
  
  "term_id": "QM-1-014",
  "los_id": "LOS_1c",
  
  "question_text": "An investor buys 4 shares of UUA stock at $44. During the year, the company pays a $3 special dividend per share. Then, at the end of the first year, the investor buys 5 more shares at $46. Lastly, at the end of the second year, he sold all the shares for $57. If there was no dividend during the second year, what is the time-weighted rate of return of this investment?",
  "question_text_ru": "Инвестор покупает 4 акции UUA по $44. В течение года компания выплачивает специальный дивиденд $3 на акцию. Затем в конце первого года инвестор покупает ещё 5 акций по $46. В конце второго года он продал все акции по $57. Если во втором году дивидендов не было, какова доходность по методу взвешивания по времени?",
  "question_text_formula": null,
  "question_continuation": null,
  
  "has_table": false,
  "table_data": null,
  
  "options": [
    {"id": "opt1", "text": "11.4%"},
    {"id": "opt2", "text": "15.2%"},
    {"id": "opt3", "text": "17.4%"}
  ],
  
  "correct_option_id": "opt3",
  
  "explanation": "TWRR is calculated by linking the HPRs of each sub-period geometrically.",
  "explanation_ru": "TWRR рассчитывается путём геометрического связывания HPR каждого подпериода.",
  "explanation_formula": "$HPR_1 = \\frac{46-44+3}{44} = 11.36\\%$\n$HPR_2 = \\frac{57-46}{46} = 23.91\\%$\n$TWRR = [(1.1136)(1.2391)]^{0.5} - 1 = 17.4\\%$",
  
  "explanation_wrong": {
    "opt1": {
      "text": "An 11.4% return would suggest only considering the first year's performance without properly accounting for the compounding effect over the two years.",
      "text_ru": "Доходность 11.4% предполагает учёт только первого года без правильного учёта эффекта сложного процента за два года.",
      "formula": null
    },
    "opt2": {
      "text": "A 15.2% return underestimates the combined effect of the first year's dividend and the second year's capital gain. It does not accurately reflect the geometric linking of the two periods' returns as required by the TWR calculation.",
      "text_ru": "Доходность 15.2% недооценивает совокупный эффект дивиденда первого года и прироста капитала второго года. Она не отражает точно геометрическое связывание доходностей двух периодов, требуемое расчётом TWR.",
      "formula": null
    }
  },
  
  "requires_calculation": true,
  
  "calculator_steps": [
    "HPR1: (46-44+3)/44 = 0.1136",
    "HPR2: (57-46)/46 = 0.2391",
    "1.1136 [×] 1.2391 [=]",
    "[yˣ] 0.5 [=]",
    "[-] 1 [=] → 17.4%"
  ],
  
  "difficulty": "HARD",
  
  "topic_tags": ["TWRR", "HPR", "geometric linking", "multi-period return"]
}
```

---

## ИЗВЕСТНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема: Формулы в DOCX разваливаются при парсинге
**Решение:** Писать формулы вручную в LaTeX, ориентируясь на контекст и результат

### Проблема: Не понятно какой term_id присвоить
**Решение:** Искать ключевые слова (HPR, TWRR, EAR...) в тексте вопроса и explanation

### Проблема: LOS в исходнике из другой книги
**Решение:** Игнорировать LOS из исходника, определять по термину из glossary этого модуля. Записать оригинальный LOS в отдельное поле `source_los` если нужно.

### Проблема: Несколько терминов в одном вопросе
**Решение:** Указать основной термин (на который отвечает вопрос). Можно добавить `related_terms: ["QM-1-007", "QM-1-014"]`

---

## КОМАНДА ДЛЯ ЗАПУСКА

```
Создай questions.json для [book]/[module].

СТРОГО следуй инструкции QBANK_INSTRUCTION_v4.md:
1. ШАГ 0: Загрузи glossary.json и извлеки список терминов
2. ШАГ 1: Извлеки текст из qbank.docx
3. ШАГ 2: Для каждого вопроса найди term_id по ключевым словам
4. ШАГ 3: Извлеки explanation_wrong для каждого неправильного варианта
5. ШАГ 4: Добавь calculator_steps
6. ШАГ 5: Определи difficulty
7. ШАГ 6: Валидируй JSON

Исходники:
- frontend/data/v2/[book]/[module]/sources/qbank.docx
- frontend/data/v2/[book]/[module]/glossary.json

Результат:
- frontend/data/v2/[book]/[module]/questions.json
```

---

## ФИНАЛЬНЫЙ ЧЕКЛИСТ

```
ПЕРЕД СОХРАНЕНИЕМ questions.json ПРОВЕРИТЬ:

□ Glossary загружен, список терминов извлечён
□ Все вопросы из исходника обработаны
□ Каждый вопрос имеет term_id (если применимо)
□ explanation_wrong содержит ВСЕ неправильные варианты
□ calculator_steps есть для всех requires_calculation: true
□ Формулы в правильном LaTeX формате
□ JSON валиден (нет trailing commas, правильные кавычки)
□ total_questions соответствует количеству вопросов в массиве
```
