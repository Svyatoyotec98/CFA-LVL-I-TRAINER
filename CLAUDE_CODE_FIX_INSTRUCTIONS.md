# ИНСТРУКЦИЯ ДЛЯ CLAUDE CODE: Исправление критических багов CFA Trainer

**Дата:** 13 января 2026  
**Приоритет:** КРИТИЧЕСКИЙ — блокирует подготовку к экзамену  
**Дедлайн экзамена:** 13 мая 2026 (120 дней)

---

## ОБЩАЯ СИТУАЦИЯ

Тренажёр CFA Level 1 имеет критические баги, которые делают его непригодным для учёбы. Нужно срочно исправить.

---

## БАГ 1: ТАБЛИЦЫ В ВОПРОСАХ НЕ ПАРСЯТСЯ (КРИТИЧЕСКИЙ)

### Проблема
При парсинге PDF вопросов таблицы полностью теряются. Вопрос становится нерешаемым.

### Пример
**В PDF (оригинал):**
```
Q.770 Rick Hassler earned the following annual rates of return by holding shares of XYZ Inc. for a period of five years:

Year     Return (%)
2011     13
2012     19
2013     -11
2014     25
2015     30

The share's holding period return over the five-year period is closest to:
A. 94%.
B. 21%.
C. 14%.
```

**В JSON (что получилось — НЕПРАВИЛЬНО):**
```json
{
  "question_text": "Rick Hassler earned the following annual rates of return by holding shares of XYZ Inc. for a period of five years: The share's holding period return over the five-year period is closest to:",
  "has_table": false
}
```

**Таблица с данными полностью потеряна!** Без неё вопрос невозможно решить.

### Решение
1. Переписать парсер PDF для корректного извлечения таблиц
2. Использовать `pdfplumber` с методом `extract_tables()` или `camelot-py`
3. Сохранять таблицы в поле `table_data` в JSON

### Формат хранения таблиц
```json
{
  "question_id": "QM-1-770",
  "question_text": "Rick Hassler earned the following annual rates of return by holding shares of XYZ Inc. for a period of five years:",
  "has_table": true,
  "table_data": {
    "headers": ["Year", "Return (%)"],
    "rows": [
      ["2011", "13"],
      ["2012", "19"],
      ["2013", "-11"],
      ["2014", "25"],
      ["2015", "30"]
    ]
  },
  "question_continuation": "The share's holding period return over the five-year period is closest to:"
}
```

