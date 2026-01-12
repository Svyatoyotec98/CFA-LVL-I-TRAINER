#!/usr/bin/env python3
"""
Parser for CFA Level 1 glossary terms from notes PDFs.
Extracts key terms and definitions, adds formulas from Formula Sheet.
"""

import re
import json
from pathlib import Path

# Book configurations with Russian translations
BOOKS = {
    1: {"name": "Quantitative Methods", "name_ru": "Количественные методы", "prefix": "QM", "formula_section": "QUANTITATIVE"},
    2: {"name": "Economics", "name_ru": "Экономика", "prefix": "ECON", "formula_section": "ECONOMICS"},
    3: {"name": "Corporate Issuers", "name_ru": "Корпоративные эмитенты", "prefix": "CI", "formula_section": None},
    4: {"name": "Financial Statement Analysis", "name_ru": "Анализ финансовой отчётности", "prefix": "FSA", "formula_section": None},
    5: {"name": "Equity Investments", "name_ru": "Инвестиции в акции", "prefix": "EQ", "formula_section": "EQUITY"},
    6: {"name": "Fixed Income", "name_ru": "Инструменты с фиксированным доходом", "prefix": "FI", "formula_section": "FIXED INCOME"},
    7: {"name": "Derivatives", "name_ru": "Деривативы", "prefix": "DER", "formula_section": "DERIVATIVES"},
    8: {"name": "Alternative Investments", "name_ru": "Альтернативные инвестиции", "prefix": "ALT", "formula_section": "ALTERNATIVE"},
    9: {"name": "Portfolio Management", "name_ru": "Управление портфелем", "prefix": "PM", "formula_section": "PORTFOLIO"},
    10: {"name": "Ethics", "name_ru": "Этика", "prefix": "ETH", "formula_section": None},
}

# Common term patterns to extract
TERM_PATTERNS = [
    # "Term is defined as..."
    r'([A-Z][a-zA-Z\s\-\(\)]+)\s+(?:is|are)\s+(?:defined as|the|a|an)\s+([^.]+\.)',
    # "Term refers to..."
    r'([A-Z][a-zA-Z\s\-\(\)]+)\s+refers?\s+to\s+([^.]+\.)',
    # "Term: definition"
    r'^([A-Z][a-zA-Z\s\-\(\)]+):\s+([^.]+\.)',
    # "The term describes..."
    r'([A-Z][a-zA-Z\s\-\(\)]+)\s+describes?\s+([^.]+\.)',
]

