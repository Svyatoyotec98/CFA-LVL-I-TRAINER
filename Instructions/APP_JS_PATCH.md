# APP_JS_PATCH.md
# Изменения в app.js для новой структуры options

**Дата:** 13 января 2026

---

## ОБЗОР ИЗМЕНЕНИЙ

Переход с:
```json
"options": {"A": "text1", "B": "text2", "C": "text3"},
"correct_answer": "C"
```

На:
```json
"options": [
  {"id": "opt1", "text": "text1"},
  {"id": "opt2", "text": "text2"},
  {"id": "opt3", "text": "text3"}
],
"correct_option_id": "opt3"
```

---

## ИЗМЕНЕНИЕ 1: displayQuestion() 

**Файл:** `frontend/js/app.js`  
**Строки:** ~502-513

**БЫЛО:**
```javascript
// Options
const optionsContainer = document.getElementById('options-container');
optionsContainer.innerHTML = Object.entries(question.options).map(([letter, text]) => {
    const isSelected = state.answers[question.question_id] === letter;
    return `
        <button class="option ${isSelected ? 'selected' : ''}"
                onclick="selectAnswer('${letter}')">
            <span class="option-letter">${letter}</span>
            ${text}
        </button>
    `;
}).join('');
```

**СТАЛО:**
```javascript
// Options - shuffle и отображение без букв
const optionsContainer = document.getElementById('options-container');
const shuffledOptions = shuffleArray(question.options);

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
```

---

## ИЗМЕНЕНИЕ 2: selectAnswer()

**Строки:** ~546-558

**БЫЛО:**
```javascript
function selectAnswer(letter) {
    const question = state.questions[state.currentQuestionIndex];
    state.answers[question.question_id] = letter;

    // Update button states
    document.querySelectorAll('.option').forEach(btn => {
        btn.classList.remove('selected');
        if (btn.querySelector('.option-letter').textContent === letter) {
            btn.classList.add('selected');
        }
    });

    updateQuestionDots();

    // In 90-second mode, show result immediately
    if (state.testMode === '90_second') {
        showQuestionResult(question, letter);
    }
}
```

**СТАЛО:**
```javascript
function selectAnswer(optionId) {
    const question = state.questions[state.currentQuestionIndex];
    state.answers[question.question_id] = optionId;

    // Update button states
    document.querySelectorAll('.option').forEach(btn => {
        btn.classList.remove('selected');
        if (btn.dataset.optionId === optionId) {
            btn.classList.add('selected');
        }
    });

    updateQuestionDots();

    // In 90-second mode, show result immediately
    if (state.testMode === '90_second') {
        showQuestionResult(question, optionId);
    }
}
```

---

## ИЗМЕНЕНИЕ 3: showQuestionResult()

**Строки:** ~566-640

**БЫЛО:**
```javascript
function showQuestionResult(question, userAnswer) {
    const isCorrect = userAnswer === question.correct_answer;

    // Highlight correct/incorrect options
    document.querySelectorAll('.option').forEach(btn => {
        const letter = btn.querySelector('.option-letter').textContent;
        btn.disabled = true;
        if (letter === question.correct_answer) {
            btn.classList.add('correct');
        } else if (letter === userAnswer && !isCorrect) {
            btn.classList.add('incorrect');
        }
    });

    // Show explanation
    const expContainer = document.getElementById('explanation-container');

    // Result status
    const statusEl = document.getElementById('explanation-status');
    if (statusEl) {
        statusEl.innerHTML = isCorrect
            ? '<span class="result-correct">✓ Правильно!</span>'
            : '<span class="result-incorrect">✗ Неправильно</span>';
        statusEl.innerHTML += `<span class="correct-answer">Правильный ответ: ${question.correct_answer}</span>`;
    }

    document.getElementById('explanation-text').textContent = question.explanation || '';

    // ...rest of function...

    // Wrong answer explanation
    const wrongEl = document.getElementById('explanation-wrong');
    if (wrongEl) {
        if (!isCorrect && question.explanation_wrong && question.explanation_wrong[userAnswer]) {
            wrongEl.innerHTML = `<strong>Почему ${userAnswer} неправильно:</strong> ${question.explanation_wrong[userAnswer]}`;
            wrongEl.classList.remove('hidden');
        } else {
            wrongEl.classList.add('hidden');
        }
    }

    // Calculator steps
    const calcStepsContainer = document.getElementById('calculator-steps');
    if (calcStepsContainer) {
        if (question.calculator_steps && question.calculator_steps.length > 0) {
            document.getElementById('calc-steps-list').innerHTML =
                question.calculator_steps.map(step => `<li><code>${step}</code></li>`).join('');
            calcStepsContainer.classList.remove('hidden');
        } else {
            calcStepsContainer.classList.add('hidden');
        }
    }

    expContainer.classList.remove('hidden');
}
```

