# GLOSSARY INSTRUCTION v2.0
## Инструкция по созданию глоссариев для CFA Level 1 Trainer

**Версия:** 2.0
**Дата:** 2026-01-17
**Статус:** Production

---

# 🛑 СТОП! ПРОЧИТАЙ ПЕРЕД НАЧАЛОМ РАБОТЫ!

## ШАГ 0: Создание ветки (ОБЯЗАТЕЛЬНО ПЕРВЫМ!)

**НЕ НАЧИНАЙ РАБОТУ пока не создашь ветку правильно!**

### Формат названия ветки:
```
claude/add-{book}-module-{N}-glossary-{random}
```

### Пример для Economics Module 5:
```bash
git checkout -b claude/add-economics-module-5-glossary-xK9mP
git push -u origin claude/add-economics-module-5-glossary-xK9mP
```

### ⛔ ПРОВЕРЬ СЕБЯ:
1. Ветка начинается с `claude/add-` ? ✓
2. Название книги МАЛЕНЬКИМИ буквами (economics, НЕ Economics)? ✓
3. Есть `module-5` (или другой номер)? ✓
4. Есть `-glossary-` ? ✓
5. Заканчивается случайными символами? ✓

### ❌ НЕПРАВИЛЬНО:
- `claude/create-economics-glossary-xxx` — нет `module-N`!
- `claude/add-Economics-module-5-glossary-xxx` — заглавная буква!
- `claude/add-economics-glossary-xxx` — нет `module-N`!

### ✅ ПРАВИЛЬНО:
- `claude/add-economics-module-5-glossary-xK9mP`
- `claude/add-quants-module-3-glossary-aB3nQ`

**⛔ ЕСЛИ ВЕТКА СОЗДАНА НЕПРАВИЛЬНО — УДАЛИ И СОЗДАЙ ЗАНОВО:**
```bash
git checkout main
git branch -D claude/неправильное-имя
git checkout -b claude/add-{book}-module-{N}-glossary-{random}
```

**📌 Где взять значения:**
- `{book}` — название книги МАЛЕНЬКИМИ буквами (economics, quants, fsa, cf, equity, fi, derivatives, alt, pm, ethics)
- `{N}` — номер модуля из задания (1, 2, 3...)
- `{random}` — любой короткий случайный суффикс (5 символов)

**⚠️ БЕЗ номера модуля ветка НЕ БУДЕТ РАСПОЗНАНА системой мониторинга!**

---

## 📋 ОБЗОР

Эта инструкция описывает процесс создания JSON-файлов глоссария для каждого модуля CFA Level 1. 

**Ключевые принципы:**
- Группировка по LOS (Learning Outcome Statements)
- Формулы берутся из `formulas_master.json` (золотой стандарт)
- Билингвальная поддержка (EN/RU)
- Интерактивные упражнения с решениями
- Калькуляторные инструкции BA II Plus

---

## 🛠️ ВАЛИДАТОР (ОБЯЗАТЕЛЬНО!)

**Запускай валидатор ПЕРЕД КАЖДЫМ чекпоинтом:**

```bash
python frontend/data/v2/scripts/validate_glossary.py glossary_module_X.json --fix
```

### Что авто-исправляет:
- ✅ `total_terms` (пересчитывает)
- ✅ Дублирующиеся `term_id` (добавляет суффикс)

### Что требует ручного исправления:
- ❌ JSON синтаксис
- ❌ Пустые поля (term_en, definition_en/ru)
- ❌ Недостающие переводы EN/RU
- ❌ Мало терминов (<10)

### Проверки валидатора (9 штук):
1. JSON синтаксис
2. Metadata существует
3. Обязательные поля metadata
4. LOS массив существует
5. Минимум 10 терминов
6. Все термины имеют обязательные поля
7. Уникальные term_id
8. total_terms совпадает
9. EN/RU определения различаются (не copy-paste)

**Workflow каждого чекпоинта:**
```
1. Добавить термины
2. python scripts/validate_glossary.py file.json --fix
3. Убедиться что 100% ✓
4. git commit
```

**Путь к валидатору:** `scripts/validate_glossary.py`

---

## 🔄 Git — Checkpoints (ОБЯЗАТЕЛЬНО)

Глоссарий нужно коммитить поэтапно. Работаем по чекпоинтам с валидацией ПЕРЕД каждым коммитом:

## Чекпоинт 1: Структура + первый LOS

