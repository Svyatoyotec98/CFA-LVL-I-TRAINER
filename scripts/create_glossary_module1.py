#!/usr/bin/env python3
"""
Create glossary.json for book1_quants/module1 (Rate and Return)
Based on GLOSSARY_INSTRUCTION.md
"""

import json
from pathlib import Path

output_path = "/home/user/CFA-LVL-I-TRAINER/frontend/data/v2/book1_quants/module1/glossary.json"

print("📖 Creating glossary for Module 1: Rate and Return\n")

# Module 1: Rate and Return terms
# Based on the PDF content we saw in the paragraphs earlier
terms = [
    {
        "term_id": "T-QM-001",
        "term_en": "Interest Rate",
        "term_ru": "Процентная ставка",
        "definition_en": "A rate of return that reflects the relationship between cash flows occurring at different times. It can be interpreted as a required rate of return, discount rate, or opportunity cost. The interest rate compensates investors for the time value of money and various types of risk.",
        "definition_ru": "Ставка доходности, отражающая связь между денежными потоками в разные моменты времени. Может интерпретироваться как требуемая доходность, ставка дисконтирования или альтернативная стоимость. Процентная ставка компенсирует инвесторам временную стоимость денег и различные виды риска.",
        "formula": "$r = \\text{Real risk-free rate} + \\text{Inflation premium} + \\text{Default risk premium} + \\text{Liquidity premium} + \\text{Maturity premium}$",
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-002", "T-QM-003", "T-QM-004"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-002",
        "term_en": "Required Rate of Return",
        "term_ru": "Требуемая норма доходности",
        "definition_en": "The minimum rate of return that an investor must receive to accept an investment. It reflects the investor's opportunity cost and the risk associated with the investment. The required return compensates for the time value of money and various risk factors.",
        "definition_ru": "Минимальная норма доходности, которую инвестор должен получить для принятия инвестиции. Отражает альтернативную стоимость инвестора и риск, связанный с инвестицией. Требуемая доходность компенсирует временную стоимость денег и различные факторы риска.",
        "formula": None,
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-001", "T-QM-003"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-003",
        "term_en": "Discount Rate",
        "term_ru": "Ставка дисконтирования",
        "definition_en": "The rate used to calculate the present value of future cash flows. It accounts for the time value of money by converting future amounts into their equivalent present value. The discount rate and interest rate are often used interchangeably in financial calculations.",
        "definition_ru": "Ставка, используемая для расчета приведенной стоимости будущих денежных потоков. Учитывает временную стоимость денег путем преобразования будущих сумм в их эквивалентную текущую стоимость. Ставка дисконтирования и процентная ставка часто используются как взаимозаменяемые понятия.",
        "formula": "$PV = \\frac{FV}{(1+r)^n}$",
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-001", "T-QM-002"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-004",
        "term_en": "Opportunity Cost",
        "term_ru": "Альтернативная стоимость",
        "definition_en": "The value of the best alternative that an investor gives up when choosing a particular investment. It represents the return that could have been earned on the next best investment option. Opportunity cost is a key concept in evaluating investment decisions.",
        "definition_ru": "Стоимость лучшей альтернативы, от которой инвестор отказывается при выборе конкретной инвестиции. Представляет доходность, которая могла быть получена от следующего наилучшего варианта инвестирования. Альтернативная стоимость - ключевая концепция при оценке инвестиционных решений.",
        "formula": None,
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-002", "T-QM-001"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-005",
        "term_en": "Real Risk-Free Interest Rate",
        "term_ru": "Реальная безрисковая процентная ставка",
        "definition_en": "The theoretical single-period interest rate for a completely risk-free security when no inflation is expected. According to economic theory, it reflects the time preference of individuals for current versus future consumption. The real risk-free rate is the foundation upon which other interest rates are built.",
        "definition_ru": "Теоретическая процентная ставка за один период для полностью безрискового актива при отсутствии ожидаемой инфляции. Согласно экономической теории, отражает временное предпочтение людей в отношении текущего и будущего потребления. Реальная безрисковая ставка является основой, на которой строятся другие процентные ставки.",
        "formula": None,
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-001", "T-QM-006"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-006",
        "term_en": "Inflation Risk Premium",
        "term_ru": "Премия за инфляционный риск",
        "definition_en": "The additional return that investors require to compensate for the expected loss of purchasing power due to inflation. It represents the average inflation rate expected over the maturity of the investment. This premium protects investors from the erosion of real returns caused by rising prices.",
        "definition_ru": "Дополнительная доходность, которую требуют инвесторы для компенсации ожидаемой потери покупательной способности из-за инфляции. Представляет среднюю ожидаемую инфляцию за период инвестирования. Эта премия защищает инвесторов от снижения реальной доходности, вызванного ростом цен.",
        "formula": None,
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-001", "T-QM-005"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-007",
        "term_en": "Default Risk Premium",
        "term_ru": "Премия за кредитный риск",
        "definition_en": "The additional return that investors demand to compensate for the possibility that a borrower may fail to make promised payments. Higher default risk requires a higher premium. This premium reflects the creditworthiness of the issuer and increases for lower-rated securities.",
        "definition_ru": "Дополнительная доходность, которую требуют инвесторы для компенсации возможности невыполнения заемщиком обещанных платежей. Более высокий кредитный риск требует более высокой премии. Эта премия отражает кредитоспособность эмитента и увеличивается для ценных бумаг с более низким рейтингом.",
        "formula": None,
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-001", "T-QM-008"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-008",
        "term_en": "Liquidity Risk Premium",
        "term_ru": "Премия за риск ликвидности",
        "definition_en": "The additional return investors require for securities that cannot be easily converted to cash at close to fair market value. Illiquid investments require higher returns to compensate for the difficulty and potential costs of selling them. This premium is higher for securities with thin trading volumes or wide bid-ask spreads.",
        "definition_ru": "Дополнительная доходность, которую требуют инвесторы для ценных бумаг, которые нельзя легко конвертировать в денежные средства по справедливой рыночной стоимости. Неликвидные инвестиции требуют более высокой доходности для компенсации сложности и потенциальных затрат на их продажу. Эта премия выше для ценных бумаг с малыми объемами торгов или широкими спредами.",
        "formula": None,
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-001", "T-QM-007"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-009",
        "term_en": "Maturity Risk Premium",
        "term_ru": "Премия за срочность",
        "definition_en": "The additional return investors demand for longer-maturity securities to compensate for greater exposure to interest rate risk. Longer-term bonds are more sensitive to interest rate changes than short-term bonds. This premium typically increases with the length of time until maturity.",
        "definition_ru": "Дополнительная доходность, которую требуют инвесторы для ценных бумаг с более длительным сроком погашения для компенсации большей подверженности процентному риску. Долгосрочные облигации более чувствительны к изменениям процентных ставок, чем краткосрочные. Эта премия обычно увеличивается с ростом срока до погашения.",
        "formula": None,
        "module_id": 1,
        "los_id": "LOS_1a",
        "related_terms": ["T-QM-001", "T-QM-008"],
        "calculator_steps": None
    },
    {
        "term_id": "T-QM-010",
        "term_en": "Holding Period Return (HPR)",
        "term_ru": "Доходность за период владения",
        "definition_en": "The total return earned from holding an investment for a specified period of time. It includes both capital gains (or losses) from price changes and any income received during the holding period, such as dividends or interest. HPR is calculated by dividing the sum of income and price change by the beginning price.",
        "definition_ru": "Общая доходность от владения инвестицией за определенный период времени. Включает как прирост капитала (или убытки) от изменения цены, так и любой доход, полученный за период владения, такой как дивиденды или проценты. HPR рассчитывается путем деления суммы дохода и изменения цены на начальную цену.",
        "formula": "$HPR = \\frac{P_1 - P_0 + D_1}{P_0}$",
        "module_id": 1,
        "los_id": "LOS_1b",
        "related_terms": ["T-QM-011", "T-QM-012", "T-QM-013"],
        "calculator_steps": {
            "worksheet": "Standard calculation",
            "access": "Direct calculation",
            "steps": [
                "Вычислить изменение цены: P1 - P0",
                "Прибавить полученный доход (дивиденды или проценты): + D1",
                "Разделить на начальную цену: ÷ P0",
                "Результат в десятичной форме (умножить на 100 для процентов)"
            ],
            "example": {
                "given": "Bought stock at $50, sold at $56, received $2 dividend",
                "input": "P0=50, P1=56, D1=2",
                "result": "HPR = (56-50+2)/50 = 0.16 or 16%"
            }
        }
    }
]

# Create glossary structure
glossary = {
    "book_id": 1,
    "book_name": "Quantitative Methods",
    "book_name_ru": "Количественные методы",
    "module_id": 1,
    "module_name": "Rate and Return",
    "module_name_ru": "Ставки и доходность",
    "total_terms": len(terms),
    "terms": terms
}

# Save to file
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(glossary, f, indent=2, ensure_ascii=False)

print(f"✅ Created glossary.json with {len(terms)} terms")
print(f"📁 Saved to: {output_path}\n")

# Display first 5 terms
print("=" * 80)
print("FIRST 5 TERMS:")
print("=" * 80)

for i, term in enumerate(terms[:5], 1):
    print(f"\n{i}. {term['term_en']} ({term['term_ru']})")
    print(f"   ID: {term['term_id']}")
    print(f"   LOS: {term['los_id']}")
    print(f"   Definition (EN): {term['definition_en'][:100]}...")
    if term['formula']:
        print(f"   Formula: {term['formula']}")
    print("-" * 80)

print(f"\n✅ Total terms created: {len(terms)}")
