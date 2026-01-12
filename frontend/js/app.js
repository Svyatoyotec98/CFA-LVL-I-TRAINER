/**
 * CFA Level 1 Trainer - Main Application
 */

// ============== Configuration ==============
const API_URL = 'http://localhost:8001/api';
const EXAM_DATE = new Date('2026-05-13');

// ============== State ==============
let state = {
    user: null,
    token: localStorage.getItem('cfa_token'),
    currentScreen: 'landing',
    currentBook: null,
    currentModule: null,
    currentTest: null,
    testMode: null,
    questions: [],
    currentQuestionIndex: 0,
    answers: {},
    flaggedQuestions: new Set(),
    testStartTime: null,
    questionStartTime: null,
    timerInterval: null,
    booksData: {},
    progress: {}
};

// ============== Screen Management ==============
const screens = [
    'landing', 'login', 'register', 'dashboard', 'books', 'modules',
    'test-mode', 'test', 'results', 'mock-exam', 'calculator',
    'review', 'glossary', 'statistics'
];

function hideAllScreens() {
    screens.forEach(screen => {
        const el = document.getElementById(`${screen}-screen`);
        if (el) el.classList.add('hidden');
    });
}

function showScreen(screenName) {
    hideAllScreens();
    const screen = document.getElementById(`${screenName}-screen`);
    if (screen) {
        screen.classList.remove('hidden');
        state.currentScreen = screenName;
        window.scrollTo(0, 0);

        // Screen-specific initialization
        switch(screenName) {
            case 'dashboard':
                loadDashboard();
                break;
            case 'books':
                loadBooks();
                break;
            case 'modules':
                loadModules();
                break;
            case 'glossary':
                loadGlossary();
                break;
            case 'statistics':
                loadStatistics();
                break;
            case 'review':
                loadReviewQuestions();
                break;
            case 'calculator':
                loadCalculatorProblem();
                break;
        }
    }
}

// ============== Authentication ==============
async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        showLoading();
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        state.token = data.access_token;
        localStorage.setItem('cfa_token', data.access_token);

        await loadUser();
        showScreen('dashboard');
        showToast('Успешный вход!', 'success');
    } catch (error) {
        errorDiv.textContent = error.message;
    } finally {
        hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const password2 = document.getElementById('reg-password2').value;
    const errorDiv = document.getElementById('register-error');

    if (password !== password2) {
        errorDiv.textContent = 'Пароли не совпадают';
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        showToast('Регистрация успешна! Теперь войдите.', 'success');
        showScreen('login');
    } catch (error) {
        errorDiv.textContent = error.message;
    } finally {
        hideLoading();
    }
}

async function loadUser() {
    if (!state.token) return;

    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });

        if (!response.ok) {
            throw new Error('Session expired');
        }

        state.user = await response.json();
        document.getElementById('user-name').textContent = state.user.username;
        document.getElementById('welcome-name').textContent = state.user.username;
    } catch (error) {
        logout();
    }
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('cfa_token');
    showScreen('landing');
    showToast('Вы вышли из системы', 'success');
}

// ============== API Helpers ==============
async function apiGet(endpoint) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        headers: { 'Authorization': `Bearer ${state.token}` }
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API Error');
    }
    return response.json();
}