### Отображение таблиц во frontend
В `app.js` добавить функцию рендеринга таблиц:
```javascript
function renderTable(tableData) {
    if (!tableData) return '';
    
    let html = '<table class="question-table">';
    
    // Headers
    html += '<thead><tr>';
    tableData.headers.forEach(h => {
        html += `<th>${h}</th>`;
    });
    html += '</tr></thead>';
    
    // Rows
    html += '<tbody>';
    tableData.rows.forEach(row => {
        html += '<tr>';
        row.forEach(cell => {
            html += `<td>${cell}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    
    return html;
}
```

---

## БАГ 2: ФОРМУЛЫ В ОБЪЯСНЕНИЯХ ОБРЕЗАЮТСЯ (КРИТИЧЕСКИЙ)

### Проблема
В объяснениях (explanation) формулы не сохраняются корректно — теряется LaTeX разметка.

### Пример
**В PDF:**
```
FVN = PV[1 + rs/m]^(mN) = $150,000[1 + 0.08/4]^12 = $150,000 × 1.268 = $190,236.27
```

**В JSON (НЕПРАВИЛЬНО):**
```json
"explanation": "The question requires the calculation of the Future Value of a lump sum with quarterly compounding as follows; Where; PV = Present value of the investment. rs = Annual interest rate. m = Quarterly compounding annually. mN = Total compounding for the investment period(4 x 3 years= 12 quarters) Therefore;"
```

**Сама формула с расчётом потеряна!**

### Решение
1. При парсинге сохранять формулы в LaTeX формате
2. Добавить поле `explanation_formula` для математических выражений
3. Использовать MathJax для рендеринга

### Формат
```json
{
  "explanation": "The question requires the calculation of the Future Value of a lump sum with quarterly compounding.",
  "explanation_formula": "$FV_N = PV \\left[1 + \\frac{r_s}{m}\\right]^{mN} = \\$150,000 \\left[1 + \\frac{0.08}{4}\\right]^{12} = \\$190,236.27$"
}
```

---

## БАГ 3: ГЛОССАРИЙ НЕПОЛНЫЙ (КРИТИЧЕСКИЙ)

### Проблема
Глоссарий содержит только 10 терминов для Book 1, хотя в PDF Notes их десятки.

### Текущее состояние (book1_terms.json)
Только 10 терминов:
1. Holding Period Return (HPR)
2. Effective Annual Rate (EAR)
3. Present Value (PV)
4. Future Value (FV)
5. Annuity
6. Perpetuity
7. Arithmetic Mean
8. Standard Deviation
9. Coefficient of Variation (CV)
10. Skewness

### Что должно быть (из PDF Notes)
**Learning Module 1: Rate and Return**
- Interest Rate (Required rate of return, Discount rate, Opportunity cost)
- Real Risk-free Interest Rate
- Inflation Premium
- Default Risk Premium
- Liquidity Premium  
- Maturity Premium
- Nominal Risk-free Interest Rate
- Holding Period Return (HPR)
- Arithmetic Mean / Arithmetic Return
- Geometric Mean / Geometric Return
- Harmonic Mean
- Trimmed Mean
- Winsorized Mean
- Money-weighted Rate of Return (MWRR / IRR)
- Time-weighted Rate of Return (TWRR)
- Effective Annual Rate (EAR)
- Continuously Compounded Return

**Learning Module 2: Time Value of Money**
- Present Value (PV)
- Future Value (FV)
- Annuity (Ordinary Annuity, Annuity Due)
- Perpetuity
- Net Present Value (NPV)
- Internal Rate of Return (IRR)

**И так далее для всех 11 модулей...**

### Решение
1. Перепарсить PDF Notes (CH-1-Quantitative_Methods.pdf)
2. Извлечь ВСЕ термины с определениями
3. Для каждого термина добавить:
   - Формулу (если есть)
   - **Инструкцию для калькулятора BA II Plus** (если применимо)

### Формат термина с калькулятором
```json
{
  "term_id": "T-QM-015",
  "term_en": "Net Present Value (NPV)",
  "term_ru": "Чистая приведённая стоимость",
  "definition_en": "The difference between the present value of cash inflows and the present value of cash outflows over a period of time.",
  "definition_ru": "Разница между приведённой стоимостью денежных поступлений и приведённой стоимостью денежных выплат за период времени.",
  "formula": "$NPV = \\sum_{t=0}^{n} \\frac{CF_t}{(1+r)^t}$",
  "calculator_steps": {
    "description": "Расчёт NPV на BA II Plus Professional",
    "steps": [
      "Нажмите [CF] для входа в Cash Flow worksheet",
      "Введите CF0 (начальные инвестиции, обычно отрицательное число), нажмите [ENTER], затем [↓]",
      "Введите C01 (денежный поток периода 1), нажмите [ENTER], затем [↓]",
      "Введите F01 (частота повторения C01, обычно 1), нажмите [ENTER], затем [↓]",
      "Повторите для всех денежных потоков C02, F02, C03, F03 и т.д.",
      "Нажмите [NPV]",
      "Введите I (ставка дисконтирования в %), нажмите [ENTER], затем [↓]",
      "Нажмите [CPT] для расчёта NPV"
    ],
    "example": {
      "problem": "Рассчитайте NPV проекта: CF0 = -$10,000, CF1 = $3,000, CF2 = $4,000, CF3 = $5,000, r = 10%",
      "keystrokes": [
        "[CF]",
        "10000 [+/-] [ENTER] [↓]",
        "3000 [ENTER] [↓]",
        "1 [ENTER] [↓]",
        "4000 [ENTER] [↓]",
        "1 [ENTER] [↓]",
        "5000 [ENTER] [↓]",
        "1 [ENTER]",
        "[NPV]",
        "10 [ENTER] [↓]",
        "[CPT]"
      ],
      "result": "NPV = $239.72"
    }
  },
  "module_id": 2,
  "related_los": ["LOS 2.d"]
}
```

---

## БАГ 4: НЕТ "ЛЁГКОГО РЕЖИМА" (НОВАЯ ФИЧА)

### Требование
Добавить режим, где после каждого ответа сразу показывается:
- Правильно / Неправильно
- Объяснение правильного ответа
- Объяснение почему другие варианты неправильны

### Текущее поведение
Объяснения показываются только в конце теста (после submit).

### Требуемое поведение
1. Пользователь выбирает вариант ответа
2. Нажимает "Проверить" (новая кнопка)
3. Сразу видит:
   - Зелёная подсветка правильного ответа
   - Красная подсветка если ответил неправильно
   - Блок с объяснением под вопросом
4. Кнопка "Далее" для перехода к следующему вопросу

### Реализация в app.js
```javascript
// Добавить переменную режима
let testMode = 'standard'; // 'standard', '90_second', 'learning'

