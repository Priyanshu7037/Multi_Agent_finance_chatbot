from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from tools.nse_universe import is_valid_nse_ticker, search_company


class TickerResolutionError(ValueError):
    pass


def _normalize_input(raw_value: str) -> str:
    return str(raw_value or "").strip()


@lru_cache(maxsize=2048)
def resolve_ticker(raw_value: str) -> str:
    value = _normalize_input(raw_value)
    if not value:
        raise TickerResolutionError("No company name was provided.")

    candidate = value.strip()
    candidate_upper = candidate.upper()

    if candidate_upper.endswith(".NS") or candidate_upper.startswith("^"):
        raise TickerResolutionError(
            "Ticker symbol input is not allowed. Provide a company name from the NSE universe."
        )

    company_match = search_company(candidate)
    if not company_match:
        raise TickerResolutionError("Company not found in NSE universe")

    if not is_valid_nse_ticker(company_match):
        raise TickerResolutionError("Resolved company ticker is not valid in NSE universe")

    return company_match


@lru_cache(maxsize=512)
def resolve_ticker_safe(raw_value: str) -> Dict[str, Any]:
    try:
        ticker = resolve_ticker(raw_value)
        return {"success": True, "ticker": ticker}
    except TickerResolutionError as error:
        return {"success": False, "error": str(error)}

