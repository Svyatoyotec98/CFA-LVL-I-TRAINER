# ЗАДАЧА: Новая архитектура глоссария с группировкой по LOS

## 🎯 ЦЕЛЬ
Переделать систему глоссария для поддержки:
1. Группировки терминов по LOS (Learning Outcome Statements)
2. Упражнений (exercises) внутри каждого LOS
3. Новой JSON структуры

## 📁 ФАЙЛЫ ДЛЯ РАБОТЫ

### Входные файлы (читать):
- `frontend/data/v2/glossary.json` — текущий глоссарий (старая структура)
- `frontend/app.js` — функции `loadGlossary()`, `displayGlossary()`, `searchGlossary()`
- `frontend/index.html` — секция glossary-screen

### Новые файлы (создать):
- `frontend/data/v2/glossary/book1_qm/glossary_module_1.json` — новый формат
- Обновить `frontend/app.js` — новая логика

### Эталонный файл (использовать как образец):
Файл `glossary_module_1_v2.json` который я прикрепляю ниже — это эталон новой структуры.

---

## 📐 НОВАЯ JSON СТРУКТУРА

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
    "version": "2.0"
  },
  "los": [
    {
      "los_id": "LOS_1a",
      "los_code": "1a",
      "los_description_en": "Interpret interest rates...",
      "los_description_ru": "Интерпретировать процентные ставки...",
      "terms": [
        {
          "term_id": "QM-1-001",
          "term_en": "Interest Rate",
          "term_ru": "Процентная ставка",
          "definition_en": "...",
          "definition_ru": "...",
          "type": "concept",
          "formula": null,
          "calculator": null
        }
      ],
      "exercises": [
        {
          "exercise_id": "QM-1-EX-001",
          "question_en": "Which of the following...",
          "question_ru": "Какой из следующих...",
          "options": [
            {"letter": "A", "text_en": "...", "text_ru": "..."},
            {"letter": "B", "text_en": "...", "text_ru": "..."},
            {"letter": "C", "text_en": "...", "text_ru": "..."}
          ],
          "correct_answer": "B",
          "solution_en": "...",
          "solution_ru": "..."
        }
      ]
    }
  ]
}
```

---

## 🔧 ИЗМЕНЕНИЯ В app.js

### 1. Новые переменные состояния (после строки 1036)

```javascript
// ============== Glossary ==============
let glossaryData = null;        // Полные данные глоссария
let glossaryTerms = [];         // Плоский список терминов для поиска
let glossaryExercises = [];     // Плоский список упражнений
let currentLosFilter = '';      // Текущий фильтр по LOS
let calculatorTemplates = {};
```

### 2. Новая функция loadGlossary() (заменить строки 1039-1048)

```javascript
async function loadGlossary() {
    try {
        // Загрузка через API (backend вернёт новую структуру)
        const data = await apiGet('/glossary/v2?book_id=1&module_id=1');
        glossaryData = data;
        
        // Создаём плоские списки для поиска и фильтрации
        glossaryTerms = [];
        glossaryExercises = [];
        
        if (data.los) {
            data.los.forEach(los => {
                // Добавляем LOS info к каждому термину
                los.terms.forEach(term => {
                    glossaryTerms.push({
                        ...term,
                        los_id: los.los_id,
                        los_code: los.los_code,
                        los_description_en: los.los_description_en,
                        module_id: data.metadata.module_id,
                        book_id: data.metadata.book_id
                    });
                });
                
                // Собираем упражнения
                if (los.exercises) {
                    los.exercises.forEach(ex => {
                        glossaryExercises.push({
                            ...ex,
                            los_id: los.los_id
                        });
                    });
                }
            });
        }
        
        // Обновляем фильтр LOS
        updateLosFilter(data.los || []);
        
        // Отображаем
        displayGlossaryByLos(data);
        
    } catch (error) {
        console.error('Failed to load glossary:', error);
        document.getElementById('glossary-list').innerHTML =
            '<p class="text-center text-muted">Ошибка загрузки глоссария</p>';
    }
}
```

### 3. Новая функция updateLosFilter()

```javascript
function updateLosFilter(losList) {
    const container = document.getElementById('glossary-los-filter');
    if (!container) return;
    
    container.innerHTML = `
        <option value="">Все LOS</option>
        ${losList.map(los => `
            <option value="${los.los_id}">${los.los_code}: ${los.los_description_en.substring(0, 50)}...</option>
        `).join('')}
    `;
}
```

### 4. Новая функция displayGlossaryByLos() (заменить displayGlossary)

```javascript
function displayGlossaryByLos(data) {
    const container = document.getElementById('glossary-list');
    const countEl = document.getElementById('glossary-count');
    
    if (!data || !data.los) {
        container.innerHTML = '<p class="text-center text-muted">Нет данных</p>';
        return;
    }
    
    // Подсчёт
    const totalTerms = data.los.reduce((sum, los) => sum + los.terms.length, 0);
    const totalExercises = data.los.reduce((sum, los) => sum + (los.exercises?.length || 0), 0);
    if (countEl) countEl.textContent = `${totalTerms} терминов • ${totalExercises} упражнений`;
    
    // Фильтрация по LOS если выбран
    let losToDisplay = data.los;
    if (currentLosFilter) {
        losToDisplay = data.los.filter(los => los.los_id === currentLosFilter);
    }
    
    // Рендер по LOS группам
    container.innerHTML = losToDisplay.map(los => `
        <div class="los-section" data-los-id="${los.los_id}">
            <div class="los-header" onclick="toggleLosSection(this)">
                <div class="los-title">
                    <span class="los-code">${los.los_code}</span>
                    <span class="los-description">${los.los_description_en}</span>
                </div>
                <div class="los-stats">
                    <span class="los-terms-count">${los.terms.length} терминов</span>
                    ${los.exercises?.length ? `<span class="los-exercises-count">${los.exercises.length} упражнений</span>` : ''}
                </div>
                <span class="los-toggle-icon">▼</span>
            </div>
            
            <div class="los-description-ru">${los.los_description_ru || ''}</div>
            
            <div class="los-content">
                <!-- Термины -->
                <div class="los-terms">
                    ${los.terms.map(term => renderGlossaryTerm(term, los)).join('')}
                </div>
                
                <!-- Упражнения -->
                ${los.exercises?.length ? `
                    <div class="los-exercises">
                        <h4 class="exercises-header">📝 Упражнения</h4>
                        ${los.exercises.map(ex => renderExercise(ex)).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
    
    // MathJax
    if (window.MathJax && MathJax.typesetPromise) {
        MathJax.typesetPromise([container]).catch(err => console.log('MathJax error:', err));
    }
}
```

### 5. Новая функция renderGlossaryTerm()

```javascript
function renderGlossaryTerm(term, los) {
    return `
        <div class="glossary-item" data-term-id="${term.term_id}">
            <div class="term-header">
                <div class="term-title">
                    <span class="term-name">${term.term_en}</span>
                    ${term.term_ru ? `<span class="term-name-ru">— ${term.term_ru}</span>` : ''}
                </div>
                <div class="term-badges">
                    <span class="term-type term-type-${term.type || 'concept'}">${term.type || 'concept'}</span>
                </div>
            </div>
            <div class="term-content">
                <div class="term-definition">${term.definition_en}</div>
                ${term.definition_ru ? `<div class="term-definition-ru">${term.definition_ru}</div>` : ''}
                ${term.formula ? `<div class="term-formula">\\(${term.formula.replace(/^\$|\$$/g, '')}\\)</div>` : ''}
                ${term.variables ? renderVariables(term.variables) : ''}
                ${term.calculator ? renderCalculatorSteps(term.calculator) : ''}
            </div>
        </div>
    `;
}
```

### 6. Новая функция renderVariables()

```javascript
function renderVariables(variables) {
    if (!variables || variables.length === 0) return '';
    
    return `
        <div class="term-variables">
            <strong>Переменные:</strong>
            <ul>
                ${variables.map(v => `
                    <li>
                        <span class="var-symbol">\\(${v.symbol}\\)</span>: 
                        ${v.name_en}
                        ${v.name_ru ? `<span class="var-name-ru">${v.name_ru}</span>` : ''}
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
}
```

### 7. Новая функция renderExercise()

```javascript
function renderExercise(exercise) {
    return `
        <div class="exercise-item" data-exercise-id="${exercise.exercise_id}">
            <div class="exercise-question">
                <span class="exercise-number">${exercise.exercise_id}</span>
                <p class="exercise-text-en">${exercise.question_en}</p>
                <p class="exercise-text-ru">${exercise.question_ru}</p>
            </div>
            
            <div class="exercise-options">
                ${exercise.options.map(opt => `
                    <button class="exercise-option" 
                            data-letter="${opt.letter}"
                            onclick="checkExerciseAnswer(this, '${exercise.exercise_id}', '${opt.letter}', '${exercise.correct_answer}')">
                        <span class="option-letter">${opt.letter}</span>
                        <span class="option-text">${opt.text_en}</span>
                        <span class="option-text-ru">${opt.text_ru}</span>
                    </button>
                `).join('')}
            </div>
            
            <div class="exercise-solution hidden" id="solution-${exercise.exercise_id}">
                <div class="solution-status"></div>
                <div class="solution-text">
                    <p>${exercise.solution_en}</p>
                    <p class="solution-ru">${exercise.solution_ru}</p>
                </div>
            </div>
        </div>
    `;
}
```

### 8. Новая функция checkExerciseAnswer()

```javascript
function checkExerciseAnswer(button, exerciseId, selectedLetter, correctLetter) {
    const container = button.closest('.exercise-item');
    const options = container.querySelectorAll('.exercise-option');
    const solutionDiv = document.getElementById(`solution-${exerciseId}`);
    const statusDiv = solutionDiv.querySelector('.solution-status');
    
    const isCorrect = selectedLetter === correctLetter;
    
    // Disable all options
    options.forEach(opt => {
        opt.disabled = true;
        const letter = opt.dataset.letter;
        
        if (letter === correctLetter) {
            opt.classList.add('correct');
        } else if (letter === selectedLetter && !isCorrect) {
            opt.classList.add('incorrect');
        }
    });
    
    // Show solution
    statusDiv.innerHTML = isCorrect 
        ? '<span class="result-correct">✓ Правильно!</span>'
        : `<span class="result-incorrect">✗ Неправильно. Правильный ответ: ${correctLetter}</span>`;
    
    solutionDiv.classList.remove('hidden');
}
```

### 9. Функция toggleLosSection()

```javascript
function toggleLosSection(headerEl) {
    const section = headerEl.closest('.los-section');
    section.classList.toggle('collapsed');
}
```

### 10. Обновить searchGlossary() (строки 1162-1181)

```javascript
function searchGlossary() {
    const query = document.getElementById('glossary-search').value.toLowerCase();
    const bookId = document.getElementById('glossary-book-filter').value;
    const losId = document.getElementById('glossary-los-filter')?.value || '';
    
    currentLosFilter = losId;
    
    if (!glossaryData) return;
    
    // Если есть поисковый запрос — ищем по плоскому списку
    if (query) {
        const filtered = glossaryTerms.filter(t =>
            t.term_en.toLowerCase().includes(query) ||
            (t.term_ru && t.term_ru.toLowerCase().includes(query)) ||
            t.definition_en.toLowerCase().includes(query)
        );
        displayFlatGlossary(filtered);
    } else {
        // Иначе показываем по LOS
        displayGlossaryByLos(glossaryData);
    }
}

// Для поиска — плоский список
function displayFlatGlossary(terms) {
    const container = document.getElementById('glossary-list');
    const countEl = document.getElementById('glossary-count');
    
    if (countEl) countEl.textContent = `${terms.length} результатов`;
    
    container.innerHTML = terms.map(term => `
        <div class="glossary-item" data-term-id="${term.term_id}">
            <div class="term-header">
                <div class="term-title">
                    <span class="term-name">${term.term_en}</span>
                    ${term.term_ru ? `<span class="term-name-ru">— ${term.term_ru}</span>` : ''}
                </div>
                <div class="term-badges">
                    ${term.los_id ? `<span class="term-los">${term.los_id}</span>` : ''}
                    ${term.module_id ? `<span class="term-module">M${term.module_id}</span>` : ''}
                </div>
            </div>
            <div class="term-content">
                <div class="term-definition">${term.definition_en}</div>
                ${term.definition_ru ? `<div class="term-definition-ru">${term.definition_ru}</div>` : ''}
                ${term.formula ? `<div class="term-formula">\\(${term.formula.replace(/^\$|\$$/g, '')}\\)</div>` : ''}
                ${term.calculator ? renderCalculatorSteps(term.calculator) : ''}
            </div>
        </div>
    `).join('');
    
    if (window.MathJax) MathJax.typeset([container]);
}
```

---

## 🎨 CSS СТИЛИ (добавить в styles.css)

```css
/* LOS Sections */
.los-section {
    margin-bottom: 2rem;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    overflow: hidden;
}

.los-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: rgba(255,255,255,0.05);
    cursor: pointer;
    transition: background 0.2s;
}

.los-header:hover {
    background: rgba(255,255,255,0.08);
}

.los-code {
    font-weight: 700;
    color: var(--primary);
    margin-right: 0.5rem;
    padding: 0.25rem 0.5rem;
    background: rgba(99, 102, 241, 0.2);
    border-radius: 4px;
}

.los-description {
    flex: 1;
    font-size: 0.9rem;
}

.los-description-ru {
    padding: 0.5rem 1.5rem;
    font-size: 0.85rem;
    color: var(--text-muted);
    font-style: italic;
    background: rgba(255,255,255,0.02);
}

.los-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.8rem;
    color: var(--text-muted);
}