// Функция проверки одного ответа (для learning mode)
function checkSingleAnswer() {
    const currentQ = testQuestions[currentQuestionIndex];
    const selectedOption = document.querySelector('.option.selected');
    
    if (!selectedOption) {
        alert('Выберите ответ');
        return;
    }
    
    const userAnswer = selectedOption.dataset.option;
    const isCorrect = userAnswer === currentQ.correct_answer;
    
    // Подсветка ответов
    document.querySelectorAll('.option').forEach(opt => {
        opt.classList.remove('selected');
        if (opt.dataset.option === currentQ.correct_answer) {
            opt.classList.add('correct');
        } else if (opt.dataset.option === userAnswer && !isCorrect) {
            opt.classList.add('incorrect');
        }
        opt.disabled = true;
    });
    
    // Показать объяснение
    showExplanation(currentQ, userAnswer, isCorrect);
    
    // Показать кнопку "Далее"
    document.getElementById('check-btn').classList.add('hidden');
    document.getElementById('next-btn').classList.remove('hidden');
}

function showExplanation(question, userAnswer, isCorrect) {
    const container = document.getElementById('explanation-container');
    
    let html = `<div class="explanation ${isCorrect ? 'correct' : 'incorrect'}">`;
    html += `<h4>${isCorrect ? '✓ Правильно!' : '✗ Неправильно'}</h4>`;
    html += `<p><strong>Правильный ответ:</strong> ${question.correct_answer}</p>`;
    html += `<p>${question.explanation}</p>`;
    
    // Показать формулу если есть
    if (question.explanation_formula) {
        html += `<div class="formula-container">${question.explanation_formula}</div>`;
    }
    
    // Показать почему выбранный ответ неправильный
    if (!isCorrect && question.explanation_wrong && question.explanation_wrong[userAnswer]) {
        html += `<p class="wrong-explanation"><strong>Почему ${userAnswer} неправильно:</strong> ${question.explanation_wrong[userAnswer]}</p>`;
    }
    
    // Показать шаги калькулятора если есть
    if (question.calculator_steps && question.calculator_steps.length > 0) {
        html += `<div class="calculator-steps">`;
        html += `<h5>🔢 Шаги на калькуляторе BA II Plus:</h5>`;
        html += `<ol>`;
        question.calculator_steps.forEach(step => {
            html += `<li><code>${step}</code></li>`;
        });
        html += `</ol></div>`;
    }
    
    html += `</div>`;
    
    container.innerHTML = html;
    container.classList.remove('hidden');
    
    // Перерендерить MathJax
    if (window.MathJax) {
        MathJax.typesetPromise([container]);
    }
}
```

### UI изменения в index.html
```html
<!-- В test-screen добавить -->
<div class="test-mode-selector">
    <button onclick="setTestMode('standard')" class="mode-btn active">Standard</button>
    <button onclick="setTestMode('90_second')" class="mode-btn">90 секунд</button>
    <button onclick="setTestMode('learning')" class="mode-btn">Обучение</button>