# Key terms by book (manually curated important terms)
KEY_TERMS = {
    1: [  # Quantitative Methods
        ("Holding Period Return", "HPR", "Доходность за период владения",
         "The return earned from holding an asset for a specified period.",
         "$HPR = \\frac{P_1 - P_0 + D}{P_0}$"),
        ("Effective Annual Rate", "EAR", "Эффективная годовая ставка",
         "The annual rate of return accounting for compounding effects.",
         "$EAR = (1 + \\frac{r}{m})^m - 1$"),
        ("Present Value", "PV", "Приведённая стоимость",
         "The current worth of a future sum of money given a rate of return.",
         "$PV = \\frac{FV}{(1+r)^n}$"),
        ("Future Value", "FV", "Будущая стоимость",
         "The value of money at a future date based on growth rate.",
         "$FV = PV \\times (1+r)^n$"),
        ("Net Present Value", "NPV", "Чистая приведённая стоимость",
         "The difference between present value of cash inflows and outflows.",
         "$NPV = \\sum \\frac{CF_t}{(1+r)^t}$"),
        ("Internal Rate of Return", "IRR", "Внутренняя норма доходности",
         "The discount rate that makes NPV equal to zero.",
         "$\\sum \\frac{CF_t}{(1+IRR)^t} = 0$"),
        ("Standard Deviation", "σ", "Стандартное отклонение",
         "A measure of dispersion of returns around the mean.",
         "$\\sigma = \\sqrt{\\frac{\\sum(x_i - \\bar{x})^2}{n}}$"),
        ("Variance", "σ²", "Дисперсия",
         "The average squared deviation from the mean.",
         "$\\sigma^2 = \\frac{\\sum(x_i - \\bar{x})^2}{n}$"),
        ("Covariance", "Cov", "Ковариация",
         "A measure of how two variables move together.",
         "$Cov(X,Y) = E[(X-\\mu_X)(Y-\\mu_Y)]$"),
        ("Correlation", "ρ", "Корреляция",
         "Standardized measure of the linear relationship between two variables.",
         "$\\rho = \\frac{Cov(X,Y)}{\\sigma_X \\sigma_Y}$"),
        ("Normal Distribution", None, "Нормальное распределение",
         "A symmetric probability distribution described by mean and standard deviation.", None),
        ("Z-Score", None, "Z-оценка",
         "Number of standard deviations an observation is from the mean.",
         "$z = \\frac{x - \\mu}{\\sigma}$"),
        ("Confidence Interval", None, "Доверительный интервал",
         "A range of values likely to contain the population parameter.", None),
        ("Hypothesis Testing", None, "Проверка гипотез",
         "Statistical method to test claims about population parameters.", None),
        ("Type I Error", "α", "Ошибка I рода",
         "Rejecting a true null hypothesis (false positive).", None),
        ("Type II Error", "β", "Ошибка II рода",
         "Failing to reject a false null hypothesis (false negative).", None),
        ("P-Value", None, "P-значение",
         "Probability of obtaining test results at least as extreme as observed.", None),
        ("T-Test", None, "T-тест",
         "Statistical test using t-distribution for small samples.", None),
        ("Regression", None, "Регрессия",
         "Statistical method to model relationship between variables.",
         "$Y = \\alpha + \\beta X + \\epsilon$"),
        ("R-Squared", "R²", "R-квадрат",
         "Proportion of variance in dependent variable explained by independent variables.",
         "$R^2 = \\frac{SSR}{SST}$"),
    ],
    2: [  # Economics
        ("Demand", None, "Спрос",
         "The quantity of a good consumers are willing to buy at various prices.", None),
        ("Supply", None, "Предложение",
         "The quantity of a good producers are willing to sell at various prices.", None),
        ("Equilibrium", None, "Равновесие",
         "The point where supply equals demand.", None),
        ("Elasticity", None, "Эластичность",
         "Measure of responsiveness of quantity to price changes.",
         "$E = \\frac{\\%\\Delta Q}{\\%\\Delta P}$"),
        ("GDP", None, "ВВП",
         "Total market value of all final goods and services produced in a country.",
         "$GDP = C + I + G + (X - M)$"),
        ("Inflation", None, "Инфляция",
         "Sustained increase in the general price level.", None),
        ("Monetary Policy", None, "Денежно-кредитная политика",
         "Central bank actions to control money supply and interest rates.", None),
        ("Fiscal Policy", None, "Фискальная политика",
         "Government spending and taxation decisions.", None),
        ("Exchange Rate", None, "Обменный курс",
         "Price of one currency in terms of another.", None),
        ("Interest Rate Parity", None, "Паритет процентных ставок",
         "Relationship between interest rates and exchange rates.", None),
        ("Purchasing Power Parity", "PPP", "Паритет покупательной способности",
         "Theory that exchange rates adjust to equalize prices across countries.", None),
    ],
    3: [  # Corporate Issuers
        ("Stakeholder", None, "Заинтересованная сторона",
         "Any party affected by company actions.", None),
        ("Shareholder", None, "Акционер",
         "Owner of company shares with voting rights.", None),
        ("Corporate Governance", None, "Корпоративное управление",
         "System of rules and practices for directing a company.", None),
        ("Board of Directors", None, "Совет директоров",
         "Group elected to represent shareholders and oversee management.", None),
        ("Capital Structure", None, "Структура капитала",
         "Mix of debt and equity financing.",
         "$V = D + E$"),
        ("WACC", None, "WACC (средневзвешенная стоимость капитала)",
         "Weighted Average Cost of Capital.",
         "$WACC = w_d r_d(1-t) + w_e r_e$"),
        ("Cost of Equity", None, "Стоимость собственного капитала",
         "Return required by equity investors.",
         "$r_e = r_f + \\beta(r_m - r_f)$"),
        ("Cost of Debt", None, "Стоимость долга",
         "Interest rate paid on borrowed funds.", None),
        ("Leverage", None, "Финансовый рычаг",
         "Use of borrowed funds to increase potential returns.",
         "$DFL = \\frac{\\%\\Delta EPS}{\\%\\Delta EBIT}$"),
        ("Dividend Policy", None, "Дивидендная политика",
         "Company decisions regarding dividend payments.", None),
    ],
    4: [  # FSA
        ("Balance Sheet", None, "Бухгалтерский баланс",
         "Statement showing assets, liabilities, and equity at a point in time.",
         "$Assets = Liabilities + Equity$"),
        ("Income Statement", None, "Отчёт о прибылях и убытках",
         "Statement showing revenues, expenses, and profit over a period.", None),
        ("Cash Flow Statement", None, "Отчёт о движении денежных средств",
         "Statement showing cash inflows and outflows.", None),
        ("Current Ratio", None, "Коэффициент текущей ликвидности",
         "Measure of short-term liquidity.",
         "$Current\\ Ratio = \\frac{Current\\ Assets}{Current\\ Liabilities}$"),
        ("Quick Ratio", None, "Коэффициент быстрой ликвидности",
         "Liquidity measure excluding inventory.",
         "$Quick\\ Ratio = \\frac{Cash + Receivables}{Current\\ Liabilities}$"),
        ("ROE", None, "Рентабельность собственного капитала",
         "Return on Equity - profitability relative to shareholders' equity.",
         "$ROE = \\frac{Net\\ Income}{Shareholders'\\ Equity}$"),
        ("ROA", None, "Рентабельность активов",
         "Return on Assets - profitability relative to total assets.",
         "$ROA = \\frac{Net\\ Income}{Total\\ Assets}$"),
        ("DuPont Analysis", None, "Анализ Дюпон",
         "Framework decomposing ROE into component ratios.",
         "$ROE = \\frac{NI}{Sales} \\times \\frac{Sales}{Assets} \\times \\frac{Assets}{Equity}$"),
        ("EPS", None, "Прибыль на акцию",
         "Earnings Per Share.",
         "$EPS = \\frac{Net\\ Income - Preferred\\ Dividends}{Weighted\\ Avg\\ Shares}$"),
        ("P/E Ratio", None, "Коэффициент P/E",
         "Price-to-Earnings ratio for valuation.",
         "$P/E = \\frac{Market\\ Price\\ per\\ Share}{EPS}$"),
        ("Depreciation", None, "Амортизация",
         "Allocation of asset cost over its useful life.", None),
        ("Working Capital", None, "Оборотный капитал",
         "Current assets minus current liabilities.",
         "$WC = Current\\ Assets - Current\\ Liabilities$"),
    ],
    5: [  # Equity
        ("Common Stock", None, "Обыкновенные акции",
         "Ownership shares with voting rights and residual claim.", None),
        ("Preferred Stock", None, "Привилегированные акции",
         "Shares with priority dividend but usually no voting rights.", None),
        ("Dividend Discount Model", "DDM", "Модель дисконтирования дивидендов",
         "Valuation model based on present value of future dividends.",
         "$P_0 = \\frac{D_1}{r - g}$"),
        ("Gordon Growth Model", None, "Модель Гордона",
         "DDM assuming constant dividend growth rate.",
         "$P_0 = \\frac{D_0(1+g)}{r - g}$"),
        ("Free Cash Flow", "FCF", "Свободный денежный поток",
         "Cash available after capital expenditures.",
         "$FCF = CFO - CapEx$"),
        ("FCFE", None, "Свободный денежный поток на собственный капитал",
         "Free Cash Flow to Equity.",
         "$FCFE = CFO - CapEx + Net\\ Borrowing$"),
        ("FCFF", None, "Свободный денежный поток фирмы",
         "Free Cash Flow to Firm.",
         "$FCFF = EBIT(1-t) + Depreciation - CapEx - \\Delta WC$"),
        ("Enterprise Value", "EV", "Стоимость предприятия",
         "Total company value including debt.",
         "$EV = Market\\ Cap + Debt - Cash$"),
        ("Market Capitalization", None, "Рыночная капитализация",
         "Total market value of outstanding shares.",
         "$Market\\ Cap = Share\\ Price \\times Shares\\ Outstanding$"),
        ("Book Value", None, "Балансовая стоимость",
         "Value of equity on the balance sheet.", None),
    ],
    6: [  # Fixed Income
        ("Bond", None, "Облигация",
         "Debt security with fixed interest payments and principal repayment.", None),
        ("Coupon Rate", None, "Купонная ставка",
         "Annual interest rate paid on bond face value.", None),
        ("Yield to Maturity", "YTM", "Доходность к погашению",
         "Total return if bond held to maturity.", None),
        ("Current Yield", None, "Текущая доходность",
         "Annual coupon divided by current price.",
         "$Current\\ Yield = \\frac{Annual\\ Coupon}{Current\\ Price}$"),
        ("Duration", None, "Дюрация",
         "Measure of bond price sensitivity to interest rate changes.",
         "$\\%\\Delta P \\approx -Duration \\times \\Delta y$"),
        ("Modified Duration", None, "Модифицированная дюрация",
         "Duration adjusted for yield.",
         "$ModDur = \\frac{MacDur}{1 + y}$"),
        ("Convexity", None, "Выпуклость",
         "Second-order measure of bond price sensitivity.", None),
        ("Credit Spread", None, "Кредитный спред",
         "Yield difference between risky and risk-free bonds.", None),
        ("Zero-Coupon Bond", None, "Бескупонная облигация",
         "Bond that pays no coupons, sold at discount.", None),
        ("Callable Bond", None, "Отзывная облигация",
         "Bond that issuer can redeem before maturity.", None),
        ("Putable Bond", None, "Облигация с правом досрочного погашения",
         "Bond that holder can sell back before maturity.", None),
    ],
    7: [  # Derivatives
        ("Forward Contract", None, "Форвардный контракт",
         "Agreement to buy/sell asset at future date at agreed price.", None),
        ("Futures Contract", None, "Фьючерсный контракт",
         "Standardized forward contract traded on exchange.", None),
        ("Option", None, "Опцион",
         "Right but not obligation to buy/sell at specified price.", None),
        ("Call Option", None, "Колл-опцион",
         "Right to buy underlying asset at strike price.",
         "$Payoff = max(S_T - X, 0)$"),
        ("Put Option", None, "Пут-опцион",
         "Right to sell underlying asset at strike price.",
         "$Payoff = max(X - S_T, 0)$"),
        ("Strike Price", None, "Цена исполнения",
         "Price at which option can be exercised.", None),
        ("Premium", None, "Премия опциона",
         "Price paid for the option contract.", None),
        ("Intrinsic Value", None, "Внутренняя стоимость",
         "Value if option exercised immediately.", None),
        ("Time Value", None, "Временная стоимость",
         "Option premium minus intrinsic value.", None),
        ("Put-Call Parity", None, "Паритет пут-колл",
         "Relationship between put and call prices.",
         "$C + PV(X) = P + S$"),
        ("Swap", None, "Своп",
         "Agreement to exchange cash flows.", None),
        ("Interest Rate Swap", None, "Процентный своп",
         "Exchange of fixed for floating rate payments.", None),
    ],
    8: [  # Alternative Investments
        ("Hedge Fund", None, "Хедж-фонд",
         "Pooled investment using various strategies.", None),
        ("Private Equity", None, "Частный капитал",
         "Investment in non-publicly traded companies.", None),
        ("Venture Capital", None, "Венчурный капитал",
         "Financing for early-stage companies.", None),
        ("Real Estate", None, "Недвижимость",
         "Investment in property and land.", None),
        ("REIT", None, "REIT (инвестиционный траст недвижимости)",
         "Real Estate Investment Trust.", None),
        ("Commodities", None, "Товарные активы",
         "Physical goods like gold, oil, agricultural products.", None),
        ("Infrastructure", None, "Инфраструктура",
         "Investment in public utilities and facilities.", None),
        ("Leverage", None, "Кредитное плечо",
         "Use of borrowed funds to amplify returns.", None),
        ("Illiquidity Premium", None, "Премия за неликвидность",
         "Extra return for investing in illiquid assets.", None),
        ("NAV", None, "СЧА (стоимость чистых активов)",
         "Net Asset Value per share.", None),
    ],
    9: [  # Portfolio Management
        ("Portfolio", None, "Портфель",
         "Collection of investments held by an investor.", None),
        ("Diversification", None, "Диверсификация",
         "Reducing risk by investing in multiple assets.", None),
        ("Systematic Risk", None, "Систематический риск",
         "Market risk that cannot be diversified away.", None),
        ("Unsystematic Risk", None, "Несистематический риск",
         "Company-specific risk that can be diversified.", None),
        ("Beta", "β", "Бета",
         "Measure of systematic risk relative to market.",
         "$\\beta = \\frac{Cov(R_i, R_m)}{Var(R_m)}$"),
        ("CAPM", None, "CAPM (модель оценки капитальных активов)",
         "Capital Asset Pricing Model.",
         "$E(R_i) = R_f + \\beta(E(R_m) - R_f)$"),
        ("Sharpe Ratio", None, "Коэффициент Шарпа",
         "Risk-adjusted return measure.",
         "$Sharpe = \\frac{R_p - R_f}{\\sigma_p}$"),
        ("Treynor Ratio", None, "Коэффициент Трейнора",
         "Return per unit of systematic risk.",
         "$Treynor = \\frac{R_p - R_f}{\\beta_p}$"),
        ("Jensen's Alpha", "α", "Альфа Дженсена",
         "Excess return above CAPM prediction.",
         "$\\alpha = R_p - [R_f + \\beta(R_m - R_f)]$"),
        ("Efficient Frontier", None, "Эффективная граница",
         "Set of optimal portfolios offering highest return for given risk.", None),
        ("Capital Market Line", "CML", "Линия рынка капитала",
         "Line from risk-free rate tangent to efficient frontier.", None),
        ("Security Market Line", "SML", "Линия рынка ценных бумаг",
         "Graph of CAPM showing expected return vs beta.", None),
    ],
    10: [  # Ethics
        ("Code of Ethics", None, "Кодекс этики",
         "Written principles of professional conduct.", None),
        ("Standards of Practice", None, "Стандарты практики",
         "Specific rules for professional behavior.", None),
        ("Fiduciary Duty", None, "Фидуциарная обязанность",
         "Legal obligation to act in client's best interest.", None),
        ("Material Information", None, "Существенная информация",
         "Information that would affect investment decisions.", None),
        ("Insider Trading", None, "Инсайдерская торговля",
         "Trading on material non-public information.", None),
        ("Front Running", None, "Фронт-раннинг",
         "Trading ahead of client orders for personal gain.", None),
        ("Soft Dollars", None, "Мягкие доллары",
         "Using client commissions to pay for research.", None),
        ("GIPS", None, "GIPS (Глобальные стандарты инвестиционной эффективности)",
         "Global Investment Performance Standards.", None),
        ("Fair Dealing", None, "Справедливое обращение",
         "Treating all clients fairly and objectively.", None),
        ("Suitability", None, "Пригодность",
         "Ensuring recommendations match client needs.", None),
    ],
}


