from __future__ import annotations

from math import sqrt
from typing import Any, Dict

from agents.portfolio_sentiment import analyze_portfolio_sentiment
from tools.cache import cached_price_history


def determine_market_regime() -> Dict[str, Any]:
    index_ticker = "^NSEI"

    sentiment_result = analyze_portfolio_sentiment(index_ticker)
    history = cached_price_history(index_ticker, period="6mo")

    momentum_score = 50.0
    volatility_score = 50.0
    breadth_score = 50.0

    if history is not None and not history.empty and "Close" in history:
        close = history["Close"].dropna()
        if len(close) >= 2:
            momentum = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
            momentum_score = 50.0 + max(-50.0, min(50.0, momentum * 100.0))

        returns = close.pct_change().dropna()
        if not returns.empty:
            volatility = float(returns.std() * sqrt(252))
            volatility_score = max(0.0, min(100.0, 100.0 - volatility * 150.0))

        if len(close) >= 200:
            ma50 = close.rolling(50).mean().iloc[-1]
            ma200 = close.rolling(200).mean().iloc[-1]
            if ma50 > ma200:
                breadth_score += 20.0
            if close.iloc[-1] > close.iloc[-21]:
                breadth_score += 10.0
            if close.iloc[-1] > close.iloc[-63]:
                breadth_score += 10.0

    sentiment_score = float(sentiment_result["score"])

    market_score = round(
        0.35 * sentiment_score
        + 0.3 * momentum_score
        + 0.2 * volatility_score
        + 0.15 * breadth_score,
        2,
    )

    if market_score >= 60.0:
        regime = "bullish"
    elif market_score <= 40.0:
        regime = "bearish"
    else:
        regime = "neutral"

    confidence = min(1.0, max(0.0, market_score / 100.0))

    return {
        "regime": regime,
        "confidence": round(confidence, 2),
        "market_score": market_score,
    }
