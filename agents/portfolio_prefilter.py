from __future__ import annotations

from typing import Dict, List

from tools.cache import cached_company_data, cached_price_history


def prefilter_stock_universe(
    stock_universe: Dict[str, List[str]],
    max_candidates: int = 30,
) -> Dict[str, List[str]]:
    scored_stocks: list[tuple[float, str, str]] = []

    for sector, tickers in stock_universe.items():
        for ticker in tickers:
            data = cached_company_data(ticker)
            if not data:
                continue

            market_cap = data.get("market_cap") or 0
            if market_cap < 5_000_000_000:
                continue

            history = cached_price_history(ticker, period="6mo")
            required_columns = {"Close", "Volume"}
            if (
                history is None
                or history.empty
                or not required_columns.issubset(set(history.columns))
            ):
                continue

            volume = history["Volume"].dropna()
            close = history["Close"].dropna()
            if len(volume) < 40 or len(close) < 60:
                continue

            avg_volume = float(volume.tail(60).mean() or 0)
            if avg_volume < 100_000:
                continue

            recent_return = 0.0
            if len(close) >= 21:
                prices = close.tail(21)
                recent_return = float((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0])

            current_price = data.get("current_price") or float(close.iloc[-1])
            liquidity_value = avg_volume * current_price
            if liquidity_value < 25_000_000:
                continue

            data_quality = 0.0
            if data.get("revenue_growth") is not None:
                data_quality += 0.33
            if data.get("earnings_growth") is not None:
                data_quality += 0.33
            if data.get("debt_to_equity") is not None:
                data_quality += 0.17
            if data.get("free_cashflow") is not None:
                data_quality += 0.17

            score = (
                min(market_cap / 25_000_000_000, 1.0) * 40
                + min(avg_volume / 3_000_000, 1.0) * 30
                + min(liquidity_value / 1_000_000_000, 1.0) * 10
                + min(max(recent_return, 0.0) / 0.15, 1.0) * 15
                + data_quality * 5
            )

            scored_stocks.append((score, sector, ticker))

    scored_stocks.sort(key=lambda item: item[0], reverse=True)
    filtered: Dict[str, List[str]] = {}

    for score, sector, ticker in scored_stocks[:max_candidates]:
        filtered.setdefault(sector, []).append(ticker)

    return filtered
