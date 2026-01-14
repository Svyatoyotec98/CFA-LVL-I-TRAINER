# Улучшения парсера для следующих модулей

## Проблемы из Module 2:

### 1. Question Text
**Проблема:** Включает "The correct answer is"
**Решение:**
```python
# БЫЛО:
q_match = re.search(rf'Q\.{q_num}\s+(.*?)The\s+correct\s+answer', raw, re.DOTALL)

# ДОЛЖНО БЫТЬ:
q_match = re.search(rf'Q\.{q_num}\s+(.*?)(?=A\.|The\s+correct\s+answer)', raw, re.DOTALL)
```

### 2. Options Parsing
**Проблема:** Формулы и объяснения попадают в текст опций
**Решение:**
```python
# Извлекать только цифры/суммы:
opt_pattern = r'([ABC])\.\s+([\$£€]?[\d,\.]+)'

# Или ограничивать до следующей опции:
opt_pattern = r'([ABC])\.\s+(.+?)(?=\s+[ABC]\.|The\s+correct)'
```

### 3. Explanation Extraction
**Проблема:** Обрезается посередине
**Решение:**
```python
# Извлекать до конца секции:
expl_match = re.search(r'The\s+correct\s+answer\s+is\s+[ABC]\.(.*?)(?:LOS|CFA\s+Level|©|$)', raw, re.DOTALL)
```

### 4. Calculator Steps
**Проблема:** Не извлекаются
**Решение:**
```python
# Искать паттерны BA II Plus:
calc_pattern = r'(N=.*?CPT.*?(?:FV|PV|PMT))'
# Или:
calc_pattern = r'(\[.*?\]\s+\[.*?\].*?→.*?)(?:\n|$)'
```

## Рекомендации для следующих модулей:

1. **Сначала тестировать на 2-3 вопросах**
2. **Проверять каждое поле вручную**
3. **Использовать более строгие regex**
4. **Добавить больше валидаций** (длина полей, формат)
