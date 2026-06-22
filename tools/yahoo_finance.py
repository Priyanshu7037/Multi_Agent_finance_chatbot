from pathlib import Path

import pandas as pd
import yfinance as yf

from tools.nse_universe import is_valid_nse_ticker

CACHE_DIR = Path(__file__).resolve().parents[1] / ".cache" / "yfinance"
CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True
)
yf.set_tz_cache_location(
    str(CACHE_DIR)
)


def _normalize_ticker(ticker: str) -> str:
    symbol = (ticker or "").strip().upper()
    if not symbol:
        raise ValueError("Ticker is required for Yahoo Finance operations.")

    if symbol.endswith(".NS"):
        normalized = symbol
    else:
        normalized = f"{symbol}.NS"

    if not is_valid_nse_ticker(normalized):
        raise ValueError("Ticker is not a valid NSE universe symbol.")

    return normalized


def get_company_news(ticker, limit=10):
    ticker = _normalize_ticker(ticker)

    try:
        stock = yf.Ticker(ticker)

        news = stock.news
    except Exception:
        return []

    headlines = []

    for article in news[:limit]:

        try:

            title = (
                article
                .get("content", {})
                .get("title")
            )

            if title:
                headlines.append(title)

        except Exception:
            pass

    return headlines

def get_company_data(ticker):
    ticker = _normalize_ticker(ticker)

    try:
        stock = yf.Ticker(ticker)

        info = stock.info
    except Exception:
        info = {}

    return {
        "company_name": info.get("longName"),
        "sector": info.get("sector"),
        "market_cap": info.get("marketCap"),
        "current_price": info.get("currentPrice"),
        "pe_ratio": info.get("trailingPE"),

        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),

        "debt_to_equity": info.get("debtToEquity"),

        "free_cashflow": info.get("freeCashflow")
    }
def get_price_history(
    ticker,
    period="1y"
):
    ticker = _normalize_ticker(ticker)

    try:
        stock = yf.Ticker(
            ticker
        )

        return stock.history(
            period=period
        )
    except Exception:
        return pd.DataFrame()