</div>

<!-- Контейнер для объяснения -->
<div id="explanation-container" class="hidden"></div>

<!-- Кнопки навигации -->
<div class="test-navigation">
    <button onclick="prevQuestion()" id="prev-btn">← Назад</button>
    <button onclick="checkSingleAnswer()" id="check-btn" class="hidden">Проверить</button>
    <button onclick="nextQuestion()" id="next-btn">Далее →</button>
    <button onclick="submitTest()" id="submit-btn" class="hidden">Завершить</button>
</div>
```

---

## БАГ 5: CALCULATOR_STEPS НЕКОРРЕКТНЫЕ

### Проблема
Поле `calculator_steps` содержит мусор вместо чётких инструкций.

### Пример (НЕПРАВИЛЬНО)
```json
"calculator_steps": [
  "PV = Initial investment amount.\nr = Interest rate compounded monthly.\nm = Interest periods.\nN = Investment period.\nTherefore"
]
```

### Как должно быть (ПРАВИЛЬНО)
```json
"calculator_steps": [
  "[2ND] [CLR TVM] — очистить TVM worksheet",
  "2000000 [+/-] [PV] — ввести начальную сумму (отрицательная)",
  "10 [÷] 12 [=] [I/Y] — ввести месячную ставку (10%/12)",
  "12 [N] — ввести количество периодов",
  "0 [PMT] — нет периодических платежей",
  "[CPT] [FV] — рассчитать будущую стоимость",
  "Результат: 2,209,426.14"
]
```

### Решение
При парсинге PDF искать паттерны:
- "Using the BA II Plus"
- "Using the financial calculator"
- Последовательности типа "PV=...; I/Y=...; N=...; CPT"

И преобразовывать их в пошаговые инструкции.

---

## ПЛАН ДЕЙСТВИЙ

### Приоритет 1 (сделать СЕГОДНЯ):
1. [ ] Исправить парсер для извлечения таблиц
2. [ ] Перепарсить ВСЕ PDF с вопросами заново
3. [ ] Добавить "Лёгкий режим" (learning mode)

### Приоритет 2 (сделать на этой неделе):
4. [ ] Перегенерировать глоссарий из PDF Notes
5. [ ] Добавить калькуляторные инструкции в глоссарий
6. [ ] Исправить calculator_steps в вопросах

### Приоритет 3 (сделать позже):
7. [ ] Добавить план обучения (100 тем / 120 дней)
8. [ ] Улучшить калькулятор-тренажёр

---

## СТРУКТУРА ФАЙЛОВ ДЛЯ ИЗМЕНЕНИЯ

```
cfa-trainer/
├── scripts/
│   ├── parse_pdf.py          # ПЕРЕПИСАТЬ — добавить извлечение таблиц
│   └── parse_glossary.py     # СОЗДАТЬ — парсинг глоссария из Notes PDF
├── frontend/
│   ├── index.html            # ИЗМЕНИТЬ — добавить learning mode UI
│   ├── js/
│   │   └── app.js            # ИЗМЕНИТЬ — добавить learning mode логику
│   ├── css/
│   │   └── styles.css        # ИЗМЕНИТЬ — стили для таблиц и объяснений
│   └── data/
│       ├── books/
│       │   └── book1.json    # ПЕРЕГЕНЕРИРОВАТЬ — с таблицами
│       └── glossary/
│           └── book1_terms.json  # ПЕРЕГЕНЕРИРОВАТЬ — полный глоссарий
```

---

## ТЕСТИРОВАНИЕ

После исправлений проверить:

1. **Таблицы:** Открыть вопрос Q.770 (Rick Hassler) — должна отображаться таблица с годами и процентами
2. **Объяснения:** В learning mode после ответа должно показываться полное объяснение с формулами
3. **Глоссарий:** Должно быть минимум 30+ терминов для Book 1 (вместо 10)
4. **Калькулятор:** В глоссарии термин NPV должен содержать пошаговую инструкцию для BA II Plus

---

**ВАЖНО:** Все изменения должны быть backward-compatible. Существующий прогресс пользователя не должен потеряться.
