# CLAUDE_CODE_MANUAL.md
# CFA Level 1 Trainer — Полная техническая документация

**Версия:** 1.0  
**Дата:** 11 января 2026  
**Экзамен:** 13 мая 2026 (~4 месяца)  
**Автор требований:** Пользователь  
**Исполнитель:** Claude Code  

---

## Оглавление

1. [Обзор проекта](#1-обзор-проекта)
2. [Технический стек](#2-технический-стек)
3. [Структура данных](#3-структура-данных)
4. [Архитектура базы данных](#4-архитектура-базы-данных)
5. [API Endpoints](#5-api-endpoints)
6. [Frontend компоненты](#6-frontend-компоненты)
7. [Функциональность](#7-функциональность)
8. [Калькулятор-тренажёр BA II Plus](#8-калькулятор-тренажёр-ba-ii-plus)
9. [Парсинг PDF](#9-парсинг-pdf)
10. [Этапы разработки](#10-этапы-разработки)
11. [Приложения](#приложения)

---

## 1. Обзор проекта

### 1.1 Цель
Веб-тренажёр для подготовки к экзамену CFA Level 1, основанный на архитектуре существующего Spanish Trainer.

### 1.2 Источники данных
- **10 книг (Books)** с конспектами и вопросами от AnalystPrep
- **~3500 вопросов** формата Multiple Choice (A/B/C)
- **Мануал BA II Plus Professional** — официальный гайд Texas Instruments

### 1.3 Ключевые принципы
1. **Mappe структуры Spanish → CFA:**
   - Unidad → Book
   - Categoría → Learning Module (глава)
   - Palabra → Question

2. **Разблокировка 80%** — следующая глава открывается при 80%+ в текущей

3. **Два режима тестов:**
   - Standard Mode — общее время, свободная навигация
   - 90-Second Mode — 90 секунд на вопрос, уход в минус

---

## 2. Технический стек

### 2.1 Backend
```
Framework:     FastAPI
ORM:           SQLAlchemy
Database:      SQLite (файл cfa_trainer.db)
Auth:          JWT токены (python-jose)
Password:      bcrypt через passlib
```

### 2.2 Frontend
```
HTML/CSS/JS:   Vanilla (без фреймворков)
Стиль:         Glassmorphism UI
Формулы:       MathJax (CDN)
Хранение:      localStorage + sync с backend
```

### 2.3 Структура проекта
```
cfa-trainer/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic схемы
│   ├── auth.py              # JWT логика
│   ├── database.py          # DB connection
│   └── routers/
│       ├── users.py
│       ├── progress.py
│       ├── tests.py
│       └── calculator.py
├── frontend/
│   ├── index.html           # Единый HTML (SPA-like)
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js           # Вся логика
│   └── data/
│       ├── books/
│       │   ├── book1_quantitative.json
│       │   ├── book2_economics.json
│       │   └── ...
│       └── glossary/
│           ├── book1_terms.json
│           └── ...
├── scripts/
│   └── parse_pdf.py         # Парсинг PDF → JSON
├── requirements.txt
└── README.md
```

---

## 3. Структура данных

### 3.1 Формат JSON для вопросов

**Файл:** `frontend/data/books/book1_quantitative.json`

```json
{
  "book_id": 1,
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  "total_questions": 350,
  "learning_modules": [
    {
      "module_id": 1,
      "module_name": "Rates and Returns",
      "module_name_ru": "Ставки и доходности",
      "questions": [
        {
          "question_id": "QM-1-001",
          "question_text": "An investor purchases a stock for $50 and sells it one year later for $55, receiving a $2 dividend. The holding period return is closest to:",
          "question_text_formula": null,
          "has_table": false,
          "has_image": false,
          "image_path": null,
          "options": {
            "A": "10.0%",
            "B": "12.0%",
            "C": "14.0%"
          },
          "correct_answer": "C",
          "explanation": "HPR = (Ending Price - Beginning Price + Dividend) / Beginning Price = ($55 - $50 + $2) / $50 = 14%",
          "explanation_wrong": {
            "A": "This answer ignores the dividend payment",
            "B": "This answer uses incorrect formula for capital gain"
          },
          "calculator_steps": null,
          "difficulty": "easy",
          "los_reference": "LOS 1.a"
        },
        {
          "question_id": "QM-1-002",
          "question_text": "Calculate the future value of $10,000 invested for 5 years at 8% annual interest, compounded quarterly.",
          "question_text_formula": "$FV = PV \\times (1 + \\frac{r}{m})^{m \\times n}$",
          "has_table": false,
          "has_image": false,
          "image_path": null,
          "options": {
            "A": "$14,693.28",
            "B": "$14,802.44",
            "C": "$14,859.47"
          },
          "correct_answer": "B",
          "explanation": "FV = $10,000 × (1 + 0.08/4)^(4×5) = $10,000 × (1.02)^20 = $14,859.47",
          "explanation_wrong": {
            "A": "Uses simple interest instead of compound",
            "C": "Uses monthly compounding instead of quarterly"
          },
          "calculator_steps": [
            "2ND [CLR TVM]",
            "10000 [+/-] [PV]",
            "8 [I/Y]",
            "5 [2ND] [xP/Y] [N]",
            "4 [2ND] [P/Y] [ENTER]",
            "[CPT] [FV]"
          ],
          "difficulty": "medium",
          "los_reference": "LOS 1.b"
        }
      ]
    }
  ]
}
```

### 3.2 Формат JSON для глоссария

**Файл:** `frontend/data/glossary/book1_terms.json`

```json
{
  "book_id": 1,
  "book_name": "Quantitative Methods",
  "book_name_ru": "Количественные методы",
  "total_terms": 21,
  "terms": [
    {
      "term_id": "T-QM-001",
      "term_en": "Holding Period Return (HPR)",
      "term_ru": "Доходность за период владения",
      "definition_en": "The return earned from holding an asset for a single specified period of time. It is calculated as the sum of price change and income received (such as dividends), divided by the beginning price.",
      "definition_ru": "Доходность от владения активом за определённый период времени. Рассчитывается как сумма изменения цены и полученного дохода (например, дивидендов), делённая на начальную цену.",
      "formula": "$HPR = \\frac{P_1 - P_0 + D_1}{P_0}$",
      "module_id": 1,
      "los_id": "LOS_1b",
      "related_terms": ["T-QM-002", "T-QM-003", "T-QM-008"],
      "calculator_steps": {
        "worksheet": "Direct Calculation",
        "access": "Standard keys",
        "steps": [
          "(P1 [-] P0) [=] — изменение цены",
          "[+] D1 [=] — добавить доход",
          "[÷] P0 [=] — разделить на начальную цену"
        ],
        "example": {
          "given": "P0=$100, P1=$110, D1=$5",
          "input": "(110 - 100 + 5) ÷ 100",
          "result": "HPR = 15%"
        }
      }
    },
    {
      "term_id": "T-QM-004",
      "term_en": "Harmonic Mean",
      "term_ru": "Среднее гармоническое",
      "definition_en": "A measure of central tendency calculated as the number of observations divided by the sum of reciprocals of the observations.",
      "definition_ru": "Мера центральной тенденции, рассчитываемая как число наблюдений, делённое на сумму обратных величин.",
      "formula": "$\\bar{X}_H = \\frac{n}{\\sum_{i=1}^{n} \\frac{1}{X_i}}$",
      "module_id": 1,
      "los_id": "LOS_1b",
      "related_terms": ["T-QM-002", "T-QM-003"],
      "calculator_steps": {
        "worksheet": "Direct Calculation",
        "access": "Standard keys",
        "steps": [
          "1 [÷] X1 [=] [+] — обратная величина первого значения",
          "1 [÷] X2 [=] [+] — обратная величина второго значения",
          "Повторить для всех Xi",
          "[=] — сумма обратных величин",
          "n [÷] (результат) [=] — среднее гармоническое"
        ],
        "example": {
          "given": "P/E ratios: 10, 15, 20",
          "input": "n=3, sum(1/Xi) = 1/10 + 1/15 + 1/20 = 0.2167",
          "result": "Harmonic Mean = 13.85"
        }
      }
    }
  ]
}
```

#### Структура полей термина:

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `term_id` | string | ✅ | Уникальный ID термина (формат: "T-QM-001") |
| `term_en` | string | ✅ | Термин на английском |
| `term_ru` | string | ✅ | Термин на русском |
| `definition_en` | string | ✅ | Определение на английском |
| `definition_ru` | string | ✅ | Определение на русском |
| `formula` | string/null | ❌ | LaTeX формула (с $ обёртками) или null |
| `module_id` | integer | ✅ | ID модуля (1, 2, 3...) |
| `los_id` | string | ✅ | LOS reference (формат: "LOS_1a", "LOS_2b") |
| `related_terms` | array | ✅ | Массив ID связанных терминов |
| `calculator_steps` | object/null | ❌ | Шаги расчёта на калькуляторе или null |

#### Структура calculator_steps:

```json
{
  "worksheet": "Direct Calculation",  // или "TVM", "Cash Flow", "Statistics", "Interest Conversion"
  "access": "Standard keys",          // или "[2ND] [DATA]", "[CF]", "[2ND] [ICONV]"
  "steps": [                          // Массив шагов для BA II Plus
    "Шаг 1: описание действия",
    "Шаг 2: описание действия",
    "..."
  ],
  "example": {
    "given": "Дано: описание входных данных",
    "input": "Последовательность ввода на калькуляторе",
    "result": "Результат = значение"
  }
}
```

#### Правила отображения в UI:

1. **Термин всегда развёрнут** — показывается сразу: английский термин, русский перевод, определения, формула
2. **Калькуляторный блок сворачиваемый** — если есть `calculator_steps`, блок "BA II Plus: [Worksheet]" можно скрыть/показать по клику
3. **Фильтры:** по Book ID и Module ID через dropdown
4. **Badges:** LOS badge (синий) и Module badge (фиолетовый) справа от заголовка
5. **Формулы:** рендерятся через MathJax с поддержкой LaTeX

### 3.3 Структура книг CFA Level 1

| Book # | Name | ~Questions |
|--------|------|------------|
| 1 | Quantitative Methods | 350 |
| 2 | Economics | 350 |
| 3 | Financial Statement Analysis | 400 |
| 4 | Corporate Issuers | 250 |
| 5 | Equity Investments | 350 |
| 6 | Fixed Income | 400 |
| 7 | Derivatives | 300 |
| 8 | Alternative Investments | 200 |
| 9 | Portfolio Management | 350 |
| 10 | Ethics | 350 |
| **Total** | | **~3500** |

---

## 4. Архитектура базы данных

### 4.1 ER-диаграмма (SQLAlchemy модели)

```python
# models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    progress = relationship("UserProgress", back_populates="user")
    test_results = relationship("TestResult", back_populates="user")
    errors = relationship("UserError", back_populates="user")


class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer)
    module_id = Column(Integer)
    
    questions_seen = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    mastery_percent = Column(Float, default=0.0)
    is_unlocked = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="progress")


class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    test_type = Column(String)  # "module", "book", "mock_exam"
    test_mode = Column(String)  # "standard", "90_second"
    book_id = Column(Integer, nullable=True)
    module_id = Column(Integer, nullable=True)
    
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    score_percent = Column(Float)
    time_spent_seconds = Column(Integer)
    
    question_details = Column(JSON)  # [{question_id, user_answer, correct, time_spent}]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="test_results")


class UserError(Base):
    __tablename__ = "user_errors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(String)
    book_id = Column(Integer)
    module_id = Column(Integer)
    
    error_count = Column(Integer, default=1)
    last_error_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_correct_at = Column(DateTime, nullable=True)
    
    # Для Spaced Repetition
    next_review_at = Column(DateTime, nullable=True)
    review_interval_days = Column(Integer, default=1)
    
    user = relationship("User", back_populates="errors")


class CalculatorSession(Base):
    __tablename__ = "calculator_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    worksheet_type = Column(String)  # "TVM", "CF", "Bond", "Stats"
    problem_data = Column(JSON)
    user_steps = Column(JSON)
    is_correct = Column(Boolean)
    time_spent_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
```

---

## 5. API Endpoints

### 5.1 Аутентификация

| Method | Endpoint | Описание |
|--------|----------|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход, возврат JWT |
| POST | `/api/auth/refresh` | Обновление токена |
| GET | `/api/auth/me` | Текущий пользователь |

### 5.2 Прогресс

| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/api/progress` | Весь прогресс пользователя |
| GET | `/api/progress/book/{book_id}` | Прогресс по книге |
| POST | `/api/progress/sync` | Синхронизация с localStorage |

### 5.3 Тесты

| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/api/tests/module/{book_id}/{module_id}` | Вопросы для теста модуля |
| GET | `/api/tests/book/{book_id}` | Тест по книге (рандом) |
| GET | `/api/tests/mock-exam` | Mock Exam (180 вопросов) |
| POST | `/api/tests/submit` | Отправка результата |
| GET | `/api/tests/history` | История тестов |

### 5.4 Ошибки и Spaced Repetition

| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/api/errors` | Все ошибки пользователя |
| GET | `/api/errors/review` | Вопросы для повторения сегодня |
| POST | `/api/errors/mark-reviewed` | Отметить как повторённый |

### 5.5 Глоссарий

| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/api/glossary` | Все термины |
| GET | `/api/glossary/book/{book_id}` | Термины по книге |
| GET | `/api/glossary/search?q=` | Поиск терминов |

### 5.6 Калькулятор

| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/api/calculator/problems/{type}` | Задачи по типу (TVM, CF, Bond) |
| POST | `/api/calculator/check` | Проверка ответа |
| GET | `/api/calculator/stats` | Статистика по калькулятору |

---

## 6. Frontend компоненты

### 6.1 Навигация экранов (SPA-like)

```javascript
// app.js - Основная логика

const screens = {
    'landing': document.getElementById('landing-screen'),
    'login': document.getElementById('login-screen'),
    'register': document.getElementById('register-screen'),
    'dashboard': document.getElementById('dashboard-screen'),
    'books': document.getElementById('books-screen'),
    'modules': document.getElementById('modules-screen'),
    'test': document.getElementById('test-screen'),
    'results': document.getElementById('results-screen'),
    'calculator': document.getElementById('calculator-screen'),
    'glossary': document.getElementById('glossary-screen'),
    'mock-exam': document.getElementById('mock-exam-screen'),
    'statistics': document.getElementById('statistics-screen')
};

function hideAllScreens() {
    Object.values(screens).forEach(screen => {
        screen.classList.add('hidden');
    });
}

function showScreen(screenName) {
    hideAllScreens();
    screens[screenName].classList.remove('hidden');
    window.scrollTo(0, 0);
}
```

### 6.2 Структура index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CFA Level 1 Trainer</title>
    <link rel="stylesheet" href="css/styles.css">
    <!-- MathJax для формул -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async 
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>
</head>
<body>
    <!-- Landing Screen -->
    <div id="landing-screen" class="screen">
        <div class="glass-container">
            <h1>CFA Level 1 Trainer</h1>
            <p>Подготовка к экзамену 13 мая 2026</p>
            <button onclick="showScreen('login')">Войти</button>
            <button onclick="showScreen('register')">Регистрация</button>
        </div>
    </div>

    <!-- Login Screen -->
    <div id="login-screen" class="screen hidden">
        <!-- форма входа -->
    </div>

    <!-- Dashboard Screen -->
    <div id="dashboard-screen" class="screen hidden">
        <nav class="top-nav">
            <span id="user-name"></span>
            <button onclick="logout()">Выход</button>
        </nav>
        
        <div class="dashboard-grid">
            <div class="card" onclick="showScreen('books')">
                <h3>📚 Книги</h3>
                <p>10 книг, ~3500 вопросов</p>
                <div class="progress-bar">
                    <div id="overall-progress" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="card" onclick="showScreen('mock-exam')">
                <h3>📝 Mock Exam</h3>
                <p>Симуляция экзамена</p>
            </div>
            
            <div class="card" onclick="showScreen('calculator')">
                <h3>🔢 Калькулятор</h3>
                <p>BA II Plus тренажёр</p>
            </div>
            
            <div class="card" onclick="showScreen('glossary')">
                <h3>📖 Глоссарий</h3>
                <p>Термины и определения</p>
            </div>
            
            <div class="card" onclick="showScreen('statistics')">
                <h3>📊 Статистика</h3>
                <p>Анализ ошибок</p>
            </div>
        </div>
    </div>

    <!-- Books Screen -->
    <div id="books-screen" class="screen hidden">
        <nav class="breadcrumb">
            <a onclick="showScreen('dashboard')">Dashboard</a> / Книги
        </nav>
        <div id="books-list" class="books-grid">
            <!-- Динамически заполняется -->
        </div>
    </div>

    <!-- Modules Screen -->
    <div id="modules-screen" class="screen hidden">
        <nav class="breadcrumb">
            <a onclick="showScreen('dashboard')">Dashboard</a> / 
            <a onclick="showScreen('books')">Книги</a> / 
            <span id="current-book-name"></span>
        </nav>
        <div id="modules-list" class="modules-grid">
            <!-- Динамически заполняется -->
        </div>
    </div>

    <!-- Test Screen -->
    <div id="test-screen" class="screen hidden">
        <!-- Режим тестирования -->
        <div class="test-header">
            <div id="test-timer"></div>
            <div id="test-progress">1/20</div>
            <button onclick="flagQuestion()">🚩 Отметить</button>
        </div>
        
        <div id="question-container" class="glass-container">
            <div id="question-text"></div>
            <div id="question-formula"></div>
            <div id="question-image"></div>
            
            <div id="options-container">
                <!-- A, B, C варианты -->
            </div>
        </div>
        
        <div class="test-navigation">
            <button onclick="prevQuestion()">← Назад</button>
            <button onclick="nextQuestion()">Далее →</button>
            <button onclick="submitTest()" id="submit-btn" class="hidden">
                Завершить тест
            </button>
        </div>
    </div>

    <!-- Results Screen -->
    <div id="results-screen" class="screen hidden">
        <div class="glass-container">
            <h2>Результаты</h2>
            <div id="score-display"></div>
            <div id="time-display"></div>
            <div id="questions-review">
                <!-- Разбор ответов -->
            </div>
        </div>
    </div>

    <!-- Calculator Screen -->
    <div id="calculator-screen" class="screen hidden">
        <!-- BA II Plus тренажёр -->
    </div>

    <!-- Mock Exam Screen -->
    <div id="mock-exam-screen" class="screen hidden">
        <!-- Полная симуляция экзамена -->
    </div>

    <script src="js/app.js"></script>
</body>
</html>
```

### 6.3 CSS Glassmorphism стиль

```css
/* styles.css */

:root {
    --glass-bg: rgba(255, 255, 255, 0.1);
    --glass-border: rgba(255, 255, 255, 0.2);
    --primary: #4F46E5;
    --success: #10B981;
    --danger: #EF4444;
    --warning: #F59E0B;
}

body {
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    min-height: 100vh;
    color: white;
}

.hidden {
    display: none !important;
}

.glass-container {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 24px;
    margin: 16px;
}

.card {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.card.locked {
    opacity: 0.5;
    cursor: not-allowed;
}

.progress-bar {
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 12px;
}

.progress-bar > div {
    height: 100%;
    background: linear-gradient(90deg, var(--primary), var(--success));
    transition: width 0.3s;
}

/* Книги и модули */
.books-grid, .modules-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    padding: 16px;
}

/* Тест */
.test-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    position: sticky;
    top: 0;
    z-index: 100;
}

#test-timer {
    font-size: 24px;
    font-weight: bold;
}

#test-timer.negative {
    color: var(--danger);
}

.option {
    display: block;
    width: 100%;
    padding: 16px;
    margin: 8px 0;
    background: rgba(255, 255, 255, 0.05);
    border: 2px solid transparent;
    border-radius: 8px;
    color: white;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
}

.option:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: var(--primary);
}

.option.selected {
    background: rgba(79, 70, 229, 0.3);
    border-color: var(--primary);
}

.option.correct {
    background: rgba(16, 185, 129, 0.3);
    border-color: var(--success);
}

.option.incorrect {
    background: rgba(239, 68, 68, 0.3);
    border-color: var(--danger);
}

/* MathJax формулы */
.formula-container {
    background: rgba(0, 0, 0, 0.2);
    padding: 16px;
    border-radius: 8px;
    margin: 12px 0;
    overflow-x: auto;
}
```

---

## 7. Функциональность

### 7.1 Режимы тестирования

#### Standard Mode
```javascript
// Общее время на весь тест
const standardTest = {
    totalTimeMinutes: null,  // Без ограничения или заданное
    allowNavigation: true,   // Можно переходить между вопросами
    showTimer: true,
    canFlag: true,           // Можно отметить вопрос
    showAnswersAfter: 'submit'  // Показать ответы после сдачи
};
```

#### 90-Second Mode
```javascript
// 90 секунд на каждый вопрос
const timedTest = {
    secondsPerQuestion: 90,
    allowNavigation: false,  // Только вперёд
    showTimer: true,
    negativeTimeAllowed: true,  // Время уходит в минус
    showAnswersAfter: 'each'    // Показать сразу после ответа
};

function startQuestionTimer() {
    let seconds = 90;
    const timer = setInterval(() => {
        seconds--;
        updateTimerDisplay(seconds);
        
        if (seconds < 0) {
            timerElement.classList.add('negative');
        }
    }, 1000);
    
    return timer;
}
```

### 7.2 Система прогресса

```javascript
// Расчёт прогресса модуля
function calculateModuleMastery(moduleId) {
    const questions = getModuleQuestions(moduleId);
    const userAnswers = getUserAnswers(moduleId);
    
    const correct = userAnswers.filter(a => a.isCorrect).length;
    const total = questions.length;
    
    return {
        seen: userAnswers.length,
        correct: correct,
        mastery: (correct / total) * 100,
        isComplete: userAnswers.length === total,
        isUnlocked: true  // Всегда true для текущего
    };
}

// Проверка разблокировки следующего модуля
function checkUnlock(bookId, moduleId) {
    const currentMastery = calculateModuleMastery(moduleId);
    
    if (currentMastery.mastery >= 80) {
        unlockNextModule(bookId, moduleId + 1);
        return true;
    }
    return false;
}
```

### 7.3 Spaced Repetition для ошибок

```javascript
// Алгоритм интервального повторения (упрощённый SM-2)
function calculateNextReview(errorRecord) {
    const intervals = [1, 3, 7, 14, 30, 60];  // дни
    
    if (errorRecord.lastAnswerCorrect) {
        // Увеличиваем интервал
        const currentIndex = intervals.indexOf(errorRecord.currentInterval);
        const nextIndex = Math.min(currentIndex + 1, intervals.length - 1);
        return intervals[nextIndex];
    } else {
        // Сбрасываем на начало
        return intervals[0];
    }
}

// Получить вопросы для повторения сегодня
function getReviewQuestions() {
    const today = new Date();
    return userErrors.filter(error => {
        return new Date(error.nextReviewAt) <= today;
    });
}
```

### 7.4 Adaptive Difficulty (только Mock Exam)

```javascript
// Формирование Mock Exam с учётом слабых мест
function generateMockExam() {
    const TOTAL_QUESTIONS = 180;
    
    // 30% — вопросы с ошибками
    const errorQuestions = selectFromErrors(TOTAL_QUESTIONS * 0.3);
    
    // 30% — вопросы из слабых модулей (mastery < 70%)
    const weakModules = getWeakModules();
    const weakQuestions = selectFromModules(weakModules, TOTAL_QUESTIONS * 0.3);
    
    // 40% — рандомные вопросы
    const randomQuestions = selectRandom(TOTAL_QUESTIONS * 0.4);
    
    // Перемешиваем
    return shuffle([...errorQuestions, ...weakQuestions, ...randomQuestions]);
}
```

---

## 8. Калькулятор-тренажёр BA II Plus

### 8.1 Покрываемые функции

| Worksheet | Переменные | Приоритет |
|-----------|------------|-----------|
| **TVM** | N, I/Y, PV, PMT, FV, P/Y, C/Y, BGN/END | ⭐⭐⭐ Критично |
| **Cash Flow** | CFo, C01-C32, F01-F32, NPV, IRR, NFV | ⭐⭐⭐ Критично |
| **Bond** | SDT, CPN, RDT, RV, YLD, PRI, AI, DUR | ⭐⭐⭐ Критично |
| **Statistics** | X, Y, LIN/Ln/EXP/PWR, a, b, r | ⭐⭐ Важно |
| **Interest Conversion** | NOM, EFF, C/Y | ⭐⭐ Важно |
| **Amortization** | P1, P2, BAL, PRN, INT | ⭐ Дополнительно |

### 8.2 Формат задач калькулятора

```json
{
  "problem_id": "CALC-TVM-001",
  "worksheet": "TVM",
  "problem_text": "You invest $10,000 today at 8% annual interest compounded quarterly. What will be the value in 5 years?",
  "given": {
    "PV": -10000,
    "I/Y": 8,
    "N_years": 5,
    "P/Y": 4,
    "C/Y": 4
  },
  "find": "FV",
  "correct_answer": 14859.47,
  "tolerance": 0.01,
  "steps": [
    "Press [2ND] [CLR TVM] to clear TVM worksheet",
    "Enter 10000 [+/-] [PV]",
    "Enter 8 [I/Y]",
    "Press [2ND] [P/Y], enter 4, press [ENTER]",
    "Enter 5 [2ND] [xP/Y] [N] (this calculates 5×4=20)",
    "Press [CPT] [FV]",
    "Answer: 14,859.47"
  ],
  "common_mistakes": [
    "Forgetting to set P/Y and C/Y to 4",
    "Not making PV negative (cash outflow)",
    "Using 5 directly for N instead of 20 periods"
  ]
}
```

### 8.3 Интерфейс калькулятора

```javascript
// Виртуальная клавиатура BA II Plus
const calculatorKeys = {
    row1: ['ON/OFF', 'ENTER', '↑', '↓', 'CPT'],
    row2: ['2ND', 'N', 'I/Y', 'PV', 'PMT', 'FV'],
    row3: ['CF', 'NPV', 'IRR', 'AMORT', 'BOND', 'STAT'],
    row4: ['7', '8', '9', '×', 'DEL'],
    row5: ['4', '5', '6', '-', 'STO'],
    row6: ['1', '2', '3', '+', 'RCL'],
    row7: ['0', '.', '+/-', '=', 'CE/C']
};

// Отображение состояния калькулятора
const calculatorState = {
    display: '0.00',
    mode: 'standard',  // 'standard', 'TVM', 'CF', 'Bond', 'Stat'
    secondFunction: false,
    variables: {
        N: 0, IY: 0, PV: 0, PMT: 0, FV: 0,
        PY: 1, CY: 1, BGN: false
    }
};
```

---

## 9. Парсинг PDF

### 9.1 Структура PDF вопросов

```
Q.13 — [Question Text]
[Optional: Table or Image]

A. [Option A text]
B. [Option B text]  
C. [Option C text]

Correct Answer: B

[Explanation paragraph]

A is incorrect. [Why A is wrong]
C is incorrect. [Why C is wrong]

LOS: [Reference]
```

### 9.2 Скрипт парсинга

```python
# scripts/parse_pdf.py

import pdfplumber
import json
import re
from pathlib import Path

def parse_questions_pdf(pdf_path, book_id, output_path):
    """
    Парсит PDF с вопросами в JSON формат.
    """
    questions = []
    current_module = None
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    
    # Разбиваем на отдельные вопросы
    question_pattern = r'Q\.(\d+)\s*[—–-]\s*(.*?)(?=Q\.\d+|$)'
    matches = re.findall(question_pattern, full_text, re.DOTALL)
    
    for q_num, q_content in matches:
        question = parse_single_question(q_num, q_content, book_id)
        if question:
            questions.append(question)
    
    # Группируем по модулям
    modules = group_by_module(questions)
    
    output = {
        "book_id": book_id,
        "book_name": get_book_name(book_id),
        "total_questions": len(questions),
        "learning_modules": modules
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    return output


def parse_single_question(q_num, content, book_id):
    """
    Парсит один вопрос.
    """
    # Извлекаем текст вопроса
    question_match = re.search(r'^(.*?)(?=\nA\.)', content, re.DOTALL)
    if not question_match:
        return None
    
    question_text = question_match.group(1).strip()
    
    # Извлекаем варианты ответов
    options = {}
    for letter in ['A', 'B', 'C']:
        pattern = rf'{letter}\.\s*(.*?)(?=[ABC]\.|Correct Answer|$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            options[letter] = match.group(1).strip()
    
    # Извлекаем правильный ответ
    correct_match = re.search(r'Correct Answer:\s*([ABC])', content)
    correct_answer = correct_match.group(1) if correct_match else None
    
    # Извлекаем объяснение
    explanation_match = re.search(
        r'Correct Answer:\s*[ABC]\s*(.*?)(?=[ABC] is incorrect|LOS:|$)',
        content, re.DOTALL
    )
    explanation = explanation_match.group(1).strip() if explanation_match else ""
    
    # Извлекаем объяснения неправильных ответов
    wrong_explanations = {}
    for letter in ['A', 'B', 'C']:
        if letter != correct_answer:
            pattern = rf'{letter} is incorrect\.\s*(.*?)(?=[ABC] is incorrect|LOS:|$)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                wrong_explanations[letter] = match.group(1).strip()
    
    # Извлекаем LOS
    los_match = re.search(r'LOS:\s*(.*?)(?:\n|$)', content)
    los_reference = los_match.group(1).strip() if los_match else None
    
    # Проверяем наличие формул (LaTeX паттерны)
    has_formula = bool(re.search(r'\$.*?\$|\\frac|\\times|\\sum', question_text))
    
    return {
        "question_id": f"Q-{book_id}-{q_num}",
        "question_text": question_text,
        "question_text_formula": extract_formula(question_text) if has_formula else None,
        "has_table": detect_table(content),
        "has_image": False,  # Требует отдельной обработки
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "explanation_wrong": wrong_explanations,
        "calculator_steps": extract_calculator_steps(content),
        "los_reference": los_reference
    }


def extract_calculator_steps(content):
    """
    Извлекает шаги калькулятора если есть.
    """
    # Ищем паттерны типа [PV], [FV], [2ND], [CPT]
    if re.search(r'\[(?:PV|FV|PMT|N|I/Y|CPT|2ND)\]', content):
        steps = re.findall(r'(?:Press |Enter )?\[.*?\].*?(?=\n|$)', content)
        return steps if steps else None
    return None


if __name__ == "__main__":
    import sys
    
    pdf_path = sys.argv[1]
    book_id = int(sys.argv[2])
    output_path = sys.argv[3]
    
    parse_questions_pdf(pdf_path, book_id, output_path)
    print(f"Parsed {pdf_path} -> {output_path}")
```

---

## 10. Этапы разработки

### Фаза 1: MVP (2 недели)
**Цель:** Базовый функционал для начала подготовки

| День | Задача |
|------|--------|
| 1-2 | Backend: FastAPI + SQLAlchemy + Auth |
| 3-4 | Frontend: HTML/CSS структура, навигация |
| 5-6 | Парсинг 1-2 книг PDF → JSON |
| 7-8 | Тест модуля (Standard Mode) |
| 9-10 | Система прогресса + localStorage |
| 11-12 | Синхронизация с backend |
| 13-14 | Тестирование, фикс багов |

**Результат Фазы 1:**
- Можно проходить тесты по главам
- Видно прогресс
- Работает авторизация

### Фаза 2: Полный контент (2 недели)
| День | Задача |
|------|--------|
| 1-4 | Парсинг всех 10 книг |
| 5-7 | 90-Second Mode |
| 8-10 | Разблокировка 80% |
| 11-12 | MathJax интеграция |
| 13-14 | Таблицы и картинки в вопросах |

### Фаза 3: Продвинутые функции (2 недели)
| День | Задача |
|------|--------|
| 1-4 | Калькулятор-тренажёр BA II Plus |
| 5-7 | Mock Exam (180 вопросов) |
| 8-10 | Spaced Repetition |
| 11-12 | Adaptive Difficulty |
| 13-14 | Глоссарий с поиском |

### Фаза 4: Полировка (1 неделя)
| День | Задача |
|------|--------|
| 1-2 | UI/UX улучшения |
| 3-4 | Статистика и аналитика |
| 5-7 | Финальное тестирование |

---

## Приложения

### A. Команды запуска

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (отдельный сервер для разработки)
cd frontend
python -m http.server 3000
```

### B. Переменные окружения

```env
# .env
DATABASE_URL=sqlite:///./cfa_trainer.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### C. Требования (requirements.txt)

```txt
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
python-jose>=3.3.0
passlib>=1.7.4
bcrypt>=4.0.0
python-multipart>=0.0.6
pdfplumber>=0.10.0
aiofiles>=23.2.0
```

### D. Чеклист перед экзаменом (13 мая 2026)

- [ ] Все 10 книг пройдены с 80%+
- [ ] 10+ Mock Exams с результатом 70%+
- [ ] Калькулятор: TVM, CF, Bond — свободно
- [ ] Все ошибки повторены минимум 2 раза
- [ ] Глоссарий: ключевые термины выучены

---

**Документ готов к использованию Claude Code.**

*При возникновении вопросов — обращаться к этому документу как к единственному источнику истины.*
