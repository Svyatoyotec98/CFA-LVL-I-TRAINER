# GLOSSARY_INSTRUCTION.md
# Инструкция по созданию JSON глоссария из PDF Notes

**Версия:** 2.0 (Final)  
**Дата:** 13 января 2026

---

## ЦЕЛЬ

Создать JSON файлы с терминами и определениями для каждой книги CFA Level 1.

**Источник:** PDF файлы из `Materials/NOTES/`

---

## СТРУКТУРА ПРОЕКТА

```
CFA-LVL-I-TRAINER/
├── frontend/
│   └── data/
│       └── glossary/
│           ├── book1_terms.json    ← Quantitative Methods
│           ├── book2_terms.json    ← Economics
│           └── ...
├── Materials/
│   └── NOTES/                      ← Исходные PDF
└── backend/
    └── routers/
        └── glossary.py             ← Читает JSON, не менять
```

**Выходные файлы:** `frontend/data/glossary/book{N}_terms.json`

---

## СТРУКТУРА JSON ФАЙЛА

```json
{
  "book_id": 1,
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  "total_terms": 85,
  
  "terms": [
    {
      "term_id": "T-QM-001",
      "term_en": "Holding Period Return (HPR)",
      "term_ru": "Доходность за период владения",
      "definition_en": "The return earned from holding an asset for a specified period, calculated as the sum of price change and income received, divided by the beginning price.",
      "definition_ru": "Доходность от владения активом за определённый период, рассчитываемая как сумма изменения цены и полученного дохода, делённая на начальную цену.",
      "formula": "$HPR = \\frac{P_1 - P_0 + D}{P_0}$",
      "module_id": 1,
      "los_id": "LOS_1b",
      "related_terms": ["T-QM-002", "T-QM-015"],
      "calculator_steps": null
    },
    {
      "term_id": "T-QM-002",
      "term_en": "Effective Annual Rate (EAR)",
      "term_ru": "Эффективная годовая ставка",
      "definition_en": "The annual rate of return that accounts for the effect of compounding. It represents the true annual return when interest is compounded more frequently than once per year.",
      "definition_ru": "Годовая ставка доходности, учитывающая эффект начисления процентов. Представляет реальную годовую доходность при начислении процентов чаще одного раза в год.",
      "formula": "$EAR = \\left(1 + \\frac{r_s}{m}\\right)^m - 1$",
      "module_id": 1,
      "los_id": "LOS_1d",
      "related_terms": ["T-QM-003", "T-QM-004"],
      "calculator_steps": {
        "worksheet": "Interest Conversion",
        "access": "[2ND] [ICONV]",
        "steps": [
          "Ввести NOM (номинальную ставку) [ENTER]",
          "[↓] C/Y — ввести периоды начисления в год [ENTER]",
          "[↓] EFF — нажать [CPT]"
        ],
        "example": {
          "given": "Nominal rate 8%, quarterly compounding",
          "input": "NOM=8, C/Y=4",
          "result": "EFF = 8.24%"
        }
      }
    }
  ]
}
```

---

## ПРАВИЛА ИЗВЛЕЧЕНИЯ

### 1. Term ID
```
T-{BOOK_CODE}-{NUMBER}

Примеры:
T-QM-001   (Quants, термин #1)
T-QM-025   (Quants, термин #25)
T-FI-003   (Fixed Income, термин #3)
```

**Book Codes:**
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

### 2. Определения (КРИТИЧНО!)

**Требования:**
- `definition_en` — полное определение на английском (2-4 предложения)
- `definition_ru` — качественный перевод на русский
- НЕ копировать дословно из PDF — перефразировать для ясности
- Включать контекст использования термина

**Плохо:**
```json
"definition_en": "The return earned from holding an asset."
```

**Хорошо:**
```json
"definition_en": "The return earned from holding an asset for a specified period, calculated as the sum of price change and income received, divided by the beginning price. HPR captures total return including both capital gains and income."
```

### 3. Формулы

**Формат LaTeX:**
```json
"formula": "$HPR = \\frac{P_1 - P_0 + D}{P_0}$"
```

**Правила:**
- Использовать `$...$` для inline формул
- Экранировать backslash: `\\frac`, `\\sqrt`, `\\sum`
- Проверить рендеринг в MathJax

**Если формулы нет:**
```json
"formula": null
```

### 4. Module ID

Присваивать `module_id` на основе главы/раздела в PDF:

| Book 1 (Quants) | module_id |
|-----------------|-----------|
| Rate and Return | 1 |
| Time Value of Money | 2 |
| Statistical Measures | 3 |
| Probability Concepts | 4 |
| Common Probability Distributions | 5 |
| Sampling and Estimation | 6 |
| Hypothesis Testing | 7 |
| Linear Regression | 8 |
| Multiple Regression | 9 |
| Time Series Analysis | 10 |
| Big Data Techniques | 11 |

### 5. LOS ID

