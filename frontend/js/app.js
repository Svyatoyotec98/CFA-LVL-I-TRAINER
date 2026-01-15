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
        // Load book data from API (reads from v2 structure)
        const data = await apiGet(`/tests/book-info/${bookId}`);
        state.booksData[bookId] = data;
        return data;
    } catch (error) {
        console.error(`Failed to load book ${bookId}:`, error);
        showToast('Ошибка загрузки данных книги', 'error');
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
        const checkBtn = document.getElementById('check-btn');
        if (mode === '90_second') {
            document.getElementById('prev-btn').classList.add('hidden');
            document.getElementById('flag-btn').classList.add('hidden');
            if (checkBtn) checkBtn.classList.add('hidden');
        } else if (mode === 'learning') {
            document.getElementById('prev-btn').classList.remove('hidden');
            document.getElementById('flag-btn').classList.remove('hidden');
            if (checkBtn) checkBtn.classList.remove('hidden');
        } else {
            document.getElementById('prev-btn').classList.remove('hidden');
            document.getElementById('flag-btn').classList.remove('hidden');
            if (checkBtn) checkBtn.classList.add('hidden');
        }

        showScreen('test');
        displayQuestion();
        if (mode !== 'learning') {
            startTimer();
        }
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

    // Table (if question has table data)
    const tableDiv = document.getElementById('question-table');
    if (tableDiv) {
        if (question.has_table && question.table_data) {
            tableDiv.innerHTML = renderTable(question.table_data);
            tableDiv.classList.remove('hidden');
        } else {
            tableDiv.innerHTML = '';
            tableDiv.classList.add('hidden');
        }
    }

    // Question continuation (text after table)
    const continuationDiv = document.getElementById('question-continuation');
    if (continuationDiv) {
        if (question.question_continuation) {
            continuationDiv.textContent = question.question_continuation;
            continuationDiv.classList.remove('hidden');
        } else {
            continuationDiv.textContent = '';
            continuationDiv.classList.add('hidden');
        }
    }

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

    // Options - with backwards compatibility and shuffle
    const optionsContainer = document.getElementById('options-container');
    const options = getOptions(question);
    const shuffledOptions = shuffleArray(options);

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

    // Update dots
    updateQuestionDots();

    // Update navigation
    document.getElementById('prev-btn').disabled = state.currentQuestionIndex === 0;

    const isLastQuestion = state.currentQuestionIndex === state.questions.length - 1;
    document.getElementById('next-btn').textContent = isLastQuestion ? 'Завершить' : 'Далее →';

    // Hide explanation for new question
    document.getElementById('explanation-container').classList.add('hidden');

    // Show check button for learning mode (if question not already answered in this mode)
    const checkBtn = document.getElementById('check-btn');
    if (checkBtn && state.testMode === 'learning') {
        // If already checked this question, keep button hidden and show explanation
        const alreadyAnswered = state.answers[question.question_id];
        if (alreadyAnswered) {
            // Check if this question was already revealed (we track by checking if explanation is shown)
            // For simplicity, show check button again if navigating back
            checkBtn.classList.remove('hidden');
        } else {
            checkBtn.classList.remove('hidden');
        }
    }
}

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