1. Создай файл `glossary_module_X.json` с metadata
2. Добавь первый LOS со всеми терминами
3. **ВАЛИДАЦИЯ:** `python scripts/validate_glossary.py glossary_module_X.json --fix`
4. Убедись что 100% ✓
5. **GIT COMMIT + PUSH:**
```bash
git add . && git commit -m "Glossary Module X: checkpoint 1 - structure and LOS_Xa"
git push origin HEAD
```

## Чекпоинт 2: Следующие LOS (до 50%)

1. Добавь следующие LOS с терминами (до 50% от общего количества LOS)
2. **ВАЛИДАЦИЯ:** `python scripts/validate_glossary.py glossary_module_X.json --fix`
3. Убедись что 100% ✓
4. **GIT COMMIT + PUSH:**
```bash
git add . && git commit -m "Glossary Module X: checkpoint 2 - 50% LOS complete"
git push origin HEAD
```

## Чекпоинт 3: Оставшиеся LOS (до 75%)

1. Добавь оставшиеся LOS с терминами (до 75% от общего количества LOS)
2. **ВАЛИДАЦИЯ:** `python scripts/validate_glossary.py glossary_module_X.json --fix`
3. Убедись что 100% ✓
4. **GIT COMMIT + PUSH:**
```bash
git add . && git commit -m "Glossary Module X: checkpoint 3 - 75% LOS complete"
git push origin HEAD
```

## Чекпоинт 4: Финализация

1. Добавь все оставшиеся LOS с терминами (100%)
2. Добавь все упражнения (exercises) для каждого LOS
3. **ФИНАЛЬНАЯ ВАЛИДАЦИЯ:** `python scripts/validate_glossary.py glossary_module_X.json --fix`
4. Убедись что 100% ✓
5. Обнови `meta.json` — добавь `glossary_file` и обнови статус
6. **GIT COMMIT + PUSH:**
```bash
git add . && git commit -m "Glossary Module X: complete - Y terms, Z exercises"
git push origin HEAD
```

**ВАЖНО:**
- Валидация ПЕРЕД каждым коммитом обязательна!
- Коммит только после 100% ✓ от валидатора
- Используй `git push origin HEAD` вместо `git push origin {branch-name}`

---

## 📁 СТРУКТУРА ФАЙЛОВ

```
frontend/data/v2/
├── formulas_master.json          ← Золотой стандарт формул (НЕ РЕДАКТИРОВАТЬ)
│
├── book1_quants/
│   ├── meta.json                 ← Метаданные книги
│   ├── module1/
│   │   ├── glossary_module_1.json   ← Глоссарий модуля
│   │   └── sources/              ← PDF источники (опционально)
│   ├── module2/
│   │   └── glossary_module_2.json
│   └── ...
│
├── book2_economics/
│   ├── meta.json
│   └── module1/
│       └── glossary_module_1.json
└── ...
```

---

## 📊 СТРУКТУРА meta.json

Каждая книга имеет свой `meta.json`:

```json
{
  "book_id": 1,
  "book_code": "QM",
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  "total_modules": 11,
  "modules": [
    {
      "module_id": 1,
      "module_name": "Rates and Returns",
      "module_name_ru": "Ставки и доходность",
      "page_range": "3-30",
      "question_range": "3-39",
      "los_codes": ["LOS_1a", "LOS_1b", "LOS_1c", "LOS_1d"],
      "glossary_file": "glossary_module_1.json",
      "status": "complete"
    }
  ]
}
```

**Поля status:**
- `"complete"` — глоссарий готов и проверен
- `"in_progress"` — в работе
- `"pending"` — ещё не начат

**Коды книг (book_code):**
| book_id | book_code | Название |
|---------|-----------|----------|
| 1 | QM | Quantitative Methods |
| 2 | ECON | Economics |
| 3 | FSA | Financial Statement Analysis |
| 4 | CORP | Corporate Issuers |
| 5 | EQ | Equity Investments |
| 6 | FI | Fixed Income |
| 7 | DER | Derivatives |
| 8 | ALT | Alternative Investments |
| 9 | PM | Portfolio Management |
| 10 | ETH | Ethics |

---

## 📐 СТРУКТУРА ГЛОССАРИЯ (glossary_module_X.json)

