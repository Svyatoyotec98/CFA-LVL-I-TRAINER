#!/usr/bin/env python3
"""
Enhance glossary with Russian translations and calculator instructions
"""

import json
import os

GLOSSARY_DIR = '/home/user/CFA-LVL-I-TRAINER/frontend/data/glossary/'

# Russian translations for common CFA terms
TRANSLATIONS = {
    # Quantitative Methods
    "Holding Period Return (HPR)": "Доходность за период владения",
    "Effective Annual Rate (EAR)": "Эффективная годовая ставка",
    "Present Value (PV)": "Приведённая (текущая) стоимость",
    "Future Value (FV)": "Будущая стоимость",
    "Net Present Value (NPV)": "Чистая приведённая стоимость",
    "Internal Rate of Return (IRR)": "Внутренняя норма доходности",
    "Arithmetic Mean": "Среднее арифметическое",
    "Geometric Mean": "Среднее геометрическое",
    "Harmonic Mean": "Среднее гармоническое",
    "Standard Deviation": "Стандартное отклонение",
    "Variance": "Дисперсия",
    "Covariance": "Ковариация",
    "Correlation": "Корреляция",
    "Coefficient of Variation": "Коэффициент вариации",
    "Skewness": "Асимметрия (скошенность)",
    "Kurtosis": "Эксцесс (куртозис)",
    "Normal Distribution": "Нормальное распределение",
    "Probability": "Вероятность",
    "Expected Value": "Ожидаемое значение",
    "Confidence Interval": "Доверительный интервал",
    "Hypothesis Testing": "Проверка гипотез",
    "t-statistic": "t-статистика",
    "p-value": "p-значение",
    "Type I Error": "Ошибка I рода (ложноположительная)",
    "Type II Error": "Ошибка II рода (ложноотрицательная)",
    "Regression": "Регрессия",
    "R-squared": "Коэффициент детерминации R²",
    "Annuity": "Аннуитет",
    "Perpetuity": "Бессрочная рента (перпетуитет)",
    "Discount Rate": "Ставка дисконтирования",
    "Compounding": "Капитализация (начисление сложных процентов)",
    "Continuously Compounded Return": "Непрерывно начисляемая доходность",
    "Money-Weighted Return": "Денежно-взвешенная доходность",
    "Time-Weighted Return": "Взвешенная по времени доходность",

    # Economics
    "GDP (Gross Domestic Product)": "ВВП (Валовой внутренний продукт)",
    "Inflation": "Инфляция",
    "Deflation": "Дефляция",
    "Supply and Demand": "Спрос и предложение",
    "Equilibrium": "Равновесие",
    "Elasticity": "Эластичность",
    "Price Elasticity of Demand": "Ценовая эластичность спроса",
    "Fiscal Policy": "Фискальная (бюджетная) политика",
    "Monetary Policy": "Денежно-кредитная политика",
    "Exchange Rate": "Обменный курс",
    "Interest Rate": "Процентная ставка",
    "Opportunity Cost": "Альтернативная стоимость",
    "Marginal Cost": "Предельные издержки",
    "Marginal Revenue": "Предельный доход",
    "Consumer Price Index (CPI)": "Индекс потребительских цен (ИПЦ)",
    "Business Cycle": "Экономический цикл",
    "Recession": "Рецессия",
    "Expansion": "Экспансия (подъём)",
    "Central Bank": "Центральный банк",
    "Trade Balance": "Торговый баланс",
    "Current Account": "Счёт текущих операций",
    "Capital Account": "Счёт операций с капиталом",

    # Financial Statement Analysis
    "Balance Sheet": "Балансовый отчёт",
    "Income Statement": "Отчёт о прибылях и убытках",
    "Cash Flow Statement": "Отчёт о движении денежных средств",
    "Assets": "Активы",
    "Liabilities": "Обязательства",
    "Equity": "Собственный капитал",
    "Revenue": "Выручка",
    "Net Income": "Чистая прибыль",
    "Gross Profit": "Валовая прибыль",
    "Operating Income": "Операционная прибыль",
    "EBITDA": "EBITDA (Прибыль до вычета процентов, налогов, износа и амортизации)",
    "EPS (Earnings Per Share)": "Прибыль на акцию",
    "P/E Ratio": "Коэффициент цена/прибыль",
    "ROE (Return on Equity)": "Рентабельность собственного капитала",
    "ROA (Return on Assets)": "Рентабельность активов",
    "Current Ratio": "Коэффициент текущей ликвидности",
    "Quick Ratio": "Коэффициент быстрой ликвидности",
    "Debt-to-Equity Ratio": "Коэффициент долга к собственному капиталу",
    "Working Capital": "Оборотный капитал",
    "Depreciation": "Амортизация основных средств",
    "Amortization": "Амортизация нематериальных активов",
    "Inventory": "Запасы",
    "Accounts Receivable": "Дебиторская задолженность",
    "Accounts Payable": "Кредиторская задолженность",

    # Corporate Finance
    "Capital Structure": "Структура капитала",
    "Cost of Capital": "Стоимость капитала",
    "WACC (Weighted Average Cost of Capital)": "Средневзвешенная стоимость капитала",
    "Cost of Equity": "Стоимость собственного капитала",
    "Cost of Debt": "Стоимость заёмного капитала",
    "Dividend": "Дивиденд",
    "Dividend Yield": "Дивидендная доходность",
    "Capital Budgeting": "Бюджетирование капитала",
    "Payback Period": "Срок окупаемости",
    "Leverage": "Финансовый рычаг (леверидж)",
    "Operating Leverage": "Операционный рычаг",
    "Financial Leverage": "Финансовый рычаг",

    # Equity
    "Stock": "Акция",
    "Common Stock": "Обыкновенные акции",
    "Preferred Stock": "Привилегированные акции",
    "Market Capitalization": "Рыночная капитализация",
    "Book Value": "Балансовая стоимость",
    "Intrinsic Value": "Внутренняя (справедливая) стоимость",
    "Dividend Discount Model (DDM)": "Модель дисконтирования дивидендов",
    "Gordon Growth Model": "Модель Гордона",
    "Free Cash Flow": "Свободный денежный поток",
    "Enterprise Value": "Стоимость предприятия",

    # Fixed Income
    "Bond": "Облигация",
    "Coupon": "Купон",
    "Coupon Rate": "Купонная ставка",
    "Yield to Maturity (YTM)": "Доходность к погашению",
    "Current Yield": "Текущая доходность",
    "Duration": "Дюрация",
    "Modified Duration": "Модифицированная дюрация",
    "Macaulay Duration": "Дюрация Маколея",
    "Convexity": "Выпуклость",
    "Credit Risk": "Кредитный риск",
    "Interest Rate Risk": "Процентный риск",
    "Par Value": "Номинальная стоимость",
    "Premium": "Премия",
    "Discount": "Дисконт",
    "Yield Curve": "Кривая доходности",
    "Spread": "Спред",

    # Derivatives
    "Derivative": "Производный инструмент (дериватив)",
    "Option": "Опцион",
    "Call Option": "Опцион колл (на покупку)",
    "Put Option": "Опцион пут (на продажу)",
    "Strike Price": "Цена исполнения (страйк)",
    "Premium (Option)": "Премия опциона",
    "Expiration Date": "Дата истечения",
    "In the Money": "В деньгах",
    "Out of the Money": "Вне денег",
    "At the Money": "На деньгах",
    "Futures Contract": "Фьючерсный контракт",
    "Forward Contract": "Форвардный контракт",
    "Swap": "Своп",
    "Hedging": "Хеджирование",
    "Delta": "Дельта",
    "Gamma": "Гамма",
    "Theta": "Тета",
    "Vega": "Вега",

    # Alternative Investments
    "Alternative Investments": "Альтернативные инвестиции",
    "Hedge Fund": "Хедж-фонд",
    "Private Equity": "Прямые инвестиции",
    "Real Estate": "Недвижимость",
    "Commodities": "Сырьевые товары",
    "Infrastructure": "Инфраструктура",
    "Venture Capital": "Венчурный капитал",

    # Portfolio Management
    "Portfolio": "Портфель",
    "Diversification": "Диверсификация",
    "Systematic Risk": "Систематический риск",
    "Unsystematic Risk": "Несистематический риск",
    "Beta": "Бета-коэффициент",
    "Alpha": "Альфа",
    "Sharpe Ratio": "Коэффициент Шарпа",
    "Treynor Ratio": "Коэффициент Трейнора",
    "Information Ratio": "Информационный коэффициент",
    "CAPM (Capital Asset Pricing Model)": "Модель оценки капитальных активов",
    "Security Market Line": "Линия рынка ценных бумаг",
    "Efficient Frontier": "Эффективная граница",
    "Risk-Free Rate": "Безрисковая ставка",
    "Market Risk Premium": "Рыночная премия за риск",

    # Ethics
    "Code of Ethics": "Кодекс этики",
    "Standards of Professional Conduct": "Стандарты профессионального поведения",
    "Fiduciary Duty": "Фидуциарная обязанность",
    "Conflict of Interest": "Конфликт интересов",
    "Material Nonpublic Information": "Существенная непубличная информация",
    "Insider Trading": "Инсайдерская торговля",
    "Market Manipulation": "Манипулирование рынком",
    "Suitability": "Пригодность (соответствие)",
    "Fair Dealing": "Добросовестное обращение",
    "Loyalty": "Лояльность",
    "Prudence": "Осмотрительность",
    "Disclosure": "Раскрытие информации",
}