function showQuestionResult(question, userAnswer) {
    const correctOptionId = getCorrectOptionId(question);
    const isCorrect = userAnswer === correctOptionId;

    // Find correct option text for display
    const options = getOptions(question);
    const correctOption = options.find(opt => opt.id === correctOptionId);
    const correctText = correctOption ? correctOption.text : '';

    // Highlight correct/incorrect options
    document.querySelectorAll('.option').forEach(btn => {
        const optId = btn.dataset.optionId;
        btn.disabled = true;

        if (optId === correctOptionId) {
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

    // Wrong answer explanation (supports old string and new object format)
    const wrongEl = document.getElementById('explanation-wrong');
    if (wrongEl) {
        const wrongExplanation = question.explanation_wrong?.[userAnswer];
        if (!isCorrect && wrongExplanation) {
            let wrongHtml = `<strong>Почему ваш ответ неправильный:</strong> `;

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

    // Render MathJax for explanation
    if (window.MathJax && MathJax.typesetPromise) {
        MathJax.typesetPromise([expContainer]).catch(err => console.log('MathJax error:', err));
    }

    // In learning mode, show next button after checking
    if (state.testMode === 'learning') {
        const checkBtn = document.getElementById('check-btn');
        const nextBtn = document.getElementById('next-btn');
        if (checkBtn) checkBtn.classList.add('hidden');
        if (nextBtn) nextBtn.classList.remove('hidden');
    }
}

// Check single answer for learning mode
function checkSingleAnswer() {
    const question = state.questions[state.currentQuestionIndex];
    const userAnswer = state.answers[question.question_id];

    if (!userAnswer) {
        showToast('Выберите ответ', 'warning');
        return;
    }

    // Show result
    showQuestionResult(question, userAnswer);

    // Disable all options after checking
    document.querySelectorAll('.option').forEach(btn => {
        btn.style.pointerEvents = 'none';
    });

    // Hide check button after use
    const checkBtn = document.getElementById('check-btn');
    if (checkBtn) checkBtn.classList.add('hidden');
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

    // Calculate results (with backwards compatibility)
    const questionDetails = state.questions.map(q => {
        const correctId = getCorrectOptionId(q);
        return {
            question_id: q.question_id,
            user_answer: state.answers[q.question_id] || null,
            correct_answer: correctId,
            correct: state.answers[q.question_id] === correctId,
            time_spent: 0 // TODO: track per-question time
        };
    });

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
                    ${data.questions.map(q => {
                        const options = getOptions(q.question);
                        const correctId = getCorrectOptionId(q.question);
                        return `
                            <div class="review-question glass-container">
                                <p>${q.question.question_text}</p>
                                <div class="options-container">
                                    ${options.map(opt => `
                                        <button class="option"
                                                data-option-id="${opt.id}"
                                                onclick="answerReview('${q.question_id}', '${opt.id}', '${correctId}')">
                                            ${opt.text}
                                        </button>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }).join('')}
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

function renderCalculatorSteps(calc) {
    if (!calc) return '';
    return `
        <div class="calculator-block">
            <div class="calc-header" onclick="toggleCalculatorBlock(this)">
                <span class="calc-toggle-icon">▼</span>
                <span class="calc-icon">📟</span>
                <span class="calc-title">BA II Plus: ${calc.worksheet || 'Calculator'}</span>
                ${calc.access ? `<code class="calc-access">${calc.access}</code>` : ''}
            </div>
            <ol class="calc-steps">
                ${calc.steps.map(step => `<li>${step}</li>`).join('')}
            </ol>
            ${calc.example ? `
                <div class="calc-example">
                    <strong>Пример:</strong> ${calc.example.given || ''}
                    ${calc.example.input ? `<br><code>${calc.example.input}</code>` : ''}
                    ${calc.example.result ? `<br><span class="calc-result">→ ${calc.example.result}</span>` : ''}
                </div>
            ` : ''}
        </div>
    `;
}

function displayGlossary(terms) {
    const container = document.getElementById('glossary-list');
    const countEl = document.getElementById('glossary-count');

    if (countEl) countEl.textContent = `${terms.length} терминов`;

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
                ${term.calculator_steps ? renderCalculatorSteps(term.calculator_steps) : ''}
            </div>
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

// Calculator block toggle (terms are always expanded)
function toggleCalculatorBlock(headerEl) {
    const block = headerEl.closest('.calculator-block');
    block.classList.toggle('collapsed');
}

function expandAllCalcBlocks() {
    document.querySelectorAll('.calculator-block').forEach(block => {
        block.classList.remove('collapsed');
    });
}

function collapseAllCalcBlocks() {
    document.querySelectorAll('.calculator-block').forEach(block => {
        block.classList.add('collapsed');
    });
}

function searchGlossary() {
    const query = document.getElementById('glossary-search').value.toLowerCase();
    const bookId = document.getElementById('glossary-book-filter').value;
    const moduleId = document.getElementById('glossary-module-filter').value;

    let filtered = glossaryTerms;

    if (bookId) filtered = filtered.filter(t => t.book_id == bookId);
    if (moduleId) filtered = filtered.filter(t => t.module_id == moduleId);
    if (query) {
        filtered = filtered.filter(t =>
            t.term_en.toLowerCase().includes(query) ||
            (t.term_ru && t.term_ru.toLowerCase().includes(query)) ||
            t.definition_en.toLowerCase().includes(query) ||
            (t.los_id && t.los_id.toLowerCase().includes(query))
        );
    }

    displayGlossary(filtered);
}

function onBookFilterChange() {
    const bookId = document.getElementById('glossary-book-filter').value;
    const moduleSelect = document.getElementById('glossary-module-filter');

    // Update module dropdown based on selected book
    const modules = getModulesForBook(bookId);
    moduleSelect.innerHTML = '<option value="">Все модули</option>' +
        modules.map(m => `<option value="${m.id}">Module ${m.id}: ${m.name}</option>`).join('');

    filterGlossary();
}

function getModulesForBook(bookId) {
    if (!bookId) return [];

    const bookModules = {
        '1': [
            {id: 1, name: 'Rate and Return'},
            {id: 2, name: 'Time Value of Money'},
            {id: 3, name: 'Statistical Measures'},
            {id: 4, name: 'Probability Concepts'},
            {id: 5, name: 'Probability Distributions'},
            {id: 6, name: 'Sampling & Estimation'},
            {id: 7, name: 'Hypothesis Testing'},
            {id: 8, name: 'Linear Regression'},
            {id: 9, name: 'Multiple Regression'},
            {id: 10, name: 'Time Series'},
            {id: 11, name: 'Big Data'}
        ]
    };

    return bookModules[bookId] || [];
}

function filterGlossary() {
    const bookId = document.getElementById('glossary-book-filter').value;
    const moduleId = document.getElementById('glossary-module-filter').value;
    const query = document.getElementById('glossary-search').value.toLowerCase();

    let filtered = glossaryTerms;

    if (bookId) filtered = filtered.filter(t => t.book_id == bookId);
    if (moduleId) filtered = filtered.filter(t => t.module_id == moduleId);
    if (query) {
        filtered = filtered.filter(t =>
            t.term_en.toLowerCase().includes(query) ||
            (t.term_ru && t.term_ru.toLowerCase().includes(query)) ||
            t.definition_en.toLowerCase().includes(query)
        );
    }

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

// ============== Table Rendering ==============
function renderTable(tableData) {
    if (!tableData) return '';

    let html = '<table class="question-table">';

    // Headers
    if (tableData.headers && tableData.headers.length > 0) {
        html += '<thead><tr>';
        tableData.headers.forEach(h => {
            html += `<th>${h}</th>`;
        });
        html += '</tr></thead>';
    }

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

// ============== Backwards Compatibility ==============
// These functions support both old (A/B/C object) and new (opt1/opt2/opt3 array) formats

function getOptions(question) {
    // New format (array)
    if (Array.isArray(question.options)) {
        return question.options;
    }

    // Old format (object A/B/C) - convert to new format
    return Object.entries(question.options).map(([letter, text], index) => ({
        id: `opt${index + 1}`,
        text: text,
        _originalLetter: letter  // for backwards compatibility
    }));
}

function getCorrectOptionId(question) {
    // New format
    if (question.correct_option_id) {
        return question.correct_option_id;
    }

    // Old format - convert A→opt1, B→opt2, C→opt3
    const letterToOpt = {'A': 'opt1', 'B': 'opt2', 'C': 'opt3', 'D': 'opt4'};
    return letterToOpt[question.correct_answer] || 'opt1';
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
