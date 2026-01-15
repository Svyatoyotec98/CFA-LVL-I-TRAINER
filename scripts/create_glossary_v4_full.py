#!/usr/bin/env python3
"""
Create glossary.json for book1_quants/module1
Following GLOSSARY_INSTRUCTION_v4.md - COMPLETE VERSION

ETALON: 5 LOS, 21 terms total
"""

import json
from pathlib import Path

output_path = "/home/user/CFA-LVL-I-TRAINER/frontend/data/v2/book1_quants/module1/glossary.json"

print("="*80)
print("CREATING GLOSSARY V4 FOR MODULE 1: RATE AND RETURN")
print("ETALON: 5 LOS, 21 terms")
print("="*80)

# Complete terms list following v4 ETALON
terms = [
    # LOS_1a: Interpret interest rates (6 terms)
    {
        "term_id": "QM-1-001",
        "term_en": "Interest Rate",
        "term_ru": "Процентная ставка",
        "definition_en": "A rate of return that reflects the relationship between cash flows occurring at different times. It can be interpreted as a required rate of return, discount rate, or opportunity cost. The interest rate compensates investors for the time value of money and consists of a real risk-free rate plus premiums for inflation, default, liquidity, and maturity risks.",
        "definition_ru": "Ставка доходности, отражающая связь между денежными потоками в разные моменты времени. Может интерпретироваться как требуемая доходность, ставка дисконтирования или альтернативная стоимость. Процентная ставка компенсирует инвесторам временную стоимость денег и состоит из реальной безрисковой ставки плюс премии за инфляцию, дефолт, ликвидность и срочность.",
        "formula": None,
        "los_id": "LOS_1a",
        "calculator": None
    },
    {
        "term_id": "QM-1-002",
        "term_en": "Real Risk-Free Interest Rate",
        "term_ru": "Реальная безрисковая процентная ставка",
        "definition_en": "The theoretical single-period interest rate for a completely risk-free security when no inflation is expected. According to economic theory, it reflects the time preference of individuals for current versus future consumption. The real risk-free rate is the foundation upon which other interest rates are built.",
        "definition_ru": "Теоретическая процентная ставка за один период для полностью безрискового актива при отсутствии ожидаемой инфляции. Согласно экономической теории, отражает временное предпочтение людей в отношении текущего и будущего потребления. Реальная безрисковая ставка является основой, на которой строятся другие процентные ставки.",
        "formula": None,
        "los_id": "LOS_1a",
        "calculator": None
    },
    {
        "term_id": "QM-1-003",
        "term_en": "Inflation Premium",
        "term_ru": "Премия за инфляционный риск",
        "definition_en": "The additional return that investors require to compensate for the expected loss of purchasing power due to inflation. It represents the average inflation rate expected over the maturity of the investment. This premium protects investors from the erosion of real returns caused by rising prices.",
        "definition_ru": "Дополнительная доходность, которую требуют инвесторы для компенсации ожидаемой потери покупательной способности из-за инфляции. Представляет среднюю ожидаемую инфляцию за период инвестирования. Эта премия защищает инвесторов от снижения реальной доходности, вызванного ростом цен.",
        "formula": None,
        "los_id": "LOS_1a",
        "calculator": None
    },
    {
        "term_id": "QM-1-004",
        "term_en": "Default Risk Premium",
        "term_ru": "Премия за кредитный риск",
        "definition_en": "The additional return that investors demand to compensate for the possibility that a borrower may fail to make promised payments. Higher default risk requires a higher premium. This premium reflects the creditworthiness of the issuer and increases for lower-rated securities.",
        "definition_ru": "Дополнительная доходность, которую требуют инвесторы для компенсации возможности невыполнения заемщиком обещанных платежей. Более высокий кредитный риск требует более высокой премии. Эта премия отражает кредитоспособность эмитента и увеличивается для ценных бумаг с более низким рейтингом.",
        "formula": None,
        "los_id": "LOS_1a",
        "calculator": None
    },
    {
        "term_id": "QM-1-005",
        "term_en": "Liquidity Premium",
        "term_ru": "Премия за риск ликвидности",
        "definition_en": "The additional return investors require for securities that cannot be easily converted to cash at close to fair market value. Illiquid investments require higher returns to compensate for the difficulty and potential costs of selling them. This premium is higher for securities with thin trading volumes or wide bid-ask spreads.",
        "definition_ru": "Дополнительная доходность, которую требуют инвесторы для ценных бумаг, которые нельзя легко конвертировать в денежные средства по справедливой рыночной стоимости. Неликвидные инвестиции требуют более высокой доходности для компенсации сложности и потенциальных затрат на их продажу. Эта премия выше для ценных бумаг с малыми объемами торгов или широкими спредами.",
        "formula": None,
        "los_id": "LOS_1a",
        "calculator": None
    },
    {
        "term_id": "QM-1-006",
        "term_en": "Maturity Premium",
        "term_ru": "Премия за срочность",
        "definition_en": "The additional return investors demand for longer-maturity securities to compensate for greater exposure to interest rate risk. Longer-term bonds are more sensitive to interest rate changes than short-term bonds. This premium typically increases with the length of time until maturity.",
        "definition_ru": "Дополнительная доходность, которую требуют инвесторы для ценных бумаг с более длительным сроком погашения для компенсации большей подверженности процентному риску. Долгосрочные облигации более чувствительны к изменениям процентных ставок, чем краткосрочные. Эта премия обычно увеличивается с ростом срока до погашения.",
        "formula": None,
        "los_id": "LOS_1a",
        "calculator": None
    },

    # LOS_1b: Calculate and interpret returns (6 terms)
    {
        "term_id": "QM-1-007",
        "term_en": "Holding Period Return (HPR)",
        "term_ru": "Доходность за период владения",
        "definition_en": "The total return earned from holding an investment for a specified period of time. It includes both capital gains (or losses) from price changes and any income received during the holding period, such as dividends or interest. HPR is the most basic measure of investment return.",
        "definition_ru": "Общая доходность от владения инвестицией за определенный период времени. Включает как прирост капитала (или убытки) от изменения цены, так и любой доход, полученный за период владения, такой как дивиденды или проценты. HPR является самой базовой мерой доходности инвестиций.",
        "formula": "$HPR = \\frac{P_1 - P_0 + D_1}{P_0}$",
        "los_id": "LOS_1b",
        "calculator": {
            "template_id": "DIRECT_HPR"
        }
    },
    {
        "term_id": "QM-1-008",
        "term_en": "Arithmetic Mean Return",
        "term_ru": "Среднее арифметическое доходности",
        "definition_en": "The simple average of a series of returns, calculated by summing all returns and dividing by the number of observations. It represents the expected return for a single period and is most appropriate for forecasting next period's return. The arithmetic mean is always greater than or equal to the geometric mean.",
        "definition_ru": "Простое среднее ряда доходностей, рассчитываемое путем суммирования всех доходностей и деления на количество наблюдений. Представляет ожидаемую доходность за один период и наиболее подходит для прогнозирования доходности следующего периода. Среднее арифметическое всегда больше или равно среднему геометрическому.",
        "formula": "$\\bar{R} = \\frac{1}{n}\\sum_{i=1}^{n}R_i$",
        "los_id": "LOS_1b",
        "calculator": {
            "template_id": "STAT_mean"
        }
    },
    {
        "term_id": "QM-1-009",
        "term_en": "Geometric Mean Return",
        "term_ru": "Среднее геометрическое доходности",
        "definition_en": "The compound annual growth rate of an investment, calculated as the nth root of the product of (1 + return) factors minus 1. It represents the constant return that would need to be earned each period to achieve the same final value. The geometric mean is always less than or equal to the arithmetic mean and is preferred for measuring historical performance.",
        "definition_ru": "Сложная годовая темп роста инвестиции, рассчитываемый как корень n-й степени из произведения факторов (1 + доходность) минус 1. Представляет постоянную доходность, которая должна была бы зарабатываться каждый период для достижения той же конечной стоимости. Среднее геометрическое всегда меньше или равно среднему арифметическому и предпочтительно для измерения исторической эффективности.",
        "formula": "$R_G = \\sqrt[n]{\\prod_{i=1}^{n}(1+R_i)} - 1$",
        "los_id": "LOS_1b",
        "calculator": {
            "template_id": "DIRECT_geometric_mean"
        }
    },
    {
        "term_id": "QM-1-010",
        "term_en": "Harmonic Mean",
        "term_ru": "Среднее гармоническое",
        "definition_en": "The reciprocal of the arithmetic mean of the reciprocals of a set of observations. The harmonic mean is used when averaging ratios or rates and is appropriate for averaging cost-per-share when making regular purchases of different amounts. It is always less than or equal to the geometric mean.",
        "definition_ru": "Обратная величина среднего арифметического обратных величин набора наблюдений. Среднее гармоническое используется при усреднении соотношений или ставок и подходит для усреднения стоимости за акцию при регулярных покупках разных сумм. Оно всегда меньше или равно среднему геометрическому.",
        "formula": "$\\bar{X}_H = \\frac{n}{\\sum_{i=1}^{n}\\frac{1}{X_i}}$",
        "los_id": "LOS_1b",
        "calculator": {
            "method": "Direct Calculation",
            "steps": [
                "Для каждого значения: [1] [÷] {Xi} [=] [STO] i",
                "Суммировать все 1/Xi",
                "[N] [÷] {сумма} [=]"
            ],
            "example": {
                "given": "Values: 2, 4, 8",
                "input": "1÷2=0.5, 1÷4=0.25, 1÷8=0.125, sum=0.875, 3÷0.875=",
                "result": "3.43"
            }
        }
    },
    {
        "term_id": "QM-1-011",
        "term_en": "Trimmed Mean",
        "term_ru": "Усечённое среднее",
        "definition_en": "A measure of central tendency calculated by removing a specified percentage of the highest and lowest observations before computing the arithmetic mean. For example, a 10% trimmed mean removes the highest 10% and lowest 10% of values. This method reduces the influence of outliers while preserving more data than the median.",
        "definition_ru": "Мера центральной тенденции, рассчитываемая путем удаления указанного процента наивысших и наинизших наблюдений перед вычислением среднего арифметического. Например, 10% усечённое среднее удаляет 10% наивысших и 10% наинизших значений. Этот метод снижает влияние выбросов, сохраняя при этом больше данных, чем медиана.",
        "formula": None,
        "los_id": "LOS_1b",
        "calculator": {
            "method": "Multi-step Calculation",
            "description": "Расчёт усечённого среднего вручную",
            "steps": [
                "Шаг 1: Упорядочить данные по возрастанию",
                "Шаг 2: Определить количество значений для удаления с каждой стороны",
                "Шаг 3: Удалить наименьшие и наибольшие значения",
                "Шаг 4: Рассчитать среднее арифметическое оставшихся значений"
            ],
            "example": {
                "given": "10 values, 20% trimmed mean (remove 1 from each end)",
                "result": "Average of middle 8 values"
            }
        }
    },
    {
        "term_id": "QM-1-012",
        "term_en": "Winsorized Mean",
        "term_ru": "Винзоризованное среднее",
        "definition_en": "A measure of central tendency where extreme values are replaced (not removed) with the nearest non-extreme values before calculating the mean. For example, in a 10% winsorized mean, the lowest 10% of values are set equal to the value at the 10th percentile, and the highest 10% are set to the 90th percentile value. This maintains sample size while reducing outlier impact.",
        "definition_ru": "Мера центральной тенденции, при которой экстремальные значения заменяются (а не удаляются) ближайшими не экстремальными значениями перед вычислением среднего. Например, при 10% винзоризованном среднем, наименьшие 10% значений устанавливаются равными значению 10-го перцентиля, а наибольшие 10% - значению 90-го перцентиля. Это сохраняет размер выборки при снижении влияния выбросов.",
        "formula": None,
        "los_id": "LOS_1b",
        "calculator": {
            "method": "Multi-step Calculation",
            "description": "Расчёт винзоризованного среднего вручную",
            "steps": [
                "Шаг 1: Упорядочить данные по возрастанию",
                "Шаг 2: Определить пороговые значения (перцентили)",
                "Шаг 3: Заменить значения ниже нижнего порога на значение порога",
                "Шаг 4: Заменить значения выше верхнего порога на значение порога",
                "Шаг 5: Рассчитать среднее арифметическое всех значений"
            ],
            "example": {
                "given": "10 values, 10% winsorized (replace 1 from each end)",
                "result": "Average of all 10 values after replacement"
            }
        }
    },

    # LOS_1c: MWRR vs TWRR (2 terms)
    {
        "term_id": "QM-1-013",
        "term_en": "Money-Weighted Rate of Return (MWRR)",
        "term_ru": "Денежно-взвешенная норма доходности",
        "definition_en": "The internal rate of return (IRR) on a portfolio, taking into account the timing and magnitude of all cash flows. It measures the growth rate of the actual investment value and is sensitive to the size and timing of contributions and withdrawals. MWRR is most appropriate for individual investors evaluating their personal portfolio performance.",
        "definition_ru": "Внутренняя норма доходности (IRR) портфеля, учитывающая время и величину всех денежных потоков. Измеряет темп роста фактической стоимости инвестиций и чувствительна к размеру и времени вкладов и изъятий. MWRR наиболее подходит для индивидуальных инвесторов, оценивающих эффективность своего личного портфеля.",
        "formula": "$\\sum_{t=0}^{n} \\frac{CF_t}{(1+MWRR)^t} = 0$",
        "los_id": "LOS_1c",
        "calculator": {
            "template_id": "CF_IRR"
        }
    },
    {
        "term_id": "QM-1-014",
        "term_en": "Time-Weighted Rate of Return (TWRR)",
        "term_ru": "Временно-взвешенная норма доходности",
        "definition_en": "A measure of the compound rate of growth of $1 initially invested in a portfolio over a stated time period. It removes the effect of cash flows by calculating returns for each sub-period between cash flows and then compounding these returns. TWRR is the standard for evaluating investment manager performance as it is not affected by client-driven cash flows.",
        "definition_ru": "Мера сложной темпа роста 1 доллара, первоначально инвестированного в портфель за указанный период времени. Устраняет эффект денежных потоков путем расчета доходности для каждого подпериода между денежными потоками с последующим их компаундированием. TWRR является стандартом для оценки эффективности менеджера инвестиций, так как не зависит от денежных потоков, инициированных клиентом.",
        "formula": "$TWRR = [(1+HPR_1)(1+HPR_2)...(1+HPR_n)] - 1$",
        "los_id": "LOS_1c",
        "calculator": {
            "method": "Multi-step Calculation",
            "description": "Расчёт TWRR через последовательность HPR",
            "steps": [
                "Шаг 1: Разбить период на подпериоды между денежными потоками",
                "Шаг 2: Рассчитать HPR для каждого подпериода",
                "Шаг 3: Конвертировать каждый HPR в (1 + HPR)",
                "Шаг 4: Перемножить все (1 + HPR) факторы",
                "Шаг 5: Вычесть 1 для получения TWRR"
            ],
            "example": {
                "given": "HPR1=5%, HPR2=3%, HPR3=7%",
                "input": "1.05 × 1.03 × 1.07 - 1",
                "result": "TWRR = 15.77%"
            }
        }
    },

    # LOS_1d: Annualized returns (2 terms)
    {
        "term_id": "QM-1-015",
        "term_en": "Effective Annual Rate (EAR)",
        "term_ru": "Эффективная годовая ставка",
        "definition_en": "The annual rate of return that accounts for the effect of compounding when interest is paid more frequently than once per year. EAR represents the true annual return and allows for comparison of investments with different compounding frequencies. It is always greater than the stated annual rate when compounding occurs more than once per year.",
        "definition_ru": "Годовая ставка доходности, учитывающая эффект начисления процентов, когда проценты выплачиваются чаще одного раза в год. EAR представляет истинную годовую доходность и позволяет сравнивать инвестиции с разной частотой начисления процентов. Она всегда больше заявленной годовой ставки, когда начисление происходит чаще одного раза в год.",
        "formula": "$EAR = \\left(1 + \\frac{r_s}{m}\\right)^m - 1$",
        "los_id": "LOS_1d",
        "calculator": {
            "template_id": "DIRECT_EAR"
        }
    },
    {
        "term_id": "QM-1-016",
        "term_en": "Continuously Compounded Return",
        "term_ru": "Непрерывно начисляемая доходность",
        "definition_en": "The natural logarithm of the price relative (ending price divided by beginning price). It assumes interest is compounded continuously (infinitely many times per period). Continuously compounded returns are additive over time and symmetric for gains and losses, making them useful for mathematical modeling and risk analysis.",
        "definition_ru": "Натуральный логарифм относительной цены (конечная цена, деленная на начальную цену). Предполагает непрерывное начисление процентов (бесконечное количество раз за период). Непрерывно начисляемые доходности являются аддитивными во времени и симметричными для прибылей и убытков, что делает их полезными для математического моделирования и анализа рисков.",
        "formula": "$r_{cc} = \\ln\\left(\\frac{P_1}{P_0}\\right) = \\ln(1 + HPR)$",
        "los_id": "LOS_1d",
        "calculator": {
            "template_id": "DIRECT_continuous_return"
        }
    },

    # LOS_1e: Types of returns (5 terms)
    {
        "term_id": "QM-1-017",
        "term_en": "Gross Return",
        "term_ru": "Валовая доходность",
        "definition_en": "The total return on an investment before deducting any fees, expenses, or taxes. It represents the return generated by the portfolio manager's investment decisions alone. Gross returns are used to evaluate manager skill independently of the fee structure and are always higher than net returns.",
        "definition_ru": "Общая доходность инвестиции до вычета каких-либо комиссий, расходов или налогов. Представляет доходность, полученную исключительно от инвестиционных решений менеджера портфеля. Валовая доходность используется для оценки навыков менеджера независимо от структуры комиссий и всегда выше чистой доходности.",
        "formula": None,
        "los_id": "LOS_1e",
        "calculator": None
    },
    {
        "term_id": "QM-1-018",
        "term_en": "Net Return",
        "term_ru": "Чистая доходность",
        "definition_en": "The return on an investment after deducting management fees, administrative expenses, and other costs, but typically before personal income taxes. It represents the actual return received by the investor. Net returns are used to evaluate the total value added to the investor after accounting for all investment costs.",
        "definition_ru": "Доходность инвестиции после вычета комиссий за управление, административных расходов и других затрат, но обычно до личных налогов на доходы. Представляет фактическую доходность, полученную инвестором. Чистая доходность используется для оценки общей добавленной стоимости для инвестора после учета всех инвестиционных затрат.",
        "formula": None,
        "los_id": "LOS_1e",
        "calculator": None
    },
    {
        "term_id": "QM-1-019",
        "term_en": "Real Return",
        "term_ru": "Реальная доходность",
        "definition_en": "The return on an investment after adjusting for the effects of inflation. It represents the increase in purchasing power from an investment. Real returns are calculated by removing the inflation component from nominal returns and are essential for evaluating the true economic gain from investments.",
        "definition_ru": "Доходность инвестиции после корректировки на эффекты инфляции. Представляет увеличение покупательной способности от инвестиции. Реальная доходность рассчитывается путем удаления инфляционного компонента из номинальной доходности и является существенной для оценки истинного экономического выигрыша от инвестиций.",
        "formula": "$r_{real} \\approx r_{nominal} - \\pi$ или $r_{real} = \\frac{1 + r_{nominal}}{1 + \\pi} - 1$",
        "los_id": "LOS_1e",
        "calculator": {
            "method": "Direct Calculation",
            "steps": [
                "Приближённая формула: {r_nominal} [-] {inflation} [=]",
                "Точная формула: [(] [1] [+] {r_nominal} [)] [÷] [(] [1] [+] {inflation} [)] [-] [1] [=]"
            ],
            "example": {
                "given": "Nominal return 8%, inflation 3%",
                "input": "Approximate: 0.08 - 0.03 = 5%",
                "result": "Exact: 1.08 ÷ 1.03 - 1 = 4.85%"
            }
        }
    },
    {
        "term_id": "QM-1-020",
        "term_en": "Nominal Return",
        "term_ru": "Номинальная доходность",
        "definition_en": "The return on an investment expressed in current currency units without adjusting for inflation. It includes both the real return and the compensation for inflation. Nominal returns are what investors observe directly but do not reflect changes in purchasing power over time.",
        "definition_ru": "Доходность инвестиции, выраженная в текущих денежных единицах без корректировки на инфляцию. Включает как реальную доходность, так и компенсацию за инфляцию. Номинальная доходность - это то, что инвесторы наблюдают напрямую, но она не отражает изменения покупательной способности с течением времени.",
        "formula": None,
        "los_id": "LOS_1e",
        "calculator": None
    },
    {
        "term_id": "QM-1-021",
        "term_en": "Leveraged Return",
        "term_ru": "Доходность с использованием заёмных средств",
        "definition_en": "The return on an investment when borrowed funds are used to finance part of the investment. Leverage magnifies both gains and losses, making the return more volatile than an unleveraged investment. The leveraged return depends on the relationship between the return on the investment and the cost of borrowing.",
        "definition_ru": "Доходность инвестиции, когда заемные средства используются для финансирования части инвестиции. Кредитное плечо увеличивает как прибыли, так и убытки, делая доходность более волатильной, чем инвестиция без заемных средств. Доходность с заемными средствами зависит от соотношения между доходностью инвестиции и стоимостью заимствования.",
        "formula": "$r_L = r_I + \\frac{Debt}{Equity}(r_I - r_D)$",
        "los_id": "LOS_1e",
        "calculator": {
            "method": "Direct Calculation",
            "steps": [
                "Шаг 1: {r_I} [-] {r_D} [=] — разница доходностей",
                "Шаг 2: [×] {Debt/Equity} [=] — умножить на плечо",
                "Шаг 3: [+] {r_I} [=] — добавить базовую доходность"
            ],
            "example": {
                "given": "Investment return 12%, debt cost 5%, leverage 2:1",
                "input": "(0.12 - 0.05) × 2 + 0.12",
                "result": "Leveraged return = 26%"
            }
        }
    }
]