def create_glossary(book_id: int) -> dict:
    """Create glossary JSON for a book."""
    config = BOOKS.get(book_id)
    if not config:
        return None

    terms = KEY_TERMS.get(book_id, [])

    glossary_terms = []
    for i, term_data in enumerate(terms, 1):
        term_en, symbol, term_ru, definition, formula = term_data

        term_entry = {
            "term_id": f"T-{config['prefix']}-{str(i).zfill(3)}",
            "term_en": term_en + (f" ({symbol})" if symbol else ""),
            "term_ru": term_ru,
            "definition_en": definition,
            "definition_ru": "",  # Can be filled with translations later
            "formula": formula,
            "module_id": 1,
            "related_los": []
        }
        glossary_terms.append(term_entry)

    return {
        "book_id": book_id,
        "book_name": config["name"],
        "book_name_ru": config["name_ru"],
        "terms": glossary_terms
    }


def main():
    output_dir = Path("/home/user/CFA-LVL-I-TRAINER/frontend/data/glossary")
    output_dir.mkdir(exist_ok=True)

    total_terms = 0

    for book_id in range(1, 11):
        glossary = create_glossary(book_id)
        if glossary:
            output_path = output_dir / f"book{book_id}_terms.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(glossary, f, indent=2, ensure_ascii=False)

            num_terms = len(glossary['terms'])
            total_terms += num_terms
            print(f"Book {book_id} ({glossary['book_name']}): {num_terms} terms")

    print(f"\nTotal: {total_terms} terms across all books")


if __name__ == "__main__":
    main()
