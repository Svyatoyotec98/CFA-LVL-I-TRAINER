# Анализ: Module 1 vs QBANK_INSTRUCTION_v2.md

**Дата:** 14 января 2026
**Цель:** Выявить расхождения между фактической структурой Module 1 (работает отлично) и инструкцией QBANK_INSTRUCTION_v2.md (дает плохие результаты)

---

## 🔴 КРИТИЧЕСКИЕ РАСХОЖДЕНИЯ

### 1. СТРУКТУРА JSON FIELDS

| Поле | Module 1 (ФАКТ) | Instruction (ТЕОРИЯ) | Статус |
|------|----------------|---------------------|---------|
| **question_id** | `"QM-1-013"` | `"Q-QM-1-013"` | ❌ РАЗНЫЕ |
| **question_number** | `13` (integer) | Нет такого поля | ❌ НЕТ В ИНСТРУКЦИИ |
| **original_number** | Нет такого поля | `"Q.13"` (string) | ❌ НЕТ В MODULE 1 |
| **los_reference** | `"LOS 1d"` | `"LOS (d): full text..."` | ❌ РАЗНЫЕ ФОРМАТЫ |
| **los_id** | Нет такого поля | `"LOS_1d"` | ❌ НЕТ В MODULE 1 |

### 2. OPTIONS STRUCTURE

**Module 1:**
```json
"options": [
  {
    "id": "opt1",  // <--- "id", не "option_id"!
    "text": "$188,956.80"
  }
]
```

**Instruction:**
```json
"options": [
  {
    "option_id": "opt1",  // <--- "option_id"!
    "text": "...",
    "text_ru": "..."
  }
]
```

**Проблема:** Разные названия полей (`id` vs `option_id`)

### 3. EXPLANATION STRUCTURE (САМОЕ ВАЖНОЕ!)

**Module 1 — ПЛОСКАЯ структура:**
```json
{
  "explanation": "FV with quarterly compounding: FV = PV[1 + rs/m]^(mN) = ...",  // STRING!
  "explanation_ru": "FV с квартальным начислением.",
  "explanation_formula": "$FV_N = PV \\left[1 + \\frac{r_s}{m}\\right]^{mN} = ...$",  // ОТДЕЛЬНОЕ ПОЛЕ!
  "explanation_wrong": {  // ОТДЕЛЬНОЕ ПОЛЕ на верхнем уровне!
    "opt1": {
      "text": "FV with annual compounding instead of quarterly.",
      "formula": "$FV = \\$150,000(1.08)^3 = \\$188,956.80$"
    }
  }
}
```

**Instruction — ВЛОЖЕННАЯ структура:**
```json
{
  "explanation": {  // OBJECT, не STRING!
    "main": "...",
    "main_ru": "...",
    "formula": "...",
    "formula_latex": "...",  // ВНУТРИ explanation!
    "solution_steps": ["..."],
    "wrong_answers": {  // ВНУТРИ explanation как "wrong_answers", не "explanation_wrong"!
      "opt1": {
        "reason": "...",
        "reason_ru": "...",
        "calculation": "..."
      }
    },
    "calculator_steps": {...}  // ВНУТРИ explanation!
  }
}
```

**Проблема:** Полностью разная архитектура данных!

### 4. CALCULATOR_STEPS STRUCTURE

**Module 1:**
```json
"calculator_steps": [  // МАССИВ СТРОК!
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

**Instruction:**
```json
"calculator_steps": {  // ОБЪЕКТ!
  "applicable": true,
  "calculator_model": "BA II Plus Professional",
  "method": "TVM Worksheet",
  "preparation": ["..."],
  "keystrokes": ["..."],  // МАССИВ ВНУТРИ ОБЪЕКТА!
  "display_result": "...",
  "alternative_method": {...},
  "note": "..."
}
```

**Проблема:** Module 1 использует простой массив строк, инструкция — сложный объект

---

## 🟡 ФОРМАТ PDF (AnalystPrep)

### ФАКТИЧЕСКАЯ СТРУКТУРА PDF:

```
Q.8
[Question text: "If you invest $100,000 currently..."]

The correct answer is C.    ← ОТВЕТ ИДЕТ ПЕРВЫМ!

[Explanation text]
A is incorrect. [formula]
B is incorrect. [formula]

A. $108,000.00    ← ОПЦИИ ИДУТ ПОСЛЕ ОБЪЯСНЕНИЯ!
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

### ЧТО ОЖИДАЕТ ИНСТРУКЦИЯ:

```python
# Инструкция предполагает такой порядок:
pattern = r'(Q\.\d+.*?)(?=Q\.\d+|$)'
# Ожидается: Question → Options → "The correct answer"
```

**Проблема:** AnalystPrep PDF имеет порядок:
```
Question → "The correct answer is X" → Explanation → Options
```

А инструкция ожидает:
```
Question → Options → "The correct answer is X" → Explanation
```

---

## 📊 CHECKPOINT COMPLIANCE

### Module 1: ❌ НЕ СЛЕДОВАЛ ИНСТРУКЦИИ

- ✅ Нет CHECKPOINT 1 коммита
- ✅ Нет CHECKPOINT 2 коммита
- ✅ Нет CHECKPOINT 3 коммита
- ✅ Нет CHECKPOINT 4 коммита
- ✅ Нет файлов extracted/{chapter}_raw.txt
- ✅ Нет файлов extracted/{chapter}_split.json

