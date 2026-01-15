# GLOSSARY INSTRUCTION v4.0

**Версия:** 4.0  
**Дата:** 14 января 2026  
**Для структуры:** `frontend/data/v2/`

---

## ЦЕЛЬ

Создать `glossary.json` для одного модуля CFA Level 1.  
Глоссарий содержит термины, формулы и инструкции калькулятора BA II Plus.

---

## ПРИНЦИП РАБОТЫ

```
notes.pdf (исходник)
    ↓
glossary.json (результат)
    ↓
questions.json (использует glossary через LOS_ID)
```

**Glossary создаётся ПЕРВЫМ**, потому что QBANK берёт из него формулы и calculator_steps.

---

## ФАЙЛОВАЯ СТРУКТУРА

**Входные данные:**
```
frontend/data/v2/{book}/module{N}/sources/notes.pdf
```

**Выходные данные:**
```
frontend/data/v2/{book}/module{N}/glossary.json
```

**Справочник калькулятора:**
```
frontend/data/v2/calculator_templates.json
```

**Пример:**
```
frontend/data/v2/book1_quants/module1/sources/notes.pdf
    ↓
frontend/data/v2/book1_quants/module1/glossary.json
```

---

## ⚠️ АЛГОРИТМ СОЗДАНИЯ GLOSSARY (СТРОГО ОБЯЗАТЕЛЬНЫЙ)

### ШАГ 0: ПОЛНОЕ СКАНИРОВАНИЕ PDF

```
⚠️ КРИТИЧЕСКИ ВАЖНО ⚠️
Прочитать PDF ОТ НАЧАЛА ДО КОНЦА перед извлечением чего-либо!
НЕ останавливаться после первых страниц!
НЕ начинать извлечение пока не прочитан ВЕСЬ документ!
```

**Как проверить:** После чтения PDF должен быть известен последний LOS в документе.

---

### ШАГ 1: НАЙТИ ВСЕ LOS (REGEX СКАНИРОВАНИЕ)

**Команда:** Найти ВСЕ паттерны `LOS \d+[a-z]:` в документе.

**Пример для Module 1 "Rate and Return":**
```
Найдено: LOS 1a, LOS 1b, LOS 1c, LOS 1d, LOS 1e
Итого: 5 LOS
```

**Формат записи:**
```
los_list: ["LOS_1a", "LOS_1b", "LOS_1c", "LOS_1d", "LOS_1e"]
```

```
⛔ СТОП-ПРОВЕРКА #1:
Если найдено меньше 3 LOS — ОШИБКА СКАНИРОВАНИЯ!
Вернуться к ШАГ 0 и перечитать PDF полностью.
```

---

### ШАГ 2: ОПРЕДЕЛИТЬ ГРАНИЦЫ КАЖДОГО LOS

Для каждого LOS определить текстовый диапазон:

| LOS | Начало | Конец |
|-----|--------|-------|
| LOS_1a | Позиция "LOS 1a:" | Позиция "LOS 1b:" |
| LOS_1b | Позиция "LOS 1b:" | Позиция "LOS 1c:" |
| LOS_1c | Позиция "LOS 1c:" | Позиция "LOS 1d:" |
| LOS_1d | Позиция "LOS 1d:" | Позиция "LOS 1e:" |
| LOS_1e | Позиция "LOS 1e:" | Конец документа |

**Цель:** Гарантировать что ВЕСЬ текст документа покрыт и ни один LOS не пропущен.

---

### ШАГ 3: ИЗВЛЕЧЬ ТЕРМИНЫ ДЛЯ КАЖДОГО LOS

Для КАЖДОГО LOS из списка (ШАГ 1) в его границах (ШАГ 2):

1. Найти все термины (болд/выделенные)
2. Найти все формулы
3. Найти все названия метрик/показателей

**Что искать:**
- Термины выделенные **жирным**
- Названия формул (HPR, EAR, NPV, IRR...)
- Типы returns (Gross Return, Net Return, Real Return...)
- Типы rates (Nominal Rate, Real Rate...)
- Типы means (Arithmetic, Geometric, Harmonic, Trimmed, Winsorized...)
- Премии за риск (Default Premium, Liquidity Premium...)

```
⛔ СТОП-ПРОВЕРКА #2:
Каждый LOS должен иметь МИНИМУМ 1 термин.
Если у какого-то LOS 0 терминов — перечитать этот раздел PDF!
```

---