**СТАЛО:**
```javascript
function showQuestionResult(question, userAnswer) {
    const isCorrect = userAnswer === question.correct_option_id;

    // Найти текст правильного ответа для отображения
    const correctOption = question.options.find(opt => opt.id === question.correct_option_id);
    const correctText = correctOption ? correctOption.text : '';

    // Highlight correct/incorrect options
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
    const expContainer = document.getElementById('explanation-container');

    // Result status
    const statusEl = document.getElementById('explanation-status');
    if (statusEl) {
        statusEl.innerHTML = isCorrect
            ? '<span class="result-correct">✓ Правильно!</span>'
            : '<span class="result-incorrect">✗ Неправильно</span>';
        statusEl.innerHTML += `<span class="correct-answer">Правильный ответ: ${correctText}</span>`;
    }

    document.getElementById('explanation-text').textContent = question.explanation || '';

    // Explanation formula
    const formulaEl = document.getElementById('explanation-formula');
    if (formulaEl) {
        if (question.explanation_formula) {
            formulaEl.innerHTML = question.explanation_formula;
            formulaEl.classList.remove('hidden');
            if (window.MathJax) {
                MathJax.typesetPromise([formulaEl]).catch(err => console.log('MathJax error:', err));
            }
        } else {
            formulaEl.classList.add('hidden');
        }
    }

    // Wrong answer explanation (новая структура)
    const wrongEl = document.getElementById('explanation-wrong');
    if (wrongEl) {
        const wrongExplanation = question.explanation_wrong?.[userAnswer];
        if (!isCorrect && wrongExplanation) {
            let wrongHtml = `<strong>Почему ваш ответ неправильный:</strong> `;
            
            // Поддержка старой (строка) и новой (объект) структуры
            if (typeof wrongExplanation === 'string') {
                wrongHtml += wrongExplanation;
            } else {
                wrongHtml += wrongExplanation.text || wrongExplanation.text_ru || '';
                if (wrongExplanation.formula) {
                    wrongHtml += `<div class="wrong-formula">${wrongExplanation.formula}</div>`;
                }
            }
            
            wrongEl.innerHTML = wrongHtml;
            wrongEl.classList.remove('hidden');
            
            // Render formula if present
            if (window.MathJax) {
                MathJax.typesetPromise([wrongEl]).catch(err => console.log('MathJax error:', err));
            }
        } else {
            wrongEl.classList.add('hidden');
        }
    }

    // Calculator steps
    const calcStepsContainer = document.getElementById('calculator-steps');
    if (calcStepsContainer) {
        if (question.calculator_steps && question.calculator_steps.length > 0) {
            document.getElementById('calc-steps-list').innerHTML =
                question.calculator_steps.map(step => `<li><code>${step}</code></li>`).join('');
            calcStepsContainer.classList.remove('hidden');
        } else {
            calcStepsContainer.classList.add('hidden');
        }
    }

    expContainer.classList.remove('hidden');

    // In learning mode, show next button after checking
    if (state.testMode === 'learning') {
        const checkBtn = document.getElementById('check-btn');
        const nextBtn = document.getElementById('next-btn');
        if (checkBtn) checkBtn.classList.add('hidden');
        if (nextBtn) nextBtn.classList.remove('hidden');
    }
}
```

