from __future__ import annotations

from typing import Dict, List

from agents.portfolio_sentiment import analyze_portfolio_sentiment
from tools.cache import cached_fundamental, cached_quant


def rank_sectors(stock_universe: Dict[str, List[str]]) -> Dict[str, float]:
    sector_scores: Dict[str, float] = {}

    for sector, tickers in stock_universe.items():
        sample = tickers[:8]
        if not sample:
            continue

        fundamentals = []
        sentiments = []
        quant_scores = []

        for ticker in sample:
            fundamental = cached_fundamental(ticker)
            sentiment = analyze_portfolio_sentiment(ticker)
            quant = cached_quant(ticker)

            fundamentals.append(fundamental.score)
            sentiments.append(float(sentiment["score"]))
            quant_scores.append(quant.score)

        if not fundamentals or not sentiments or not quant_scores:
            continue

        average_fundamental = sum(fundamentals) / len(fundamentals)
        average_sentiment = sum(sentiments) / len(sentiments)
        average_quant = sum(quant_scores) / len(quant_scores)

        sector_scores[sector] = round(
            0.5 * average_fundamental
            + 0.3 * average_quant
            + 0.2 * average_sentiment,
            2,
        )

    if not sector_scores:
        return {}

    max_score = max(sector_scores.values())
    if max_score <= 0:
        return {sector: 0.0 for sector in sector_scores}

    normalized = {
        sector: round((score / max_score) * 100.0, 2)
        for sector, score in sector_scores.items()
    }

    return dict(sorted(normalized.items(), key=lambda item: item[1], reverse=True))
