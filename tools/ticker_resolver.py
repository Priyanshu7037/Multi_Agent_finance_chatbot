from __future__ import annotations

from functools import lru_cache
from typing import Optional

from tools.nse_universe import search_company

import yfinance as yf


class TickerResolutionError(ValueError):
    pass


def _normalize_input(raw_value: str) -> str:
    return str(raw_value or "").strip()


@lru_cache(maxsize=512)
def validate_ticker(ticker: str) -> bool:
    symbol = (ticker or "").strip().upper()
    if not symbol:
        return False

    try:
        stock = yf.Ticker(symbol)
        info = stock.info or {}
    except Exception:
        return False

    return bool(info.get("symbol") or info.get("longName") or info.get("shortName"))


ALIASES = {
    "HDFC": "HDFCBANK.NS",
    "AIRTEL": "BHARTIARTL.NS",
}


@lru_cache(maxsize=2048)
def resolve_ticker(raw_value: str) -> str:
    value = _normalize_input(raw_value)
    if not value:
        raise TickerResolutionError("No ticker or company name was provided.")

    candidate = value.strip().upper()

    # special alias shortcuts
    if candidate in ALIASES:
        return ALIASES[candidate]

    # if the input already looks like an NSE symbol, validate it
    if candidate.endswith(".NS") or candidate.startswith("^"):
        if validate_ticker(candidate):
            return candidate

    # company lookups should come from the NSE universe CSV
    company_match = search_company(value)
    if company_match and validate_ticker(company_match):
        return company_match

    # alpha-only ticker names may still resolve by appending .NS
    if candidate.isalpha():
        norm = f"{candidate}.NS"
        if validate_ticker(norm):
            return norm

    raise TickerResolutionError(f"Could not resolve '{raw_value}' to a valid NSE ticker.")