async function apiPost(endpoint, data) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${state.token}`
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API Error');
    }
    return response.json();
}

// ============== Dashboard ==============
async function loadDashboard() {
    try {
        const progress = await apiGet('/progress');
        state.progress = progress;

        // Update stats
        document.getElementById('stat-questions').textContent = progress.total_questions_seen || 0;
        const accuracy = progress.total_questions_seen > 0
            ? Math.round((progress.total_questions_correct / progress.total_questions_seen) * 100)
            : 0;
        document.getElementById('stat-correct').textContent = `${accuracy}%`;
        document.getElementById('overall-percent').textContent = `${Math.round(progress.overall_mastery || 0)}%`;
        document.getElementById('overall-progress-bar').style.width = `${progress.overall_mastery || 0}%`;
        document.getElementById('books-progress').style.width = `${progress.overall_mastery || 0}%`;

        // Load test count
        try {
            const history = await apiGet('/tests/history?limit=100');
            document.getElementById('stat-tests').textContent = history.length || 0;
        } catch (e) {
            document.getElementById('stat-tests').textContent = '0';
        }

        // Load review count
        try {
            const review = await apiGet('/errors/review');
            document.getElementById('review-count').textContent = `${review.total_due || 0} вопросов к повторению`;
        } catch (e) {
            document.getElementById('review-count').textContent = '0 вопросов к повторению';
        }
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// ============== Books ==============
const BOOKS = [
    { id: 1, name: 'Quantitative Methods', name_ru: 'Количественные методы', questions: 350 },
    { id: 2, name: 'Economics', name_ru: 'Экономика', questions: 350 },
    { id: 3, name: 'Financial Statement Analysis', name_ru: 'Анализ финансовой отчётности', questions: 400 },
    { id: 4, name: 'Corporate Issuers', name_ru: 'Корпоративные эмитенты', questions: 250 },
    { id: 5, name: 'Equity Investments', name_ru: 'Инвестиции в акции', questions: 350 },
    { id: 6, name: 'Fixed Income', name_ru: 'Фиксированный доход', questions: 400 },
    { id: 7, name: 'Derivatives', name_ru: 'Деривативы', questions: 300 },
    { id: 8, name: 'Alternative Investments', name_ru: 'Альтернативные инвестиции', questions: 200 },
    { id: 9, name: 'Portfolio Management', name_ru: 'Управление портфелем', questions: 350 },
    { id: 10, name: 'Ethics', name_ru: 'Этика', questions: 350 }
];

async function loadBooks() {
    const container = document.getElementById('books-list');
    let progressData = {};

    try {
        const progress = await apiGet('/progress');
        progress.books_progress?.forEach(bp => {
            progressData[bp.book_id] = bp;
        });
    } catch (e) {
        console.error('Failed to load progress:', e);
    }

    container.innerHTML = BOOKS.map(book => {
        const bp = progressData[book.id] || {};
        const mastery = bp.total_questions_seen > 0
            ? Math.round((bp.total_questions_correct / bp.total_questions_seen) * 100)
            : 0;

        return `
            <div class="book-card" onclick="selectBook(${book.id})">
                <div class="book-number">Book ${book.id}</div>
                <div class="book-name">${book.name}</div>
                <div class="book-name-ru text-muted">${book.name_ru}</div>
                <div class="book-stats">${bp.total_questions_seen || 0} / ${book.questions} вопросов</div>
                <div class="progress-bar small">
                    <div style="width: ${mastery}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

function selectBook(bookId) {
    state.currentBook = BOOKS.find(b => b.id === bookId);
    showScreen('modules');
}