# Russian definitions for terms
DEFINITIONS_RU = {
    "Holding Period Return (HPR)": "Общая доходность актива за определённый период владения, включающая прирост капитала и полученный доход.",
    "Effective Annual Rate (EAR)": "Фактическая годовая процентная ставка с учётом капитализации процентов за год.",
    "Present Value (PV)": "Текущая стоимость будущей суммы денег с учётом временной стоимости денег.",
    "Future Value (FV)": "Стоимость инвестиции в определённый момент в будущем с учётом роста по заданной ставке.",
    "Net Present Value (NPV)": "Разница между приведённой стоимостью денежных притоков и оттоков проекта.",
    "Internal Rate of Return (IRR)": "Ставка дисконтирования, при которой NPV проекта равен нулю.",
    "Standard Deviation": "Мера разброса значений относительно среднего; корень из дисперсии.",
    "Variance": "Средний квадрат отклонений от среднего значения.",
    "Covariance": "Мера совместной изменчивости двух переменных.",
    "Correlation": "Нормализованная мера линейной связи между переменными от -1 до +1.",
    "Beta": "Мера систематического риска актива относительно рынка.",
    "Sharpe Ratio": "Показатель доходности с поправкой на риск: (доходность - безрисковая ставка) / стандартное отклонение.",
    "Duration": "Мера чувствительности цены облигации к изменению процентных ставок.",
    "Yield to Maturity (YTM)": "Полная доходность облигации при удержании до погашения.",
    "P/E Ratio": "Отношение рыночной цены акции к прибыли на акцию; показатель оценки.",
    "ROE (Return on Equity)": "Рентабельность собственного капитала: чистая прибыль / собственный капитал.",
    "WACC (Weighted Average Cost of Capital)": "Средняя стоимость капитала компании, взвешенная по долям источников финансирования.",
}

def enhance_glossary():
    """Add Russian translations and improve glossary"""

    for filename in sorted(os.listdir(GLOSSARY_DIR)):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(GLOSSARY_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)

        modified = False

        for term in data.get('terms', []):
            term_en = term.get('term_en', '')

            # Add Russian term name
            if term_en in TRANSLATIONS and not term.get('term_ru'):
                term['term_ru'] = TRANSLATIONS[term_en]
                modified = True

            # Add Russian definition
            if term_en in DEFINITIONS_RU and not term.get('definition_ru'):
                term['definition_ru'] = DEFINITIONS_RU[term_en]
                modified = True

        if modified:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Updated: {filename}")

if __name__ == "__main__":
    enhance_glossary()
    print("Done!")
