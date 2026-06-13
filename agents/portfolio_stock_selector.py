from __future__ import annotations

from typing import Dict, List

from agents.portfolio_sentiment import analyze_portfolio_sentiment
from tools.cache import cached_fundamental, cached_quant


def select_stocks(
    stock_universe: Dict[str, List[str]],
    top_n: int = 4,
) -> Dict[str, List[dict[str, object]]]:
    selection: Dict[str, List[dict[str, object]]] = {}

    for sector, tickers in stock_universe.items():
        candidates: List[dict[str, object]] = []

        for ticker in tickers[:10]:
            fundamental = cached_fundamental(ticker)
            sentiment = analyze_portfolio_sentiment(ticker)
            quant = cached_quant(ticker)

            score = round(
                0.5 * fundamental.score
                + 0.3 * quant.score
                + 0.2 * float(sentiment["score"]),
                2,
            )

            candidates.append(
                {
                    "ticker": ticker,
                    "score": score,
                    "fundamental_score": fundamental.score,
                    "sentiment_score": sentiment["score"],
                    "sentiment": sentiment["sentiment"],
                    "quant_score": quant.score,
                }
            )

        candidates.sort(key=lambda item: item["score"], reverse=True)
        selection[sector] = candidates[:top_n]

    return selection