// ============== Modules ==============
async function loadModules() {
    if (!state.currentBook) {
        showScreen('books');
        return;
    }

    document.getElementById('current-book-name').textContent = state.currentBook.name;
    const container = document.getElementById('modules-list');

    // Load book data from JSON
    try {
        const bookData = await loadBookData(state.currentBook.id);
        const modules = bookData.learning_modules || [];

        // Get progress
        let progressData = {};
        try {
            const progress = await apiGet(`/progress/book/${state.currentBook.id}`);
            progress.modules?.forEach(m => {
                progressData[m.module_id] = m;
            });
        } catch (e) {
            console.error('Failed to load module progress:', e);
        }

        container.innerHTML = modules.map((module, index) => {
            const mp = progressData[module.module_id] || {};
            const isUnlocked = index === 0 || mp.is_unlocked || (progressData[modules[index-1]?.module_id]?.mastery_percent >= 80);
            const questionsCount = module.questions?.length || 0;
            const mastery = mp.mastery_percent || 0;

            return `
                <div class="module-card ${isUnlocked ? '' : 'locked'}"
                     onclick="${isUnlocked ? `selectModule(${module.module_id}, '${module.module_name.replace(/'/g, "\\'")}')` : ''}">
                    ${!isUnlocked ? '<span class="lock-icon">🔒</span>' : ''}
                    <div class="module-number">Module ${module.module_id}</div>
                    <div class="module-name">${module.module_name}</div>
                    ${module.module_name_ru ? `<div class="text-muted">${module.module_name_ru}</div>` : ''}
                    <div class="module-stats">${questionsCount} вопросов • ${Math.round(mastery)}% mastery</div>
                    <div class="progress-bar small">
                        <div style="width: ${mastery}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        container.innerHTML = '<p class="text-center text-muted">Данные для этой книги пока недоступны</p>';
        console.error('Failed to load modules:', error);
    }
}

async function loadBookData(bookId) {
    if (state.booksData[bookId]) {
        return state.booksData[bookId];
    }

    try {
        const response = await fetch(`data/books/book${bookId}.json`);
        if (!response.ok) throw new Error('Book data not found');
        const data = await response.json();
        state.booksData[bookId] = data;
        return data;
    } catch (error) {
        console.error(`Failed to load book ${bookId}:`, error);
        throw error;
    }
}

function selectModule(moduleId, moduleName) {
    state.currentModule = { id: moduleId, name: moduleName };
    document.getElementById('test-module-name').textContent = moduleName;

    // Get questions count
    const bookData = state.booksData[state.currentBook.id];
    const module = bookData?.learning_modules?.find(m => m.module_id === moduleId);
    const count = module?.questions?.length || 0;
    document.getElementById('test-questions-count').textContent = `${count} вопросов`;

    showScreen('test-mode');
}

// ============== Test ==============
async function startTest(mode) {
    state.testMode = mode;
    state.currentQuestionIndex = 0;
    state.answers = {};
    state.flaggedQuestions = new Set();
    state.testStartTime = Date.now();

    try {
        showLoading();
        // Load questions from API or local data
        const bookData = state.booksData[state.currentBook.id];
        const module = bookData?.learning_modules?.find(m => m.module_id === state.currentModule.id);
        state.questions = shuffleArray([...(module?.questions || [])]);

        if (state.questions.length === 0) {
            throw new Error('Нет вопросов для этого модуля');
        }

        document.getElementById('test-total').textContent = state.questions.length;

        // Setup navigation dots
        const dotsContainer = document.getElementById('question-dots');
        dotsContainer.innerHTML = state.questions.map((_, i) =>
            `<div class="question-dot" onclick="goToQuestion(${i})" data-index="${i}"></div>`
        ).join('');

        // Configure based on mode
        if (mode === '90_second') {
            document.getElementById('prev-btn').classList.add('hidden');
            document.getElementById('flag-btn').classList.add('hidden');
        } else {
            document.getElementById('prev-btn').classList.remove('hidden');
            document.getElementById('flag-btn').classList.remove('hidden');
        }

        showScreen('test');
        displayQuestion();
        startTimer();
    } catch (error) {
        showToast(error.message, 'error');
        showScreen('modules');
    } finally {
        hideLoading();
    }
}

function displayQuestion() {
    const question = state.questions[state.currentQuestionIndex];
    if (!question) return;

    state.questionStartTime = Date.now();

    document.getElementById('q-num').textContent = state.currentQuestionIndex + 1;
    document.getElementById('test-current').textContent = state.currentQuestionIndex + 1;
    document.getElementById('question-text').textContent = question.question_text;

    // Formula
    const formulaDiv = document.getElementById('question-formula');
    if (question.question_text_formula) {
        formulaDiv.innerHTML = question.question_text_formula;
        formulaDiv.classList.remove('hidden');
        if (window.MathJax) MathJax.typeset([formulaDiv]);
    } else {
        formulaDiv.classList.add('hidden');
    }

    // Difficulty
    const diffDiv = document.getElementById('q-difficulty');
    if (question.difficulty) {
        diffDiv.textContent = question.difficulty;
        diffDiv.className = `question-difficulty ${question.difficulty}`;
    } else {
        diffDiv.textContent = '';
    }

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

    // Update dots
    updateQuestionDots();

    // Update navigation
    document.getElementById('prev-btn').disabled = state.currentQuestionIndex === 0;

    const isLastQuestion = state.currentQuestionIndex === state.questions.length - 1;
    document.getElementById('next-btn').textContent = isLastQuestion ? 'Завершить' : 'Далее →';

    // Hide explanation for new question
    document.getElementById('explanation-container').classList.add('hidden');
}

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

function showQuestionResult(question, userAnswer) {
    const isCorrect = userAnswer === question.correct_answer;

    // Highlight correct/incorrect options
    document.querySelectorAll('.option').forEach(btn => {
        const letter = btn.querySelector('.option-letter').textContent;
        if (letter === question.correct_answer) {
            btn.classList.add('correct');
        } else if (letter === userAnswer && !isCorrect) {
            btn.classList.add('incorrect');
        }
    });

    // Show explanation
    const expContainer = document.getElementById('explanation-container');
    document.getElementById('explanation-text').textContent = question.explanation || '';

    if (question.explanation_wrong && question.explanation_wrong[userAnswer]) {
        document.getElementById('explanation-wrong').textContent = question.explanation_wrong[userAnswer];
    } else {
        document.getElementById('explanation-wrong').textContent = '';
    }

    // Calculator steps
    if (question.calculator_steps && question.calculator_steps.length > 0) {
        document.getElementById('calc-steps-list').innerHTML =
            question.calculator_steps.map(step => `<li>${step}</li>`).join('');
        document.getElementById('calculator-steps').classList.remove('hidden');
    } else {
        document.getElementById('calculator-steps').classList.add('hidden');
    }

    expContainer.classList.remove('hidden');
}

function updateQuestionDots() {
    document.querySelectorAll('.question-dot').forEach((dot, i) => {
        dot.classList.remove('current', 'answered', 'flagged');

        if (i === state.currentQuestionIndex) {
            dot.classList.add('current');
        }

        const q = state.questions[i];
        if (q && state.answers[q.question_id]) {
            dot.classList.add('answered');
        }

        if (state.flaggedQuestions.has(i)) {
            dot.classList.add('flagged');
        }
    });
}

function prevQuestion() {
    if (state.currentQuestionIndex > 0) {
        state.currentQuestionIndex--;
        displayQuestion();
    }
}

function nextQuestion() {
    if (state.currentQuestionIndex < state.questions.length - 1) {
        state.currentQuestionIndex++;
        displayQuestion();

        // Reset timer for 90-second mode
        if (state.testMode === '90_second') {
            state.questionStartTime = Date.now();
        }
    } else {
        // Last question - submit test
        submitTest();
    }
}

function goToQuestion(index) {
    if (state.testMode === 'standard' && index >= 0 && index < state.questions.length) {
        state.currentQuestionIndex = index;
        displayQuestion();
    }
}

function flagQuestion() {
    if (state.flaggedQuestions.has(state.currentQuestionIndex)) {
        state.flaggedQuestions.delete(state.currentQuestionIndex);
    } else {
        state.flaggedQuestions.add(state.currentQuestionIndex);
    }
    updateQuestionDots();
}

function startTimer() {
    if (state.timerInterval) clearInterval(state.timerInterval);

    const timerEl = document.getElementById('test-timer');

    if (state.testMode === '90_second') {
        // 90 seconds per question
        state.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - state.questionStartTime) / 1000);
            const remaining = 90 - elapsed;

            if (remaining >= 0) {
                timerEl.textContent = formatTime(remaining);
                timerEl.classList.remove('negative', 'warning');
                if (remaining <= 30) timerEl.classList.add('warning');
            } else {
                timerEl.textContent = '-' + formatTime(Math.abs(remaining));
                timerEl.classList.add('negative');
            }
        }, 1000);
    } else {
        // Total time for standard mode
        state.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - state.testStartTime) / 1000);
            timerEl.textContent = formatTime(elapsed);
        }, 1000);
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