### Полная схема

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
    "page_range": "3-30",
    "total_terms": 24,
    "total_exercises": 5,
    "version": "2.0",
    "last_updated": "2026-01-17"
  },
  "los": [
    {
      "los_id": "LOS_1a",
      "los_code": "1a",
      "los_description_en": "Interpret interest rates as required rates of return...",
      "los_description_ru": "Интерпретировать процентные ставки как требуемую доходность...",
      "terms": [ /* массив терминов */ ],
      "exercises": [ /* массив упражнений */ ]
    }
  ]
}
```

---

## 📝 СТРУКТУРА ТЕРМИНА

### Термин типа "concept" (без формулы)

```json
{
  "term_id": "QM-1-001",
  "term_en": "Interest Rate",
  "term_ru": "Процентная ставка",
  "definition_en": "A rate of return that reflects...",
  "definition_ru": "Ставка доходности, отражающая...",
  "type": "concept",
  "formula": null,
  "formula_ref": null,
  "calculator": null
}
```

### Термин типа "formula" (с формулой и калькулятором)

```json
{
  "term_id": "QM-1-008",
  "term_en": "Holding Period Return (HPR)",
  "term_ru": "Доходность за период владения",
  "definition_en": "The total return earned from holding an asset...",
  "definition_ru": "Общая доходность от владения активом...",
  "type": "formula",
  "formula": "$HPR = \\frac{(P_1 - P_0) + I_1}{P_0}$",
  "formula_ref": "QM-TVM-003",
  "variables": [
    {
      "symbol": "P_0",
      "name_en": "Price at time 0",
      "name_ru": "Цена в момент времени 0"
    },
    {
      "symbol": "P_1",
      "name_en": "Price at time 1",
      "name_ru": "Цена в момент времени 1"
    },
    {
      "symbol": "I_1",
      "name_en": "Income earned during period",
      "name_ru": "Доход, полученный за период"
    }
  ],
  "calculator": {
    "method": "BA II Plus: Direct Calculation",
    "steps_ru": [
      "1. Введите начальную цену: {P0} [+/-] [=] [STO] [1]",
      "2. Введите конечную цену: {P1} [-] [RCL] [1] [=]",
      "3. Добавьте доход: [+] {D1} [=]",
      "4. Разделите на начальную цену: [÷] [RCL] [1] [=]",
      "5. Результат: HPR в десятичной форме"
    ],
    "example": {
      "given": "P0=50, P1=56, D1=$2",
      "input": "50+/-=STO1, 56-RCL1=6, +2=8, ÷RCL1=",
      "result": "HPR = 0.16 = 16%"
    }
  }
}
```

### Термин типа "method" (процедура без формулы)

```json
{
  "term_id": "QM-1-012",
  "term_en": "Trimmed Mean",
  "term_ru": "Усечённое среднее",
  "definition_en": "A measure of central tendency calculated by removing...",
  "definition_ru": "Мера центральной тенденции, рассчитываемая путём удаления...",
  "type": "method",
  "formula": null,
  "formula_ref": null,
  "calculator": {
    "method": "BA II Plus: Multi-step Calculation",
    "steps_ru": [
      "1. Упорядочить данные по возрастанию",
      "2. Определить количество значений для удаления с каждой стороны",
      "3. Удалить наименьшие и наибольшие значения",
      "4. Рассчитать среднее арифметическое оставшихся значений"
    ],
    "example": {
      "given": "10 values, 20% trimmed mean",
      "result": "Remove 1 from each end, average middle 8 values"
    }
  }
}
```

### Типы терминов

| type | Описание | formula | calculator |
|------|----------|---------|------------|
| `concept` | Концепция/определение | null | null |
| `formula` | Математическая формула | Обязательно | Обычно да |
| `method` | Процедура/алгоритм | null | Обычно да |

### Формат term_id

```
{BOOK_CODE}-{MODULE_ID}-{SEQUENCE}
```

Примеры:
- `QM-1-001` — Quantitative Methods, Module 1, Term 1
- `ECON-3-015` — Economics, Module 3, Term 15
- `FI-2-008` — Fixed Income, Module 2, Term 8

---

## 🔢 РАБОТА С ФОРМУЛАМИ

### КРИТИЧЕСКОЕ ПРАВИЛО

> **Если формула существует в `formulas_master.json` — ВСЕГДА бери её оттуда!**

### Процесс маппинга формул

1. Читаешь PDF notes модуля
2. Встречаешь формулу (например, HPR)
3. Ищешь в `formulas_master.json` по названию или ID
4. **Если нашёл:**
   - Копируешь `formula` (LaTeX)
   - Копируешь `variables`
   - Указываешь `formula_ref` = ID из мастера
   - Берёшь `calculator_note` или создаёшь `steps_ru`
5. **Если НЕ нашёл:**
   - Пишешь LaTeX вручную
   - `formula_ref: null`

### Структура формулы в formulas_master.json

```json
{
  "id": "QM-TVM-003",
  "name_en": "Holding Period Return (HPR)",
  "name_ru": "Доходность за период владения",
  "book_id": 1,
  "category": "Time Value of Money",
  "formula": "R = \\frac{(P_1 - P_0) + I_1}{P_0}",
  "description": "The total return earned from holding an asset...",
  "description_ru": "Общая доходность от владения активом...",
  "calculator_category": "complex",
  "calculator_template": "DIRECT_HPR",
  "calculator_note": "...",
  "variables": [...],
  "example": "P0=$50, P1=$56, I1=$2: R = (56-50+2)/50 = 16%"
}
```

### LaTeX формат

- Inline формулы: `$formula$`
- Дроби: `\frac{числитель}{знаменатель}`
- Индексы: `R_{i}` или `R_i`
- Суммы: `\sum_{i=1}^{n}`
- Корни: `\sqrt[n]{x}`
- Греческие: `\sigma`, `\pi`, `\beta`, `\mu`
- Надстрочные: `R^2`, `x^{n}`

---

## 🧮 СТРУКТУРА КАЛЬКУЛЯТОРА

### ⚠️ ВАЖНО: Используй `steps_ru`, НЕ `steps`!

Фронтенд ожидает поле `steps_ru` для русскоязычных инструкций.

### Формат

```json
{
  "calculator": {
    "method": "BA II Plus: TVM Worksheet",
    "steps_ru": [
      "1. [2nd] [CLR TVM] — очистка",
      "2. N = количество периодов [N]",
      "3. I/Y = процентная ставка [I/Y]",
      "4. PV = текущая стоимость [PV]",
      "5. PMT = платёж [PMT]",
      "6. [CPT] [FV] — расчёт будущей стоимости"
    ],
    "example": {
      "given": "PV=1000, I/Y=5%, N=10",
      "input": "1000 +/- PV, 5 I/Y, 10 N, CPT FV",
      "result": "FV = $1,628.89"
    }
  }
}
```

### Типы методов калькулятора

| method | Когда использовать |
|--------|-------------------|
| `BA II Plus: TVM Worksheet` | PV, FV, PMT, N, I/Y расчёты |
| `BA II Plus: Cash Flow Worksheet` | NPV, IRR, нерегулярные потоки |
| `BA II Plus: STAT Worksheet` | Статистика: mean, σ, regression |
| `BA II Plus: ICONV Worksheet` | EAR ↔ APR конвертация |
| `BA II Plus: BOND Worksheet` | Цена и доходность облигаций |
| `BA II Plus: Direct Calculation` | Прямые вычисления без worksheet |
| `BA II Plus: Multi-step Calculation` | Сложные многошаговые процедуры |

### Формат кнопок

```
[2nd]     — вторая функция
[CLR TVM] — очистка TVM
[N]       — ввод N
[I/Y]     — ввод процентной ставки
[PV]      — ввод текущей стоимости
[PMT]     — ввод платежа
[FV]      — ввод будущей стоимости
[CPT]     — вычислить
[+/-]     — смена знака
[STO]     — сохранить в память
[RCL]     — вызвать из памяти
[y^x]     — степень
[LN]      — натуральный логарифм
[ENTER]   — ввод
[↓][↑]    — навигация
```

---

## ❓ СТРУКТУРА УПРАЖНЕНИЯ

```json
{
  "exercise_id": "QM-1-EX-001",
  "question_en": "Which of the following is most likely an interpretation of interest rate as a benefit foregone when investors spend money on current consumption instead of saving or investing?",
  "question_ru": "Какая из следующих интерпретаций процентной ставки наиболее точно описывает упущенную выгоду, когда инвесторы тратят деньги на текущее потребление вместо сбережений или инвестирования?",
  "options": [
    {"letter": "A", "text_en": "Discount rate", "text_ru": "Ставка дисконтирования"},
    {"letter": "B", "text_en": "Opportunity cost", "text_ru": "Альтернативная стоимость"},
    {"letter": "C", "text_en": "Required rate of return", "text_ru": "Требуемая доходность"}
  ],
  "correct_answer": "B",
  "solution_en": "Opportunity cost is a key factor in interpreting interest rates. It refers to the interest foregone when investors opt for an alternate option...",
  "solution_ru": "Альтернативная стоимость — ключевой фактор в интерпретации процентных ставок. Это проценты, упущенные когда инвесторы выбирают альтернативный вариант..."
}
```

### Формат exercise_id

```
{BOOK_CODE}-{MODULE_ID}-EX-{SEQUENCE}
```

Примеры:
- `QM-1-EX-001` — первое упражнение Module 1
- `QM-1-EX-002` — второе упражнение Module 1

### Источник упражнений

Упражнения извлекаются из PDF notes — обычно находятся в конце каждого LOS раздела (помечены как "Question" или "Practice Problem").

---

## 🔄 ПОШАГОВЫЙ ПРОЦЕСС СОЗДАНИЯ

### Шаг 1: Подготовка

1. Открой `meta.json` нужной книги
2. Найди модуль: `page_range`, `los_codes`
3. Открой PDF notes на нужных страницах
4. Открой `formulas_master.json`

### Шаг 2: Создание структуры

```json
{
  "metadata": {
    "book_id": X,
    "book_code": "XX",
    "module_id": Y,
    // ... заполни из meta.json
  },
  "los": []
}
```

### Шаг 3: Для каждого LOS

1. Прочитай описание LOS (обычно в начале раздела PDF)
2. Создай объект LOS:
```json
{
  "los_id": "LOS_Xa",
  "los_code": "Xa",
  "los_description_en": "...",
  "los_description_ru": "...",
  "terms": [],
  "exercises": []
}
```

### Шаг 4: Извлечение терминов

Для каждого термина в LOS:

1. **Определи type:** concept / formula / method
2. **Извлеки definition** из PDF (EN)
3. **Переведи на русский** → definition_ru
4. **Если formula:**
   - Проверь `formulas_master.json`
   - Скопируй LaTeX и variables
   - Добавь formula_ref
5. **Если нужен calculator:**
   - Напиши steps_ru
   - Добавь example

### Шаг 5: Извлечение упражнений

1. Найди вопросы в конце LOS раздела
2. Извлеки:
   - Текст вопроса (EN)
   - Варианты ответов A/B/C
   - Правильный ответ
   - Решение/объяснение
3. Переведи на русский
4. Добавь в `exercises[]`

### Шаг 6: Валидация

1. ✅ Все term_id уникальны
2. ✅ LaTeX формулы корректны (проверь рендеринг)
3. ✅ Переводы точные
4. ✅ Правильные ответы в упражнениях верны
5. ✅ steps_ru (НЕ steps) в калькуляторе

### Шаг 7: Обновление meta.json

После завершения:
```json
{
  "module_id": X,
  "status": "complete"  // было "pending"
}
```

---

## 🔄 ОБЯЗАТЕЛЬНО: Обновление meta.json (подробно)

**После создания glossary файла — ОБЯЗАТЕЛЬНО обнови meta.json книги:**

1. Открой `frontend/data/v2/books/book{N}_{name}/meta.json`
2. Найди нужный модуль по `module_id`
3. Добавь/обнови поле: `"glossary_file": "glossary_module_X.json"`
4. Обнови статус:
   - Если qbank уже есть → `"status": "complete"`
   - Если qbank ещё нет → `"status": "in_progress"`
5. Сохрани файл
6. Включи meta.json в коммит

**БЕЗ ЭТОГО ШАГА ГЛОССАРИЙ МОЖЕТ НЕ ОТОБРАЖАТЬСЯ КОРРЕКТНО!**

---

## 📊 Статусы модулей в meta.json

| Статус | Значение | Когда ставить |
|--------|----------|---------------|
| `"pending"` | Контент не создан | По умолчанию |
| `"in_progress"` | Частично готов | QBank ИЛИ Glossary создан |
| `"complete"` | Полностью готов | QBank И Glossary оба готовы |

---

## ✅ ЧЕКЛИСТ КАЧЕСТВА

### Метаданные
- [ ] `book_id` и `module_id` корректны
- [ ] `book_code` соответствует стандарту (QM, ECON, etc.)
- [ ] `page_range` соответствует PDF
- [ ] `total_terms` = реальное количество терминов
- [ ] `total_exercises` = реальное количество упражнений
- [ ] `last_updated` = сегодняшняя дата

### LOS
- [ ] Все LOS из `meta.json` присутствуют
- [ ] `los_description_en` точно из PDF
- [ ] `los_description_ru` корректный перевод

### Термины
- [ ] Все ключевые термины из PDF включены
- [ ] `term_id` уникальны и следуют формату
- [ ] `type` корректен для каждого термина
- [ ] Определения точные и полные
- [ ] Переводы корректные

### Формулы
- [ ] Формулы из `formulas_master.json` где возможно
- [ ] `formula_ref` указан при использовании мастера
- [ ] LaTeX синтаксис корректен
- [ ] `variables` описаны для сложных формул

### Калькулятор
- [ ] Используется `steps_ru` (НЕ `steps`)
- [ ] Шаги понятные и последовательные
- [ ] `example` реалистичный
- [ ] Результаты в примерах правильные

### Упражнения
- [ ] Минимум 1 упражнение на каждый LOS
- [ ] `exercise_id` уникальны
- [ ] Варианты ответов полные (A, B, C)
- [ ] `correct_answer` верный
- [ ] `solution` объясняет логику

---

## ⚠️ ИЗВЕСТНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: steps vs steps_ru

**Симптом:** Калькуляторные инструкции не отображаются

**Причина:** Фронтенд ожидает `steps_ru`, а в JSON указан `steps`

**Решение:** Всегда использовать `steps_ru` для русскоязычных инструкций

### Проблема 2: Формула не рендерится

**Симптом:** Вместо формулы показывается LaTeX код

**Причина:** Неправильный LaTeX синтаксис или отсутствует `$...$`

**Решение:** 
- Оберни формулу в `$...$`
- Проверь экранирование: `\\frac` не `\frac`

### Проблема 3: Текст упражнений не читается

**Симптом:** Чёрный текст на тёмном фоне

**Причина:** CSS не применяется к новым элементам

**Решение:** Проверь что CSS содержит `color: var(--text)` для `.option-text`

---

## 🤖 АВТОМАТИЗАЦИЯ (для Claude Code)

### Алгоритм создания глоссария

```
INPUT: 
  - PDF notes (страницы X-Y)
  - meta.json (book_id, module_id, los_codes)
  - formulas_master.json