.los-toggle-icon {
    transition: transform 0.2s;
}

.los-section.collapsed .los-toggle-icon {
    transform: rotate(-90deg);
}

.los-section.collapsed .los-content,
.los-section.collapsed .los-description-ru {
    display: none;
}

.los-content {
    padding: 1rem 1.5rem;
}

.los-terms {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* Exercises */
.los-exercises {
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.1);
}

.exercises-header {
    margin-bottom: 1rem;
    color: var(--primary);
}

.exercise-item {
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.exercise-question {
    margin-bottom: 1rem;
}

.exercise-number {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.exercise-text-en {
    font-weight: 500;
    margin: 0.5rem 0;
}

.exercise-text-ru {
    font-size: 0.9rem;
    color: var(--text-muted);
    font-style: italic;
}

.exercise-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.exercise-option {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
}

.exercise-option:hover:not(:disabled) {
    background: rgba(255,255,255,0.1);
    border-color: var(--primary);
}

.exercise-option.correct {
    background: rgba(34, 197, 94, 0.2);
    border-color: var(--success);
}

.exercise-option.incorrect {
    background: rgba(239, 68, 68, 0.2);
    border-color: var(--danger);
}

.option-letter {
    font-weight: 700;
    min-width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
}

.option-text {
    flex: 1;
}

.option-text-ru {
    display: block;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

.exercise-solution {
    margin-top: 1rem;
    padding: 1rem;
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
}

.solution-status {
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.solution-ru {
    color: var(--text-muted);
    font-style: italic;
    margin-top: 0.5rem;
}

/* Term type badges */
.term-type {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
}

.term-type-concept {
    background: rgba(59, 130, 246, 0.2);
    color: #60a5fa;
}

.term-type-formula {
    background: rgba(168, 85, 247, 0.2);
    color: #c084fc;
}

.term-type-method {
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
}

/* Variables */
.term-variables {
    margin-top: 0.75rem;
    padding: 0.75rem;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
    font-size: 0.9rem;
}

.term-variables ul {
    margin: 0.5rem 0 0 1rem;
    padding: 0;
}

.term-variables li {
    margin-bottom: 0.25rem;
}

.var-symbol {
    font-family: 'Times New Roman', serif;
    color: var(--primary);
}

.var-name-ru {
    display: block;
    font-size: 0.8rem;
    color: var(--text-muted);
    font-style: italic;
}
```

---

## 📝 ОБНОВИТЬ index.html

В секции glossary-screen добавить фильтр по LOS:

```html
<!-- После glossary-book-filter -->
<select id="glossary-los-filter" onchange="searchGlossary()">
    <option value="">Все LOS</option>
</select>
```

---

## ✅ ЧЕКЛИСТ

1. [ ] Создать ветку `feature/glossary-v2`
2. [ ] Скопировать `glossary_module_1_v2.json` в `frontend/data/v2/glossary/`
3. [ ] Обновить `app.js` — все функции выше
4. [ ] Добавить CSS стили
5. [ ] Обновить `index.html` — добавить LOS фильтр
6. [ ] Обновить backend endpoint `/glossary/v2` (если нужно)
7. [ ] Протестировать:
   - [ ] Отображение по LOS группам
   - [ ] Упражнения работают
   - [ ] Поиск работает
   - [ ] Фильтры работают
   - [ ] MathJax рендерит формулы
8. [ ] Создать PR

---

## 🔗 ПРИЛОЖЕНИЯ

К этой инструкции прикреплён файл `glossary_module_1_v2.json` — эталонная структура нового глоссария.