### ШАГ 4: ДОБАВИТЬ CALCULATOR ДЛЯ ТЕРМИНОВ С ФОРМУЛАМИ

См. раздел "ПРАВИЛО CALCULATOR" ниже.

---

### ШАГ 5: ФИНАЛЬНАЯ ПРОВЕРКА

```
ЧЕКЛИСТ ПЕРЕД СОХРАНЕНИЕМ:

□ Количество LOS в los_list совпадает с найденным в ШАГ 1
□ Каждый LOS имеет минимум 1 термин
□ Каждый термин с формулой имеет calculator (не null)
□ Нет терминов без los_id
□ term_id уникальны и последовательны
□ JSON валиден
```

---

## ⚠️ ПРАВИЛО CALCULATOR (СТРОГО ОБЯЗАТЕЛЬНОЕ)

| Условие | Действие | Пример |
|---------|----------|--------|
| Термин **БЕЗ** формулы | `"calculator": null` | Interest Rate, Liquidity Premium |
| Термин **С** формулой | `"calculator": { ... }` **ОБЯЗАТЕЛЕН** | HPR, EAR, Geometric Mean |

```
⛔ ЗАПРЕЩЕНО:
- Оставлять "calculator": null для термина с формулой
- Пропускать calculator для вычисляемых метрик
```

**Как определить нужен ли calculator:**
- Есть формула в поле `formula`? → calculator ОБЯЗАТЕЛЕН
- Есть слова "calculate", "compute", "formula" в определении? → calculator скорее всего нужен
- Термин концептуальный (определение, классификация)? → calculator: null

---

## ТИПЫ CALCULATOR (4 варианта)

### Тип 1: Ссылка на шаблон (template_id)

Если расчёт есть в `calculator_templates.json`:

```json
"calculator": {
  "template_id": "TVM_FV_single"
}
```

**Доступные шаблоны:**

| Категория | template_id | Описание |
|-----------|-------------|----------|
| TVM | `TVM_FV_single` | Future Value единовременной суммы |
| TVM | `TVM_PV_single` | Present Value единовременной суммы |
| TVM | `TVM_ordinary_annuity_PV` | PV обычного аннуитета |
| TVM | `TVM_ordinary_annuity_FV` | FV обычного аннуитета |
| TVM | `TVM_annuity_due_PV` | PV аннуитета пренумерандо |
| TVM | `TVM_perpetuity` | Перпетуитет |
| TVM | `TVM_loan_payment` | Платёж по кредиту |
| Cash Flow | `CF_NPV` | Чистая приведённая стоимость |
| Cash Flow | `CF_IRR` | Внутренняя норма доходности |
| Statistics | `STAT_mean` | Среднее арифметическое |
| Statistics | `STAT_std_dev_sample` | Выборочное стандартное отклонение |
| Statistics | `STAT_std_dev_population` | Популяционное стандартное отклонение |
| Bond | `BOND_price` | Цена облигации |
| Bond | `BOND_ytm` | Доходность к погашению |
| Direct | `DIRECT_HPR` | Holding Period Return |
| Direct | `DIRECT_geometric_mean` | Среднее геометрическое |
| Direct | `DIRECT_EAR` | Эффективная годовая ставка |
| Direct | `DIRECT_continuous_return` | Непрерывно начисляемая доходность |
| Amort | `AMORT_schedule` | График амортизации |

---

### Тип 2: Прямой расчёт (Direct Calculation)

Для простых формул, которых нет в шаблонах:

```json
"calculator": {
  "method": "Direct Calculation",
  "steps": [
    "{P1} [-] {P0} [+] {D1} [=]",
    "[÷] {P0} [=]"
  ],
  "example": {
    "given": "P0=$100, P1=$110, D1=$5",
    "input": "110 - 100 + 5 = ÷ 100 =",
    "result": "0.15 или 15%"
  }
}
```

**Формат кнопок:**
- Обычные: `[N]`, `[I/Y]`, `[PV]`, `[PMT]`, `[FV]`, `[CPT]`
- Второй регистр: `[2ND]`
- Математика: `[+]`, `[-]`, `[×]`, `[÷]`, `[=]`
- Знак: `[+/-]`
- Степень: `[yˣ]`
- Корень: `[2ND] [yˣ]` (для x√y)
- Логарифм: `[LN]`
- Экспонента: `[2ND] [LN]` (для eˣ)

---

### Тип 3: Пошаговый расчёт (Multi-step Calculation)

Для сложных формул с несколькими этапами:

