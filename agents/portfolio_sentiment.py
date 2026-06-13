from __future__ import annotations

import re
from functools import lru_cache
from typing import Dict, List

from tools.ticker_resolver import resolve_ticker, TickerResolutionError
from tools.yahoo_finance import get_company_news


POSITIVE_KEYWORDS = {
    "accelerate",
    "acquisition",
    "beat",
    "beats",
    "benefit",
    "bullish",
    "buyback",
    "contract",
    "deal",
    "dividend",
    "expansion",
    "gain",
    "gains",
    "growth",
    "higher",
    "improve",
    "improved",
    "improves",
    "launch",
    "leader",
    "outperform",
    "profit",
    "rally",
    "record",
    "recovery",
    "rise",
    "rises",
    "strong",
    "surge",
    "upgrade",
    "wins",
}

NEGATIVE_KEYWORDS = {
    "bearish",
    "concern",
    "cut",
    "decline",
    "declines",
    "delay",
    "downgrade",
    "drop",
    "falls",
    "fraud",
    "headwind",
    "investigation",
    "lawsuit",
    "loss",
    "lower",
    "miss",
    "pressure",
    "probe",
    "risk",
    "selloff",
    "slump",
    "slowdown",
    "weak",
    "weaker",
    "warning",
}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z]+", text.lower())


@lru_cache(maxsize=512)
def _cached_news_headlines(ticker: str, limit: int = 10) -> tuple[str, ...]:
    try:
        resolved_ticker = resolve_ticker(ticker)
    except TickerResolutionError:
        return tuple()

    return tuple(get_company_news(resolved_ticker, limit=limit))


@lru_cache(maxsize=512)
def analyze_portfolio_sentiment(ticker: str) -> Dict[str, object]:
    headlines = _cached_news_headlines(ticker.upper(), limit=10)

    if not headlines:
        return {
            "score": 50,
            "sentiment": "neutral",
            "positive_hits": 0,
            "negative_hits": 0,
            "headline_count": 0,
        }

    tokens = _tokenize(" ".join(headlines))
    positive_hits = sum(1 for token in tokens if token in POSITIVE_KEYWORDS)
    negative_hits = sum(1 for token in tokens if token in NEGATIVE_KEYWORDS)
    total_hits = positive_hits + negative_hits

    if total_hits == 0:
        score = 50
    else:
        polarity = (positive_hits - negative_hits) / total_hits
        confidence_lift = min(25, total_hits * 3)
        score = round(50 + polarity * confidence_lift)

    score = int(max(0, min(100, score)))

    if score >= 65:
        sentiment = "positive"
    elif score <= 35:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "score": score,
        "sentiment": sentiment,
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
        "headline_count": len(headlines),
    }
