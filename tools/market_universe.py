from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import yfinance as yf


ROOT_DIR = Path(__file__).resolve().parents[1]
NIFTY100_PATH = ROOT_DIR / "data" / "nifty100.csv"
REQUIRED_COLUMNS = {"ticker", "company_name", "sector", "industry"}


def _normalize_ticker(ticker: str) -> str:
    symbol = (ticker or "").strip().upper()
    if not symbol:
        return ""
    if symbol.endswith(".NS") or symbol.startswith("^"):
        return symbol
    return f"{symbol}.NS"


@lru_cache(maxsize=512)
def validate_ticker(ticker: str) -> bool:
    symbol = _normalize_ticker(ticker)
    if not symbol:
        return False

    try:
        stock = yf.Ticker(symbol)
        info = stock.info or {}
    except Exception:
        return False

    if info.get("symbol") or info.get("longName") or info.get("shortName"):
        return True

    return False


@lru_cache(maxsize=1)
def load_nifty100() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []

    with NIFTY100_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError(
                "data/nifty100.csv must contain ticker, company_name, sector, industry columns."
            )

        seen: set[str] = set()
        for raw_row in reader:
            ticker = _normalize_ticker(raw_row.get("ticker", ""))
            if not ticker or ticker in seen:
                continue

            rows.append(
                {
                    "ticker": ticker,
                    "company_name": (raw_row.get("company_name") or "").strip(),
                    "sector": (raw_row.get("sector") or "Other").strip() or "Other",
                    "industry": (raw_row.get("industry") or "Other").strip() or "Other",
                }
            )
            seen.add(ticker)

    return rows


@lru_cache(maxsize=2)
def get_tickers(validate: bool = False) -> List[str]:
    tickers = [row["ticker"] for row in load_nifty100()]
    if validate:
        return [ticker for ticker in tickers if validate_ticker(ticker)]
    return tickers


@lru_cache(maxsize=2)
def group_by_sector(validate: bool = False) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}

    for row in load_nifty100():
        ticker = row["ticker"]
        if validate and not validate_ticker(ticker):
            continue

        sector = row.get("sector") or "Other"
        grouped.setdefault(sector, []).append(ticker)

    return grouped


def get_nifty100() -> List[Dict[str, str]]:
    return load_nifty100()


def get_sector_mapping() -> Dict[str, str]:
    return {
        row["ticker"]: row.get("sector", "Other")
        for row in load_nifty100()
    }