```json
"calculator": {
  "method": "Multi-step Calculation",
  "description": "Расчёт MWRR через Cash Flow worksheet",
  "steps": [
    "Шаг 1: [CF] — войти в Cash Flow worksheet",
    "Шаг 2: [2ND] [CLR WORK] — очистить",
    "Шаг 3: Ввести CF0 (начальный отток, отрицательный)",
    "Шаг 4: [ENTER] [↓] — ввести каждый денежный поток",
    "Шаг 5: [IRR] [CPT] — рассчитать IRR"
  ],
  "example": {
    "given": "CF0=-1000, CF1=100, CF2=100, CF3=1100",
    "result": "IRR = 10%"
  }
}
```

---

### Тип 4: Нет калькулятора (null)

ТОЛЬКО для концептуальных терминов без вычислений:

```json
"calculator": null
```

**Примеры терминов с null:**
- Interest Rate (концепция)
- Real Risk-Free Rate (компонент, не вычисляется отдельно)
- Liquidity Premium (компонент)
- Gross Return vs Net Return (концептуальное различие)

---

## СТРУКТУРА glossary.json

```json
{
  "book_id": 1,
  "book_code": "QM",
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  
  "module_id": 1,
  "module_name": "Rate and Return",
  "module_name_ru": "Ставки и доходность",
  
  "los_list": ["LOS_1a", "LOS_1b", "LOS_1c", "LOS_1d", "LOS_1e"],
  "total_terms": 21,
  
  "terms": [
    {
      "term_id": "QM-1-001",
      "term_en": "English Term Name",
      "term_ru": "Русское название термина",
      "definition_en": "English definition...",
      "definition_ru": "Русское определение...",
      "formula": "$LaTeX formula$",
      "los_id": "LOS_1a",
      "calculator": { ... } или null
    }
  ]
}
```

---

## ПОЛЯ ТЕРМИНА

| Поле | Обязательное | Описание |
|------|--------------|----------|
| `term_id` | ✅ Да | Уникальный ID: `{BOOK_CODE}-{MODULE}-{NUMBER}` |
| `term_en` | ✅ Да | Название на английском |
| `term_ru` | ✅ Да | Название на русском |
| `definition_en` | ✅ Да | Определение на английском (2-3 предложения) |
| `definition_ru` | ✅ Да | Определение на русском (2-3 предложения) |
| `formula` | ⚠️ Если есть | LaTeX формула в `$...$` |
| `los_id` | ✅ Да | К какому LOS относится |
| `calculator` | ✅ Да | Объект с инструкциями ИЛИ `null` |

---

## ФОРМУЛЫ: ПРАВИЛА LaTeX

**Формат:** `$...$` для inline формул

**Примеры:**
```
$HPR = \frac{P_1 - P_0 + D_1}{P_0}$

$FV_N = PV \times (1 + r)^N$

$EAR = \left(1 + \frac{r_s}{m}\right)^m - 1$

$R_G = \sqrt[T]{\prod_{t=1}^{T}(1+R_t)} - 1$

$r_{continuous} = \ln\left(\frac{P_1}{P_0}\right)$
```

**Синтаксис:**
| Элемент | LaTeX | Результат |
|---------|-------|-----------|
| Дробь | `\frac{a}{b}` | a/b |
| Степень | `x^N` или `x^{mN}` | xⁿ |
| Индекс | `x_1` или `x_{t}` | x₁ |
| Корень | `\sqrt{x}` | √x |
| N-корень | `\sqrt[n]{x}` | ⁿ√x |
| Сумма | `\sum_{i=1}^{N}` | Σ |
| Произведение | `\prod_{t=1}^{T}` | Π |
| Скобки авто | `\left( \right)` | () с размером |
| Логарифм | `\ln(x)` | ln(x) |

---

## NAMING CONVENTIONS

### term_id
```
{BOOK_CODE}-{MODULE}-{NUMBER}
```
Примеры: `QM-1-001`, `QM-1-002`, `QM-2-001`, `EC-1-001`

Нумерация: 001, 002, 003... (с ведущими нулями)

### los_id
```
LOS_{module}{letter}
```
Примеры: `LOS_1a`, `LOS_1b`, `LOS_2a`, `LOS_12c`

### Book Codes

| Book | Code | book_id |
|------|------|---------|
| Quantitative Methods | QM | 1 |
| Economics | EC | 2 |
| Corporate Issuers | CI | 3 |
| Financial Statement Analysis | FSA | 4 |
| Equity Investments | EQ | 5 |
| Fixed Income | FI | 6 |
| Derivatives | DER | 7 |
| Alternative Investments | ALT | 8 |
| Portfolio Management | PM | 9 |
| Ethics | ETH | 10 |