# Create glossary structure following v4 format
glossary = {
    "book_id": 1,
    "book_code": "QM",
    "book_name": "Quantitative Methods",
    "book_name_ru": "Количественные методы",

    "module_id": 1,
    "module_name": "Rate and Return",
    "module_name_ru": "Ставки и доходность",

    "los_list": ["LOS_1a", "LOS_1b", "LOS_1c", "LOS_1d", "LOS_1e"],
    "total_terms": len(terms),

    "terms": terms
}

# Validation
print(f"\n✅ VALIDATION:")
print(f"   total_terms in metadata: {glossary['total_terms']}")
print(f"   actual terms count: {len(terms)}")
print(f"   los_list: {glossary['los_list']}")

# Check ETALON
expected_count = 21
if len(terms) != expected_count:
    print(f"\n⛔ ETALON CHECK FAILED!")
    print(f"   Expected {expected_count} terms, got {len(terms)}")
else:
    print(f"   ✓ ETALON CHECK PASSED: {expected_count} terms")

# Count terms per LOS
los_counts = {}
for term in terms:
    los = term['los_id']
    los_counts[los] = los_counts.get(los, 0) + 1

print(f"\n📊 Terms per LOS:")
for los in glossary['los_list']:
    count = los_counts.get(los, 0)
    print(f"   {los}: {count} terms")

# Check calculators
calc_count = sum(1 for t in terms if t['calculator'] is not None)
formula_count = sum(1 for t in terms if t['formula'] is not None)
print(f"\n🧮 Calculators:")
print(f"   Terms with formulas: {formula_count}")
print(f"   Terms with calculators: {calc_count}")

# Save
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(glossary, f, indent=2, ensure_ascii=False)

print(f"\n✅ SAVED: {output_path}")
print(f"\nFINAL CHECK: 21 terms across 5 LOS — COMPLETE!")