async function submitTest() {
    if (state.timerInterval) clearInterval(state.timerInterval);

    const timeSpent = Math.floor((Date.now() - state.testStartTime) / 1000);

    // Calculate results
    const questionDetails = state.questions.map(q => ({
        question_id: q.question_id,
        user_answer: state.answers[q.question_id] || null,
        correct_answer: q.correct_answer,
        correct: state.answers[q.question_id] === q.correct_answer,
        time_spent: 0 // TODO: track per-question time
    }));

    const correct = questionDetails.filter(q => q.correct).length;
    const total = state.questions.length;
    const scorePercent = Math.round((correct / total) * 100);

    // Submit to API
    try {
        await apiPost('/tests/submit', {
            test_type: 'module',
            test_mode: state.testMode,
            book_id: state.currentBook.id,
            module_id: state.currentModule.id,
            time_spent_seconds: timeSpent,
            question_details: questionDetails
        });
    } catch (error) {
        console.error('Failed to submit test:', error);
    }

    // Show results
    showResults(correct, total, timeSpent, questionDetails);
}

function showResults(correct, total, timeSpent, details) {
    const scorePercent = Math.round((correct / total) * 100);

    // Update score circle
    const circle = document.getElementById('score-circle');
    circle.style.background = `conic-gradient(${scorePercent >= 70 ? 'var(--success)' : 'var(--danger)'} ${scorePercent * 3.6}deg, var(--glass-bg) 0deg)`;

    document.getElementById('score-value').textContent = `${scorePercent}%`;
    document.getElementById('correct-count').textContent = correct;
    document.getElementById('incorrect-count').textContent = total - correct;
    document.getElementById('time-spent').textContent = formatTime(timeSpent);

    // Score message
    const msgEl = document.getElementById('score-message');
    if (scorePercent >= 80) {
        msgEl.textContent = 'Отлично! Модуль разблокирован!';
    } else if (scorePercent >= 70) {
        msgEl.textContent = 'Хороший результат!';
    } else if (scorePercent >= 50) {
        msgEl.textContent = 'Нужно ещё поработать';
    } else {
        msgEl.textContent = 'Требуется повторение материала';
    }

    // Question review
    const reviewContainer = document.getElementById('questions-review');
    reviewContainer.innerHTML = details.map((d, i) => {
        const q = state.questions[i];
        return `
            <div class="review-item ${d.correct ? 'correct' : 'incorrect'}">
                <div><strong>Q${i + 1}:</strong> ${q.question_text.substring(0, 100)}...</div>
                <div class="text-muted">
                    Ваш ответ: ${d.user_answer || 'Не отвечено'} |
                    Правильный: ${d.correct_answer}
                </div>
            </div>
        `;
    }).join('');

    showScreen('results');
}