---

## ЭТАЛОН: MODULE 1 "RATE AND RETURN"

Для проверки правильности работы алгоритма — Module 1 должен содержать:

### LOS_1a (Interpret interest rates) — 6 терминов:
1. Interest Rate — `calculator: null`
2. Real Risk-Free Rate — `calculator: null`
3. Inflation Premium — `calculator: null`
4. Default Risk Premium — `calculator: null`
5. Liquidity Premium — `calculator: null`
6. Maturity Risk Premium — `calculator: null`

### LOS_1b (Calculate and interpret returns) — 6 терминов:
7. Holding Period Return (HPR) — `calculator: DIRECT_HPR`
8. Arithmetic Mean Return — `calculator: STAT_mean`
9. Geometric Mean Return — `calculator: DIRECT_geometric_mean`
10. Harmonic Mean — `calculator: Direct Calculation`
11. Trimmed Mean — `calculator: Multi-step`
12. Winsorized Mean — `calculator: Multi-step`

### LOS_1c (MWRR vs TWRR) — 2 термина:
13. Money-Weighted Rate of Return (MWRR) — `calculator: CF_IRR`
14. Time-Weighted Rate of Return (TWRR) — `calculator: Multi-step`

### LOS_1d (Compounding) — 2 термина:
15. Effective Annual Rate (EAR) — `calculator: DIRECT_EAR`
16. Continuously Compounded Return — `calculator: DIRECT_continuous_return`

### LOS_1e (Types of returns) — 5 терминов:
17. Gross Return — `calculator: null`
18. Net Return — `calculator: null`
19. Real Return — `calculator: Direct Calculation` (формула есть)
20. Nominal Return — `calculator: null`
21. Leveraged Return — `calculator: Direct Calculation` (формула есть)

**ИТОГО: 5 LOS, 21 термин**

```
⛔ ПРОВЕРКА:
Если после обработки Module 1 получилось меньше 20 терминов — 
алгоритм сработал неправильно!
```

---

## ИЗВЕСТНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема: Формулы в PDF разваливаются при извлечении
**Решение:** Писать формулы вручную в LaTeX, ориентируясь на контекст и название термина

### Проблема: Claude Code останавливается после первых LOS
**Решение:** Обязательно выполнить ШАГ 0 и ШАГ 1 — сначала найти ВСЕ LOS, потом извлекать

### Проблема: Не понятно нужен ли calculator
**Решение:** Если есть `formula` — calculator ОБЯЗАТЕЛЕН. Нет формулы — null.

### Проблема: Сложные формулы не покрываются шаблонами
**Решение:** Использовать `"method": "Multi-step Calculation"`

---

## КОМАНДА ДЛЯ ЗАПУСКА

```
Создай glossary.json для [book]/[module].

СТРОГО следуй инструкции GLOSSARY_INSTRUCTION_v4.md:
1. ШАГ 0: Прочитай ВЕСЬ PDF от начала до конца
2. ШАГ 1: Найди ВСЕ паттерны "LOS \d[a-z]:" — запиши список
3. ШАГ 2: Определи границы каждого LOS
4. ШАГ 3: Извлеки термины для КАЖДОГО LOS
5. ШАГ 4: Добавь calculator для терминов с формулами
6. ШАГ 5: Проверь по чеклисту

Исходник: frontend/data/v2/[book]/[module]/sources/notes.pdf
Результат: frontend/data/v2/[book]/[module]/glossary.json
Шаблоны: frontend/data/v2/calculator_templates.json
```

---

## ФИНАЛЬНЫЙ ЧЕКЛИСТ

```
ПЕРЕД СОХРАНЕНИЕМ glossary.json ПРОВЕРИТЬ:

□ ШАГ 1 выполнен: все LOS найдены и записаны в los_list
□ ШАГ 2 выполнен: границы каждого LOS определены
□ ШАГ 3 выполнен: для каждого LOS есть минимум 1 термин
□ ШАГ 4 выполнен: каждый термин с formula имеет calculator
□ total_terms соответствует количеству терминов в массиве terms
□ Все term_id уникальны и последовательны (001, 002, 003...)
□ Все термины имеют los_id из los_list
□ JSON валиден (нет trailing commas, правильные кавычки)
```
