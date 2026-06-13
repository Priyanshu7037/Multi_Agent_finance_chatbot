from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from tools.ticker_resolver import resolve_ticker
from tools.yahoo_finance import get_company_data, get_price_history


@lru_cache(maxsize=512)
def cached_company_data(ticker: str) -> Dict[str, Any]:
    resolved_ticker = resolve_ticker(ticker)
    return get_company_data(resolved_ticker)


@lru_cache(maxsize=512)
def cached_price_history(ticker: str, period: str = "1y"):
    resolved_ticker = resolve_ticker(ticker)
    return get_price_history(resolved_ticker, period=period)


@lru_cache(maxsize=512)
def cached_fundamental(ticker: str) -> Any:
    from agents.fundamental import analyze as fundamental_analyze

    return fundamental_analyze(ticker)


@lru_cache(maxsize=512)
def cached_sentiment(ticker: str) -> Any:
    from agents.sentiment import analyze as sentiment_analyze

    return sentiment_analyze(ticker)


@lru_cache(maxsize=512)
def cached_quant(ticker: str) -> Any:
    from agents.quant import analyze as quant_analyze

    return quant_analyze(ticker)