Связать термин с Learning Outcome Statement:
```json
"los_id": "LOS_1b"
```

Формат: `LOS_{module}_{letter}`

### 6. Calculator Steps

**Добавлять для терминов с вычислениями:**

```json
"calculator_steps": {
  "worksheet": "TVM | Cash Flow | Statistics | Interest Conversion | Bond",
  "access": "[2ND] [ICONV]",
  "steps": [
    "Шаг 1...",
    "Шаг 2..."
  ],
  "example": {
    "given": "Условие задачи",
    "input": "Что вводить",
    "result": "Результат"
  }
}
```

**Если калькулятор не нужен:**
```json
"calculator_steps": null
```

### 7. Related Terms

Связать с похожими терминами:
```json
"related_terms": ["T-QM-002", "T-QM-015"]
```

---

## СПИСОК ТЕРМИНОВ ПО КНИГАМ

### Book 1: Quantitative Methods (~85 терминов)

**Module 1: Rate and Return**
- Holding Period Return (HPR)
- Arithmetic Mean Return
- Geometric Mean Return
- Harmonic Mean
- Money-Weighted Return (MWRR)
- Time-Weighted Return (TWRR)
- Effective Annual Rate (EAR)
- Continuously Compounded Return
- Real Return
- Nominal Return
- Gross Return / Net Return
- Leveraged Return

**Module 2: Time Value of Money**
- Present Value (PV)
- Future Value (FV)
- Discount Rate
- Compounding
- Annuity
- Ordinary Annuity
- Annuity Due
- Perpetuity
- Net Present Value (NPV)
- Internal Rate of Return (IRR)

**Module 3: Statistical Measures**
- Mean / Median / Mode
- Range
- Variance
- Standard Deviation
- Coefficient of Variation (CV)
- Skewness
- Kurtosis
- Quartiles / Percentiles

**Module 4-7: Probability & Hypothesis Testing**
- Probability
- Expected Value
- Covariance
- Correlation
- Normal Distribution
- Z-Score
- Confidence Interval
- Null Hypothesis
- Type I Error / Type II Error
- P-Value
- T-Test

**Module 8-9: Regression**
- Simple Linear Regression
- Multiple Regression
- R-Squared
- Adjusted R-Squared
- Standard Error of Estimate
- F-Statistic
- Heteroskedasticity
- Multicollinearity

---

## ОЧИСТКА ОТ МУСОРА

При парсинге PDF удалять:
- `© AnalystPrep`
- Номера страниц
- Headers/footers
- "CFA Level I..."
- Пустые строки

---

## ЧЕКЛИСТ

### Контент
- [ ] Все ключевые термины из Notes извлечены
- [ ] `term_id` уникальны
- [ ] `definition_en` полные (2-4 предложения)
- [ ] `definition_ru` качественно переведены
- [ ] Формулы в LaTeX корректны
- [ ] `module_id` присвоен правильно

### Структура
- [ ] JSON валиден
- [ ] Все поля заполнены (или null)
- [ ] `calculator_steps` для расчётных терминов

### Проверка
- [ ] Формулы рендерятся в MathJax
- [ ] Фронт отображает термины корректно
- [ ] Поиск работает по EN и RU

---

## ПРИМЕР ПОЛНОГО ТЕРМИНА

```json
{
  "term_id": "T-QM-006",
  "term_en": "Internal Rate of Return (IRR)",
  "term_ru": "Внутренняя норма доходности (ВНД)",
  "definition_en": "The discount rate that makes the net present value (NPV) of all cash flows equal to zero. IRR represents the expected compound annual rate of return on an investment. It is used to evaluate the attractiveness of a project or investment.",
  "definition_ru": "Ставка дисконтирования, при которой чистая приведённая стоимость (NPV) всех денежных потоков равна нулю. IRR представляет ожидаемую сложную годовую доходность инвестиции. Используется для оценки привлекательности проекта или инвестиции.",
  "formula": "$\\sum_{t=0}^{n} \\frac{CF_t}{(1+IRR)^t} = 0$",
  "module_id": 1,
  "los_id": "LOS_1e",
  "related_terms": ["T-QM-005", "T-QM-003"],
  "calculator_steps": {
    "worksheet": "Cash Flow",
    "access": "[CF]",
    "steps": [
      "[CF] — открыть Cash Flow worksheet",
      "[2ND] [CLR WORK] — очистить данные",
      "CF0: ввести начальные инвестиции (со знаком минус) [ENTER]",
      "[↓] C01: ввести первый денежный поток [ENTER]",
      "[↓] F01: ввести частоту (обычно 1) [ENTER]",
      "Повторить для всех CF",
      "[IRR] [CPT] — рассчитать IRR"
    ],
    "example": {
      "given": "Initial investment $10,000, annual cash flows $3,000 for 5 years",
      "input": "CF0=-10000, C01=3000, F01=5",
      "result": "IRR = 15.24%"
    }
  }
}
```