PROCESS:
  1. READ meta.json → получить структуру модуля
  2. FOR each LOS in module:
     a. EXTRACT LOS description из PDF
     b. FOR each term in LOS:
        - IDENTIFY: term name, definition
        - CHECK: formulas_master.json
        - IF formula exists: COPY formula, SET formula_ref
        - TRANSLATE: to Russian
        - IF calculator needed: CREATE steps_ru
     c. EXTRACT: exercises из конца LOS раздела
     d. TRANSLATE: exercises to Russian
  3. VALIDATE: JSON structure, unique IDs
  4. UPDATE: meta.json status → "complete"

OUTPUT: glossary_module_X.json
```

### Команда для создания нового модуля

```
Создай глоссарий для Book {X}, Module {Y}.

Входные данные:
- PDF notes: страницы {A}-{B}
- meta.json: frontend/data/v2/book{X}_{name}/meta.json
- formulas_master.json: frontend/data/v2/formulas_master.json

Выходной файл:
- frontend/data/v2/book{X}_{name}/module{Y}/glossary_module_{Y}.json

Следуй инструкции: GLOSSARY_INSTRUCTION.md

После создания:
1. Обнови meta.json: status → "complete"
2. git add, commit, push
```

---

## 📚 ПРИМЕРЫ

### Пример полного глоссария

См. эталонный файл: `book1_quants/module1/glossary_module_1.json`

### Пример маппинга формулы из мастера

**В formulas_master.json:**
```json
{
  "id": "QM-TVM-003",
  "name_en": "Holding Period Return (HPR)",
  "formula": "R = \\frac{(P_1 - P_0) + I_1}{P_0}",
  "variables": [...]
}
```

**В glossary_module_X.json:**
```json
{
  "term_id": "QM-1-008",
  "term_en": "Holding Period Return (HPR)",
  "type": "formula",
  "formula": "$HPR = \\frac{(P_1 - P_0) + I_1}{P_0}$",
  "formula_ref": "QM-TVM-003",
  "variables": [/* скопировать из мастера */]
}
```

---

## 📝 CHANGELOG

### v2.0 (2026-01-17)
- Новая структура с группировкой по LOS
- Добавлены exercises
- Изменено `steps` → `steps_ru`
- Добавлен `formula_ref` для маппинга с мастером
- Добавлены типы терминов: concept, formula, method

### v1.0 (2026-01-15)
- Начальная версия с плоской структурой terms[]

---

**Конец инструкции**