**Вывод:** Module 1 был создан ВРУЧНУЮ или другим методом, НЕ по QBANK_INSTRUCTION_v2.md!

### Module 2: ✅ СЛЕДОВАЛ ИНСТРУКЦИИ

- ✅ CHECKPOINT 1: Extract raw text from ch2_module2
- ✅ CHECKPOINT 2: Split into 32 questions
- ✅ CHECKPOINT 3: Format questions 1-15
- ✅ CHECKPOINT 4: Complete ch2_module2 QBank
- ✅ Файлы extracted/ch2_module2_raw.txt
- ✅ Файлы extracted/ch2_module2_split.json

**Результат:** Плохое качество парсинга (87% dirty question_text, 78% dirty options)

---

## 🔍 ПАРАДОКС

**ИНСТРУКЦИЯ БЫЛА НАПИСАНА НА ОСНОВЕ MODULE 1, НО MODULE 1 НЕ СОЗДАВАЛСЯ ПО ЭТОЙ ИНСТРУКЦИИ!**

Это объясняет:
1. Почему структура JSON не совпадает
2. Почему парсинг Module 2 провалился
3. Почему инструкция не работает

---

## ✅ ПРАВИЛЬНАЯ СТРУКТУРА (Module 1)

```json
{
  "question_id": "QM-1-013",
  "question_number": 13,
  "question_text": "Clean question text WITHOUT 'The correct answer is'",
  "question_text_ru": "Russian translation",
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
  "explanation": "Short text explanation",
  "explanation_ru": "Russian",
  "explanation_formula": "LaTeX formula as separate field",
  "explanation_wrong": {
    "opt1": {"text": "Why wrong", "formula": "Wrong calc"},
    "opt2": {"text": "Why wrong", "formula": "Wrong calc"}
  },
  "requires_calculation": true,
  "calculator_steps": [
    "[2ND] [CLR TVM]",
    "150000 [+/-] [PV]",
    "[CPT] [FV] → 190,236.27"
  ],
  "difficulty": "MEDIUM",
  "los_reference": "LOS 1d",
  "topic_tags": ["FV", "compounding", "quarterly", "TVM"]
}
```

---

## 🎯 РЕКОМЕНДАЦИИ

### 1. Переписать QBANK_INSTRUCTION_v2.md

**Задача:** Сделать инструкцию соответствующей РЕАЛЬНОЙ структуре Module 1

**Изменить:**
- ❌ Убрать вложенную структуру explanation
- ✅ Использовать плоскую структуру с отдельными полями
- ✅ options с полем "id", не "option_id"
- ✅ calculator_steps как массив строк
- ✅ question_number вместо original_number
- ✅ Убрать префикс "Q-" из question_id

### 2. Создать правильный парсер для AnalystPrep PDF

**Проблемы:**
```python
# НЕПРАВИЛЬНО (текущий подход):
q_match = re.search(rf'Q\.{q_num}\s+(.*?)The\s+correct\s+answer', raw, re.DOTALL)

# ПРАВИЛЬНО для AnalystPrep:
q_match = re.search(rf'Q\.{q_num}\s+(.*?)(?=The\s+correct\s+answer)', raw, re.DOTALL)
```

**Порядок извлечения для AnalystPrep:**
1. Question text (до "The correct answer is")
2. Correct answer letter (после "The correct answer is")
3. Explanation (после answer letter, до options)
4. Options A/B/C (в конце)
5. Formulas (разбросаны, надо очищать)

### 3. Создать автоматизированный скрипт

**Требования:**
- ✅ Работает с AnalystPrep PDF форматом
- ✅ Создает структуру как у Module 1
- ✅ Очищает question_text от "The correct answer is"
- ✅ Очищает options от формул
- ✅ Извлекает полные объяснения
- ✅ Парсит calculator steps

---

## 🗂️ РАСПОЛОЖЕНИЕ МАТЕРИАЛОВ

### ❌ Инструкция указывает НЕПРАВИЛЬНЫЙ путь:
```
Materials/QBank/{Book_Name}/Chapters/{chapter_file}.pdf
```

### ✅ Реальное расположение:
```
Materials/QBank/Tests/{Book_Name}/Chapters/{chapter_file}.pdf
```

### Доступные материалы:
- **Quants**: 11 PDF (CH-1-Quantitative_Methods-Answers-3-39.pdf, 40-75.pdf, и т.д.)
- **FSA**: 12 PDF
- **Economics**: 7 PDF
- **Ethics**: 5 PDF
- **Full tests**: По 1 полному PDF на каждую тему

### Module 2 был создан из:
```
Materials/QBank/Tests/Quants/Chapters/Copy of CH-1-Quantitative_Methods-Answers-40-75.pdf
```
(32 вопроса: Q.8 - Q.3410)

---

## 📝 СЛЕДУЮЩИЕ ШАГИ

1. **Создать `QBANK_INSTRUCTION_v3.md`** — с правильной структурой Module 1 + правильными путями
2. **Создать `analystprep_parser.py`** — специализированный парсер для AnalystPrep PDF
3. **Пересоздать Module 2** — используя новый парсер
4. **Создать шаблон** — готовый к параллельному использованию

**Цель:** Автоматизация, которая не требует ручного вмешательства и дает качество как у Module 1.
