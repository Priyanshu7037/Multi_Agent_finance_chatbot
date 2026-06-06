from tools.llm import generate_text
from tools.yahoo_finance import (
    get_company_data,
    get_company_news,
    get_price_history
)


def format_value(value):

    if value is None:
        return "N/A"

    if isinstance(value, float):
        return f"{value:.2f}"

    return str(value)


def format_percent(value):

    if value is None:
        return "N/A"

    return f"{value * 100:.2f}%"


def llm_response(prompt, fallback):

    try:
        return generate_text(
            prompt,
            max_tokens=650,
            temperature=0.2
        )
    except Exception as error:
        print(f"Market Workflow LLM Error: {error}")
        return fallback


def build_report(title, data_lines, response):

    return {
        "title": title,
        "data_lines": data_lines,
        "response": response
    }


def history_analysis(ticker):

    history = get_price_history(
        ticker
    )

    if history.empty:
        return build_report(
            "PRICE HISTORY",
            [
                f"Ticker: {ticker}",
                "No price history found."
            ],
            "No analysis generated because price history was unavailable."
        )

    close = history["Close"]
    latest = close.iloc[-1]
    first = close.iloc[0]
    total_return = (
        (latest - first)
        /
        first
    )
    high = close.max()
    low = close.min()
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]
    volatility = close.pct_change().std() * (252 ** 0.5)

    data_lines = [
        f"Ticker: {ticker}",
        (
            f"Period: {history.index[0].date()} to "
            f"{history.index[-1].date()}"
        ),
        f"Latest Close: {latest:.2f}",
        f"Period Return: {format_percent(total_return)}",
        f"High: {high:.2f}",
        f"Low: {low:.2f}",
        f"50-Day Average: {ma50:.2f}",
        f"200-Day Average: {ma200:.2f}",
        f"Annualized Volatility: {format_percent(volatility)}"
    ]

    prompt = f"""
You are a market analyst.

Analyze this stock price history for a retail investor.
Use only the data below.

{chr(10).join(data_lines)}

Write:
1. Trend summary
2. Momentum interpretation
3. Risk note
4. Practical takeaway

Keep it under 180 words.
"""

    response = llm_response(
        prompt,
        "Price history fetched successfully, but no LLM analysis was produced."
    )

    return build_report(
        "PRICE HISTORY",
        data_lines,
        response
    )


def comparison_analysis(tickers):

    tickers = tickers or []
    companies = []

    for ticker in tickers:
        data = get_company_data(
            ticker
        )

        companies.append(
            {
                "ticker": ticker,
                **data
            }
        )

    if not companies:
        return build_report(
            "STOCK COMPARISON",
            [
                "No tickers supplied."
            ],
            "No comparison generated because no tickers were supplied."
        )

    data_lines = []

    for company in companies:
        data_lines.extend(
            [
                f"Ticker: {company['ticker']}",
                f"Company: {format_value(company.get('company_name'))}",
                f"Sector: {format_value(company.get('sector'))}",
                f"Price: {format_value(company.get('current_price'))}",
                f"Market Cap: {format_value(company.get('market_cap'))}",
                f"PE Ratio: {format_value(company.get('pe_ratio'))}",
                (
                    "Revenue Growth: "
                    f"{format_percent(company.get('revenue_growth'))}"
                ),
                (
                    "Earnings Growth: "
                    f"{format_percent(company.get('earnings_growth'))}"
                ),
                (
                    "Debt/Equity: "
                    f"{format_value(company.get('debt_to_equity'))}"
                ),
                (
                    "Free Cash Flow: "
                    f"{format_value(company.get('free_cashflow'))}"
                ),
                ""
            ]
        )

    prompt = f"""
You are an equity comparison analyst.

Compare these companies using only the fetched data below.

{chr(10).join(data_lines)}

Write:
1. Relative valuation
2. Growth comparison
3. Balance-sheet or cash-flow concern
4. Which looks stronger and why

Do not invent missing metrics. Keep it under 220 words.
"""

    response = llm_response(
        prompt,
        "Comparison data fetched successfully, but no LLM analysis was produced."
    )

    return build_report(
        "STOCK COMPARISON",
        data_lines,
        response
    )


def news_analysis(ticker):

    headlines = get_company_news(
        ticker
    )

    data_lines = [
        f"Ticker: {ticker}"
    ]

    if not headlines:
        return build_report(
            "LATEST NEWS",
            data_lines + [
                "No news headlines found."
            ],
            "No news analysis generated because headlines were unavailable."
        )

    data_lines.extend(
        [
            f"- {headline}"
            for headline in headlines
        ]
    )

    prompt = f"""
You are a financial news analyst.

Analyze the likely investor sentiment from these headlines.
Use only these headlines.

{chr(10).join(data_lines)}

Write:
1. Overall sentiment
2. Main positive signals
3. Main risk signals
4. What investors should monitor next

Keep it under 180 words.
"""

    response = llm_response(
        prompt,
        "News headlines fetched successfully, but no LLM analysis was produced."
    )

    return build_report(
        "LATEST NEWS",
        data_lines,
        response
    )


def portfolio_analysis(query, tickers=None):

    tickers = tickers or []
    companies = []

    for ticker in tickers:
        data = get_company_data(
            ticker
        )

        companies.append(
            {
                "ticker": ticker,
                **data
            }
        )

    data_lines = [
        f"Query: {query}"
    ]

    for company in companies:
        data_lines.extend(
            [
                "",
                f"Ticker: {company['ticker']}",
                f"Company: {format_value(company.get('company_name'))}",
                f"Sector: {format_value(company.get('sector'))}",
                f"Market Cap: {format_value(company.get('market_cap'))}",
                f"PE Ratio: {format_value(company.get('pe_ratio'))}",
                (
                    "Revenue Growth: "
                    f"{format_percent(company.get('revenue_growth'))}"
                ),
                (
                    "Debt/Equity: "
                    f"{format_value(company.get('debt_to_equity'))}"
                )
            ]
        )

    if not companies:
        data_lines.append(
            "No specific tickers were supplied by the router."
        )

    prompt = f"""
You are a portfolio allocation assistant.

The user asked:
{query}

Fetched portfolio context:
{chr(10).join(data_lines)}

Give a practical portfolio response.
If tickers are available, discuss diversification and concentration.
If tickers are missing, ask for holdings, capital, time horizon, and risk level,
then give a sample allocation framework.

Do not claim this is personalized financial advice.
Keep it under 220 words.
"""

    response = llm_response(
        prompt,
        (
            "I can help you build an investment plan. Please share your "
            "investment amount, time horizon, risk level, monthly contribution, "
            "and any stocks or funds you already hold. As a general framework, "
            "a balanced plan usually starts with emergency savings, then uses "
            "diversified equity exposure for long-term growth, debt or cash "
            "instruments for stability, and periodic rebalancing. This is "
            "educational guidance, not personalized financial advice."
        )
    )

    return build_report(
        "PORTFOLIO",
        data_lines,
        response
    )