function retryTest() {
    startTest(state.testMode);
}

// ============== Mock Exam ==============
async function startMockExam() {
    try {
        showLoading();
        const questions = await apiGet('/tests/mock-exam');

        state.currentBook = { id: 0, name: 'Mock Exam' };
        state.currentModule = { id: 0, name: 'Mock Exam' };
        state.questions = questions;
        state.testMode = '90_second';
        state.currentQuestionIndex = 0;
        state.answers = {};
        state.flaggedQuestions = new Set();
        state.testStartTime = Date.now();

        document.getElementById('test-total').textContent = questions.length;

        const dotsContainer = document.getElementById('question-dots');
        dotsContainer.innerHTML = questions.map((_, i) =>
            `<div class="question-dot" onclick="goToQuestion(${i})" data-index="${i}"></div>`
        ).join('');

        showScreen('test');
        displayQuestion();
        startTimer();
    } catch (error) {
        showToast('Не удалось загрузить Mock Exam', 'error');
    } finally {
        hideLoading();
    }
}

// ============== Calculator ==============
let currentCalcProblem = null;

async function loadCalculatorProblem() {
    const type = document.getElementById('calc-type-select').value;

    try {
        const data = await apiGet(`/calculator/problems/${type}?limit=1`);
        if (data.problems && data.problems.length > 0) {
            currentCalcProblem = data.problems[0];
            displayCalculatorProblem(currentCalcProblem);
        } else {
            document.getElementById('calc-problem-text').textContent = 'Нет доступных задач';
        }
    } catch (error) {
        console.error('Failed to load calculator problem:', error);
        document.getElementById('calc-problem-text').textContent = 'Ошибка загрузки задачи';
    }
}

