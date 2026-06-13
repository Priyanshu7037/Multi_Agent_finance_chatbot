from tools.ticker_resolver import TickerResolutionError, resolve_ticker
from tools.yahoo_finance import get_company_data
from data.models import AgentOutput

def score_revenue_growth(value):

    if value is None:
        return 0

    if value > 0.20:
        return 20

    elif value > 0.10:
        return 15

    elif value > 0:
        return 10

    return 0

def score_earnings_growth(value):

    if value is None:
        return 0

    if value > 0.20:
        return 20

    elif value > 0.10:
        return 15

    elif value > 0:
        return 10

    return 0

def score_debt(de):

    if de is None:
        return 0

    if de < 50:
        return 20

    elif de < 100:
        return 15

    elif de < 200:
        return 10

    return 0

def score_cashflow(fcf):

    if fcf is None:
        return 0

    if fcf > 0:
        return 20

    return 0

def score_pe(pe):

    if pe is None:
        return 0

    if 5 <= pe <= 30:
        return 20

    return 10

def analyze(ticker):

    try:
        resolved_ticker = resolve_ticker(ticker)
    except TickerResolutionError as error:
        return AgentOutput(
            agent_name="Fundamental",
            score=50,
            confidence=20,
            recommendation="HOLD",
            strengths=[],
            weaknesses=[str(error)],
            reasoning=str(error)
        )

    data = get_company_data(resolved_ticker)

    tracked_values = [
        data.get("revenue_growth"),
        data.get("earnings_growth"),
        data.get("debt_to_equity"),
        data.get("free_cashflow"),
        data.get("pe_ratio"),
    ]

    if all(value is None for value in tracked_values):
        return AgentOutput(
            agent_name="Fundamental",
            score=50,
            confidence=20,
            recommendation="HOLD",
            strengths=[],
            weaknesses=[
                "Fundamental data unavailable"
            ],
            reasoning=(
                "Yahoo Finance fundamental metrics could not be fetched, "
                "so valuation, growth, debt, and cash-flow scoring were "
                "not calculated."
            )
        )

    score = 0

    score += score_revenue_growth(
        data["revenue_growth"]
    )

    score += score_earnings_growth(
        data["earnings_growth"]
    )

    score += score_debt(
        data["debt_to_equity"]
    )

    score += score_cashflow(
        data["free_cashflow"]
    )

    score += score_pe(
        data["pe_ratio"]
    )

    strengths = []
    weaknesses = []

    # Revenue
    revenue_growth = data.get("revenue_growth")

    if revenue_growth is not None:
        if revenue_growth > 0:
            strengths.append(
                f"Revenue growing at {revenue_growth*100:.1f}%"
            )
        else:
            weaknesses.append(
                f"Revenue declined by {abs(revenue_growth)*100:.1f}%"
            )

    # Earnings
    earnings_growth = data.get("earnings_growth")

    if earnings_growth is not None:
        if earnings_growth > 0:
            strengths.append(
                f"Earnings growing at {earnings_growth*100:.1f}%"
            )
        else:
            weaknesses.append(
                f"Earnings declined by {abs(earnings_growth)*100:.1f}%"
            )

    # Debt
    debt = data.get("debt_to_equity")

    if debt is not None:
        if debt < 50:
            strengths.append(
                f"Low debt-to-equity ({debt:.2f})"
            )
        elif debt < 100:
            strengths.append(
                f"Manageable debt-to-equity ({debt:.2f})"
            )
        else:
            weaknesses.append(
                f"High debt-to-equity ({debt:.2f})"
            )

    # Free Cash Flow
    fcf = data.get("free_cashflow")

    if fcf is not None:
        if fcf > 0:
            strengths.append(
                "Positive free cash flow"
            )
        else:
            weaknesses.append(
                "Negative free cash flow"
            )

    # PE Ratio
    pe = data.get("pe_ratio")

    if pe is not None:
        if 5 <= pe <= 30:
            strengths.append(
                f"Reasonable PE ratio ({pe:.2f})"
            )
        elif pe > 30:
            weaknesses.append(
                f"Expensive valuation (PE={pe:.2f})"
            )
        else:
            strengths.append(
                f"Low valuation (PE={pe:.2f})"
            )

    # Dynamic Confidence
    total_points = len(strengths) + len(weaknesses)

    if total_points > 0:
        confidence = int(
            (len(strengths) / total_points) * 100
        )
    else:
        confidence = 50

    # Recommendation
    if score >= 80:
        recommendation = "STRONG BUY"
    elif score >= 60:
        recommendation = "BUY"
    elif score >= 40:
        recommendation = "HOLD"
    else:
        recommendation = "SELL"

    reasoning = f"""
Revenue Growth: {revenue_growth}
Earnings Growth: {earnings_growth}
Debt/Equity: {debt}
PE Ratio: {pe}
Free Cash Flow: {fcf}
"""

    return AgentOutput(
        agent_name="Fundamental",
        score=score,
        confidence=confidence,
        recommendation=recommendation,
        strengths=strengths,
        weaknesses=weaknesses,
        reasoning=reasoning
    )
