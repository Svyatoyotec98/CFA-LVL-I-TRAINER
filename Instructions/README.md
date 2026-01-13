# CFA Level 1 Trainer — Instructions

**Дата:** 13 января 2026  
**Версия:** 2.0 Final

---

## 📁 Содержимое папки

| Файл | Описание |
|------|----------|
| `QBANK_INSTRUCTION.md` | Инструкция по созданию JSON тестов из PDF QBank |
| `GLOSSARY_INSTRUCTION.md` | Инструкция по созданию JSON глоссария из PDF Notes |
| `APP_JS_PATCH.md` | Изменения в app.js для новой структуры options |
| `BA_II_PLUS_QUICK_REFERENCE.md` | Краткая справка по калькулятору |
| `BA_II_PLUS_MANUAL.txt` | Полный мануал Texas BA II Plus Professional |

---

## 🎯 Что нужно сделать

### Шаг 1: Обновить Frontend (app.js)

Применить патч из `APP_JS_PATCH.md`:
- Изменить `displayQuestion()` — shuffle options без букв
- Изменить `selectAnswer()` — работа с opt1/opt2/opt3
- Изменить `showQuestionResult()` — проверка по correct_option_id
- Изменить `loadReviewQuestions()` — новая структура

### Шаг 2: Пересоздать QBank JSON

Для каждой книги (1-10):
1. Взять PDF из `Materials/QBank/`
2. Парсить по `QBANK_INSTRUCTION.md`
3. Сохранить в `frontend/data/books/book{N}.json`

**Ключевые изменения структуры:**
```json
// СТАРОЕ (не использовать)
"options": {"A": "text1", "B": "text2", "C": "text3"},
"correct_answer": "C"

// НОВОЕ (использовать)
"options": [
  {"id": "opt1", "text": "text1"},
  {"id": "opt2", "text": "text2"},
  {"id": "opt3", "text": "text3"}
],
"correct_option_id": "opt3"
```

### Шаг 3: Пересоздать Glossary JSON

Для каждой книги (1-10):
1. Взять PDF из `Materials/NOTES/`
2. Парсить по `GLOSSARY_INSTRUCTION.md`
3. Сохранить в `frontend/data/glossary/book{N}_terms.json`

---

## 📂 Структура проекта

```
CFA-LVL-I-TRAINER/
├── frontend/
│   ├── data/
│   │   ├── books/
│   │   │   ├── book1.json      ← QBank вопросы
│   │   │   ├── book2.json
│   │   │   └── ...
│   │   ├── glossary/
│   │   │   ├── book1_terms.json ← Глоссарий
│   │   │   ├── book2_terms.json
│   │   │   └── ...
│   │   └── calculator/
│   ├── js/
│   │   └── app.js              ← ОБНОВИТЬ по патчу
│   └── index.html
├── backend/
│   └── routers/                ← НЕ МЕНЯТЬ
├── Materials/
│   ├── QBank/                  ← Исходные PDF
│   ├── NOTES/                  ← Исходные PDF
│   ├── TEXAS BI II/
│   └── Instructions/           ← ЭТА ПАПКА
└── README.md
```

---

## ✅ Что НЕ нужно менять

| Компонент | Почему не трогаем |
|-----------|-------------------|
| `backend/routers/tests.py` | Просто прокидывает JSON |
| `backend/routers/errors.py` | Работает с question_id (строка) |
| `backend/routers/glossary.py` | Читает terms[] как есть |
| `backend/routers/progress.py` | Только счётчики |
| `backend/models.py` | Структура БД не зависит от формата вопросов |

---

## 🔧 Использование с Claude Code

### Парсинг QBank главы:
```
Прочитай QBANK_INSTRUCTION.md из Materials/Instructions/
Затем распарси PDF Materials/QBank/Quants/Chapter1.pdf
Создай JSON по инструкции и сохрани в frontend/data/books/book1.json
```

### Парсинг Glossary:
```
Прочитай GLOSSARY_INSTRUCTION.md из Materials/Instructions/
Затем распарси PDF Materials/NOTES/Book1_Quants.pdf
Извлеки все термины и сохрани в frontend/data/glossary/book1_terms.json
```

---

## 📊 Прогресс

### QBank (frontend/data/books/)
- [ ] book1.json — Quantitative Methods
- [ ] book2.json — Economics
- [ ] book3.json — FSA
- [ ] book4.json — Corporate Issuers
- [ ] book5.json — Equity
- [ ] book6.json — Fixed Income
- [ ] book7.json — Derivatives
- [ ] book8.json — Alternatives
- [ ] book9.json — Portfolio Management
- [ ] book10.json — Ethics

### Glossary (frontend/data/glossary/)
- [ ] book1_terms.json
- [ ] book2_terms.json
- [ ] book3_terms.json
- [ ] book4_terms.json
- [ ] book5_terms.json
- [ ] book6_terms.json
- [ ] book7_terms.json
- [ ] book8_terms.json
- [ ] book9_terms.json
- [ ] book10_terms.json

### Frontend
- [ ] app.js обновлён по патчу
- [ ] Тестирование shuffle
- [ ] Тестирование check answer
- [ ] Тестирование explanations

---

## 🚨 Важные правила

1. **Options без букв** — используем opt1/opt2/opt3, НЕ A/B/C
2. **Shuffle на фронте** — порядок меняется при каждом показе
3. **Формулы в LaTeX** — экранировать `\\frac`, `\\sqrt`
4. **Полные объяснения** — не обрезать, добавлять пагинацию для длинных
5. **Calculator steps** — для ВСЕХ расчётных задач
6. **Очистка мусора** — удалять © AnalystPrep, номера страниц