function displayCalculatorProblem(problem) {
    document.getElementById('calc-worksheet').textContent = problem.worksheet;
    document.getElementById('calc-problem-text').textContent = problem.problem_text;

    const givenDiv = document.getElementById('calc-given');
    givenDiv.innerHTML = Object.entries(problem.given)
        .map(([k, v]) => `<div>${k} = ${v}</div>`)
        .join('');

    document.getElementById('calc-find').textContent = problem.find;
    document.getElementById('calc-answer-input').value = '';
    document.getElementById('calc-result').classList.add('hidden');
}

async function checkCalculatorAnswer() {
    if (!currentCalcProblem) return;

    const userAnswer = parseFloat(document.getElementById('calc-answer-input').value);
    if (isNaN(userAnswer)) {
        showToast('Введите числовой ответ', 'warning');
        return;
    }

    try {
        const result = await apiPost('/calculator/check', {
            problem_id: currentCalcProblem.problem_id,
            user_answer: userAnswer,
            time_spent_seconds: 0
        });

        const resultDiv = document.getElementById('calc-result');
        document.getElementById('calc-result-status').innerHTML = result.is_correct
            ? '<span style="color: var(--success)">Правильно!</span>'
            : '<span style="color: var(--danger)">Неправильно</span>';

        document.getElementById('calc-correct-answer').textContent =
            `Правильный ответ: ${result.correct_answer}`;

        document.getElementById('calc-solution-steps').innerHTML =
            '<h5>Решение:</h5><ol>' +
            result.steps.map(s => `<li>${s}</li>`).join('') +
            '</ol>';

        resultDiv.classList.remove('hidden');
    } catch (error) {
        showToast('Ошибка проверки ответа', 'error');
    }
}

