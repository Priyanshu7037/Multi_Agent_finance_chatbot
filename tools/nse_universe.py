from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional


ROOT_DIR = Path(__file__).resolve().parents[1]
NSE_DATA_DIR = ROOT_DIR / "data"
REQUIRED_COLUMNS = {"ticker", "company_name", "sector", "industry", "market_cap_category"}


def _find_universe_csv_paths() -> List[Path]:
    primary = NSE_DATA_DIR / "nse_equities.csv"
    if primary.exists():
        try:
            with primary.open("r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh)
                headers = {name.strip().lower() for name in reader.fieldnames or []}
                if REQUIRED_COLUMNS.issubset(headers):
                    return [primary]
        except Exception:
            pass

    paths: List[Path] = []
    for path in sorted(NSE_DATA_DIR.glob("*.csv")):
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh)
                if not reader.fieldnames:
                    continue
                headers = {name.strip().lower() for name in reader.fieldnames if name}
                if REQUIRED_COLUMNS.issubset(headers):
                    paths.append(path)
        except Exception:
            continue
    return paths


def _normalize_text(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", " ", (value or "").strip())
    return re.sub(r"\s+", " ", cleaned).strip().lower()


@lru_cache(maxsize=1)
def load_nse_universe() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    paths = _find_universe_csv_paths()
    if not paths:
        return rows

    seen = set()
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames:
                continue
            headers = {name.strip().lower() for name in reader.fieldnames if name}
            if not REQUIRED_COLUMNS.issubset(headers):
                continue

            for raw in reader:
                ticker = (raw.get("ticker") or "").strip().upper()
                if not ticker or ticker in seen:
                    continue

                rows.append(
                    {
                        "ticker": ticker,
                        "company_name": (raw.get("company_name") or "").strip(),
                        "sector": (raw.get("sector") or "Other").strip() or "Other",
                        "industry": (raw.get("industry") or "Other").strip() or "Other",
                        "market_cap_category": (raw.get("market_cap_category") or "Unknown").strip() or "Unknown",
                    }
                )
                seen.add(ticker)

    return rows


@lru_cache(maxsize=2)
def get_all_tickers(validate: bool = False) -> List[str]:
    tickers = [row["ticker"] for row in load_nse_universe()]
    if validate:
        # import locally to avoid circular imports at module import time
        from tools.ticker_resolver import validate_ticker

        return [t for t in tickers if validate_ticker(t)]
    return tickers


@lru_cache(maxsize=2)
def group_by_sector(validate: bool = False) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    for row in load_nse_universe():
        ticker = row["ticker"]
        if validate:
            from tools.ticker_resolver import validate_ticker

            if not validate_ticker(ticker):
                continue

        sector = row.get("sector") or "Other"
        grouped.setdefault(sector, []).append(ticker)

    return grouped


def _score_company_name(query: str, cleaned_name: str) -> int:
    tokens = query.split()
    name_tokens = cleaned_name.split()
    score = 0

    if all(token in name_tokens for token in tokens):
        score += 20 * len(tokens)

    if cleaned_name.startswith(query):
        score += 15

    if query in cleaned_name:
        score += 10

    compact_query = query.replace(" ", "")
    if compact_query in cleaned_name.replace(" ", ""):
        score += 5

    score -= len(name_tokens)
    return score


@lru_cache(maxsize=1)
def _get_nse_ticker_set() -> set[str]:
    return {row["ticker"] for row in load_nse_universe()}


@lru_cache(maxsize=1024)
def is_valid_nse_ticker(ticker: str) -> bool:
    symbol = (ticker or "").strip().upper()
    if not symbol:
        return False

    ticker_set = _get_nse_ticker_set()
    if symbol in ticker_set:
        return True

    if symbol.endswith(".NS"):
        return False

    return f"{symbol}.NS" in ticker_set


@lru_cache(maxsize=1024)
def search_company_candidates(query: str) -> List[str]:
    """Return ranked ticker candidates for a company query."""
    from difflib import get_close_matches

    if not query:
        return []

    q = query.strip().lower()
    rows = load_nse_universe()
    if not rows:
        return []

    ticker_map: Dict[str, str] = {}
    company_names: Dict[str, str] = {}
    cleaned_company_names: Dict[str, str] = {}
    compact_names: Dict[str, str] = {}

    for r in rows:
        ticker = r["ticker"].lower()
        ticker_map[ticker] = r["ticker"]
        if ticker.endswith(".ns"):
            ticker_map[ticker[:-3]] = r["ticker"]

        name = (r["company_name"] or "").strip()
        if not name:
            continue

        normalized_name = name.lower()
        cleaned_name = _normalize_text(name)
        compact_name = cleaned_name.replace(" ", "")

        company_names[normalized_name] = r["ticker"]
        cleaned_company_names[cleaned_name] = r["ticker"]
        compact_names[compact_name] = r["ticker"]

    results: List[str] = []
    compact_q = q.replace(" ", "")

    # exact company name and normalized variations
    if q in company_names:
        results.append(company_names[q])

    if q in cleaned_company_names and cleaned_company_names[q] not in results:
        results.append(cleaned_company_names[q])

    if compact_q in compact_names and compact_names[compact_q] not in results:
        results.append(compact_names[compact_q])

    # If no company-name based candidate is found, allow exact ticker match as fallback
    if not results and q in ticker_map:
        return [ticker_map[q]]

    scored: Dict[str, int] = {}

    if q in cleaned_company_names and cleaned_company_names[q] not in results:
        results.append(cleaned_company_names[q])

    if compact_q in compact_names and compact_names[compact_q] not in results:
        results.append(compact_names[compact_q])

    scored: Dict[str, int] = {}
    for cleaned_name, ticker in cleaned_company_names.items():
        score = _score_company_name(q, cleaned_name)
        if score > 0:
            scored[ticker] = max(scored.get(ticker, 0), score)

    for ticker, _ in sorted(scored.items(), key=lambda item: (-item[1], item[0])):
        if ticker not in results:
            results.append(ticker)

    if results:
        return results

    all_names = list(company_names.keys()) + list(cleaned_company_names.keys()) + list(ticker_map.keys()) + list(compact_names.keys())
    matches = get_close_matches(q, all_names, n=5, cutoff=0.65)
    for key in matches:
        candidate = company_names.get(key) or cleaned_company_names.get(key) or ticker_map.get(key) or compact_names.get(key)
        if candidate and candidate not in results:
            results.append(candidate)

    return results


@lru_cache(maxsize=1024)
def search_company(query: str) -> str | None:
    candidates = search_company_candidates(query)
    return candidates[0] if candidates else None