---

## ИЗМЕНЕНИЕ 4: loadReviewQuestions() 

**Строки:** ~935-970

**БЫЛО:**
```javascript
container.innerHTML = `
    <h3>Вопросы для повторения (${data.total_due})</h3>
    <div class="review-questions">
        ${data.questions.map(q => `
            <div class="review-question glass-container">
                <p>${q.question.question_text}</p>
                <div class="options-container">
                    ${Object.entries(q.question.options).map(([letter, text]) => `
                        <button class="option" onclick="answerReview('${q.question_id}', '${letter}', '${q.question.correct_answer}')">
                            <span class="option-letter">${letter}</span> ${text}
                        </button>
                    `).join('')}
                </div>
            </div>
        `).join('')}
    </div>
`;
```

**СТАЛО:**
```javascript
container.innerHTML = `
    <h3>Вопросы для повторения (${data.total_due})</h3>
    <div class="review-questions">
        ${data.questions.map(q => `
            <div class="review-question glass-container">
                <p>${q.question.question_text}</p>
                <div class="options-container">
                    ${q.question.options.map(opt => `
                        <button class="option" 
                                data-option-id="${opt.id}"
                                onclick="answerReview('${q.question_id}', '${opt.id}', '${q.question.correct_option_id}')">
                            ${opt.text}
                        </button>
                    `).join('')}
                </div>
            </div>
        `).join('')}
    </div>
`;
```

---

## ИЗМЕНЕНИЕ 5: answerReview()

**Строки:** ~972-986

**БЫЛО:**
```javascript
async function answerReview(questionId, userAnswer, correctAnswer) {
    const wasCorrect = userAnswer === correctAnswer;
    // ...
}
```

**Остаётся без изменений** — функция уже работает с любыми строками.

---

## ИЗМЕНЕНИЕ 6: calculateResults() (если есть)

Убедиться, что при подсчёте результатов используется `correct_option_id`:

```javascript
function calculateResults() {
    let correct = 0;
    state.questions.forEach(q => {
        if (state.answers[q.question_id] === q.correct_option_id) {
            correct++;
        }
    });
    return correct;
}
```

---

## ИЗМЕНЕНИЕ 7: CSS (опционально)

Убрать стили для `.option-letter` если больше не нужны:

```css
/* УДАЛИТЬ или закомментировать */
.option-letter {
    display: inline-flex;
    /* ... */
}
```

---

## BACKWARDS COMPATIBILITY

Если нужна поддержка старых JSON во время миграции:

```javascript
function getOptions(question) {
    // Новый формат (массив)
    if (Array.isArray(question.options)) {
        return question.options;
    }
    
    // Старый формат (объект A/B/C)
    return Object.entries(question.options).map(([letter, text], index) => ({
        id: `opt${index + 1}`,
        text: text,
        _originalLetter: letter  // для обратной совместимости
    }));
}

function getCorrectOptionId(question) {
    // Новый формат
    if (question.correct_option_id) {
        return question.correct_option_id;
    }
    
    // Старый формат — конвертируем A→opt1, B→opt2, C→opt3
    const letterToOpt = {'A': 'opt1', 'B': 'opt2', 'C': 'opt3', 'D': 'opt4'};
    return letterToOpt[question.correct_answer] || 'opt1';
}
```

---

## ТЕСТИРОВАНИЕ

После внесения изменений проверить:

1. [ ] Вопросы отображаются без букв A/B/C
2. [ ] Options перемешиваются при каждом показе
3. [ ] Выбор ответа работает
4. [ ] Правильный/неправильный подсвечиваются корректно
5. [ ] Объяснение показывает правильный текст ответа
6. [ ] Объяснение неверного ответа работает
7. [ ] Calculator steps отображаются
8. [ ] Review questions работают
9. [ ] Результаты теста считаются правильно