// ============== Review (Spaced Repetition) ==============
async function loadReviewQuestions() {
    const container = document.getElementById('review-content');

    try {
        const data = await apiGet('/errors/review');

        if (data.questions && data.questions.length > 0) {
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
        } else {
            container.innerHTML = `
                <div class="text-center">
                    <h3>Нет вопросов для повторения</h3>
                    <p class="text-muted">Все вопросы повторены. Отличная работа!</p>
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = '<p class="text-center text-muted">Ошибка загрузки</p>';
    }
}

async function answerReview(questionId, userAnswer, correctAnswer) {
    const wasCorrect = userAnswer === correctAnswer;

    try {
        await apiPost('/errors/mark-reviewed', {
            question_id: questionId,
            was_correct: wasCorrect
        });

        showToast(wasCorrect ? 'Правильно!' : 'Неправильно', wasCorrect ? 'success' : 'error');
        loadReviewQuestions();
    } catch (error) {
        showToast('Ошибка', 'error');
    }
}

// ============== Glossary ==============
let glossaryTerms = [];

async function loadGlossary() {
    try {
        const data = await apiGet('/glossary');
        glossaryTerms = data.terms || [];
        displayGlossary(glossaryTerms);
    } catch (error) {
        document.getElementById('glossary-list').innerHTML =
            '<p class="text-center text-muted">Ошибка загрузки глоссария</p>';
    }
}

function displayGlossary(terms) {
    const container = document.getElementById('glossary-list');
    container.innerHTML = terms.map(term => `
        <div class="glossary-item">
            <div class="term-name">${term.term_en}</div>
            ${term.term_ru ? `<div class="term-name-ru">${term.term_ru}</div>` : ''}
            <div class="term-definition">${term.definition_en}</div>
            ${term.definition_ru ? `<div class="term-definition-ru">${term.definition_ru}</div>` : ''}
            ${term.formula ? `<div class="term-formula">\\(${term.formula.replace(/^\$|\$$/g, '')}\\)</div>` : ''}
            ${term.calculator_steps ? `
                <div class="calculator-instructions">
                    <div class="calc-header" onclick="toggleCalcSteps(this)">
                        <span>🖩 BA II Plus: ${term.calculator_steps.worksheet}</span>
                        <span class="toggle-icon">▼</span>
                    </div>
                    <div class="calc-steps hidden">
                        <ol>
                            ${term.calculator_steps.steps.map(step => `<li>${step}</li>`).join('')}
                        </ol>
                        ${term.calculator_steps.example ? `<div class="calc-example"><strong>Пример:</strong> ${term.calculator_steps.example}</div>` : ''}
                    </div>
                </div>
            ` : ''}
        </div>
    `).join('');

    // MathJax render with retry for async loading
    if (window.MathJax && MathJax.typesetPromise) {
        MathJax.typesetPromise([container]).catch(err => console.log('MathJax error:', err));
    } else {
        setTimeout(() => {
            if (window.MathJax) MathJax.typeset([container]);
        }, 500);
    }
}

function toggleCalcSteps(header) {
    const steps = header.nextElementSibling;
    const icon = header.querySelector('.toggle-icon');
    steps.classList.toggle('hidden');
    icon.textContent = steps.classList.contains('hidden') ? '▼' : '▲';
}

function searchGlossary() {
    const query = document.getElementById('glossary-search').value.toLowerCase();
    const filtered = glossaryTerms.filter(t =>
        t.term_en.toLowerCase().includes(query) ||
        (t.term_ru && t.term_ru.toLowerCase().includes(query)) ||
        t.definition_en.toLowerCase().includes(query)
    );
    displayGlossary(filtered);
}

function filterGlossary() {
    const bookId = document.getElementById('glossary-book-filter').value;
    const filtered = bookId
        ? glossaryTerms.filter(t => t.book_id == bookId)
        : glossaryTerms;
    displayGlossary(filtered);
}

// ============== Statistics ==============
async function loadStatistics() {
    try {
        const [progress, history, errorStats] = await Promise.all([
            apiGet('/progress'),
            apiGet('/tests/history?limit=20'),
            apiGet('/errors/stats')
        ]);

        // Overall stats
        document.getElementById('overall-stats').innerHTML = `
            <div class="stat-item">
                <span class="stat-value">${progress.total_questions_seen || 0}</span>
                <span class="stat-label">Вопросов изучено</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${Math.round(progress.overall_mastery || 0)}%</span>
                <span class="stat-label">Общий прогресс</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${errorStats.total_errors || 0}</span>
                <span class="stat-label">Ошибок</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${errorStats.mastered || 0}</span>
                <span class="stat-label">Усвоено</span>
            </div>
        `;

        // Books stats
        document.getElementById('books-stats').innerHTML = BOOKS.map(book => {
            const bp = progress.books_progress?.find(p => p.book_id === book.id) || {};
            const mastery = bp.total_questions_seen > 0
                ? Math.round((bp.total_questions_correct / bp.total_questions_seen) * 100)
                : 0;
            return `
                <div class="book-stat-item">
                    <span>${book.name}</span>
                    <span>${mastery}%</span>
                </div>
            `;
        }).join('');

        // Test history
        document.getElementById('test-history').innerHTML = history.map(t => `
            <div class="history-item">
                <span>${t.test_type} - ${new Date(t.created_at).toLocaleDateString()}</span>
                <span>${Math.round(t.score_percent)}%</span>
            </div>
        `).join('') || '<p class="text-muted">Нет истории тестов</p>';

    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

// ============== Utilities ==============
function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

function updateCountdown() {
    const now = new Date();
    const diff = EXAM_DATE - now;

    if (diff > 0) {
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        document.getElementById('countdown').textContent = `${days} дней до экзамена`;
    }
}

// ============== Initialization ==============
async function init() {
    updateCountdown();
    setInterval(updateCountdown, 86400000); // Update daily

    if (state.token) {
        try {
            await loadUser();
            showScreen('dashboard');
        } catch (error) {
            showScreen('landing');
        }
    } else {
        showScreen('landing');
    }
}

// Start app
document.addEventListener('DOMContentLoaded', init);
