import numpy as np

from data.models import AgentOutput
from tools.ticker_resolver import TickerResolutionError, resolve_ticker

from tools.yahoo_finance import (
    get_price_history
)
def calculate_rsi(
    prices,
    window=14):

    delta = prices.diff()

    gain = (
        delta.where(
            delta > 0,
            0
        )
    ).rolling(window).mean()

    loss = (
        -delta.where(
            delta < 0,
            0
        )
    ).rolling(
        window
    ).mean()

    rs = gain / loss

    rsi = (
        100
        -
        (
            100 /
            (1 + rs)
        )
    )

    return rsi.iloc[-1]

def analyze(ticker):

    try:
        resolved_ticker = resolve_ticker(ticker)
    except TickerResolutionError as error:
        return AgentOutput(
            agent_name="Quant",
            score=50,
            confidence=20,
            recommendation="HOLD",
            strengths=[],
            weaknesses=[str(error)],
            reasoning=str(error)
        )

    df = get_price_history(
        resolved_ticker
    )

    if df.empty or "Close" not in df:
        return AgentOutput(
            agent_name="Quant",
            score=50,
            confidence=30,
            recommendation="HOLD",
            strengths=[],
            weaknesses=[
                "Price history unavailable"
            ],
            reasoning=(
                "Yahoo Finance price history could not be fetched, "
                "so quant indicators were not calculated."
            )
        )

    close = df["Close"]

    if len(close.dropna()) < 200:
        return AgentOutput(
            agent_name="Quant",
            score=50,
            confidence=35,
            recommendation="HOLD",
            strengths=[],
            weaknesses=[
                "Insufficient price history for 50/200-day indicators"
            ],
            reasoning=(
                f"Only {len(close.dropna())} closing prices were available."
            )
        )

    ma50 = (
        close
        .rolling(50)
        .mean()
        .iloc[-1]
    )

    ma200 = (
        close
        .rolling(200)
        .mean()
        .iloc[-1]
    )
    rsi = calculate_rsi(
        close
    )
    returns = (
        close
        .pct_change()
    )

    volatility = (
        returns.std()
        * np.sqrt(252)
    )
    score = 50
    if ma50 > ma200:
        score += 20

    if 40 <= rsi <= 70:
        score += 20

    if volatility < 0.30:
        score += 10

    strengths = []
    weaknesses = []
    if ma50 > ma200:

        strengths.append(
            "Bullish trend (50 MA above 200 MA)"
        )

    else:

        weaknesses.append(
            "Bearish trend (50 MA below 200 MA)"
        )
    if rsi > 70:

        weaknesses.append(
            f"Overbought RSI ({rsi:.1f})"
        )

    elif rsi < 30:

        weaknesses.append(
            f"Oversold RSI ({rsi:.1f})"
        )

    else:

        strengths.append(
            f"Healthy RSI ({rsi:.1f})"
        )
    if volatility < 0.30:

        strengths.append(
            "Low volatility"
        )

    else:

        weaknesses.append(
            "High volatility"
        )
    if score >= 80:

        recommendation = "BUY"

    elif score >= 60:

        recommendation = "HOLD"

    else:

        recommendation = "SELL"
    return AgentOutput(
        agent_name="Quant",
        score=score,
        confidence=80,
        recommendation=recommendation,
        strengths=strengths,
        weaknesses=weaknesses,
        reasoning=f"""
MA50={ma50:.2f}

MA200={ma200:.2f}

RSI={rsi:.2f}

Volatility={volatility:.2f}
"""
    )

