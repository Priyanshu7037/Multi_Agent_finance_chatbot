from __future__ import annotations

from typing import Any, Dict, List

from tools.cache import cached_company_data


def suggest_rebalance(
    current_holdings: List[str],
    current_allocation: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    if not current_holdings:
        return {
            "rebalance_recommendations": [
                "Provide your current holdings and allocation percentages to receive allocation guidance."
            ],
        }

    sector_counts: Dict[str, int] = {}
    ticker_scores: Dict[str, float] = {}
    for ticker in current_holdings:
        data = cached_company_data(ticker)
        sector = data.get("sector") or "Unknown"
        sector_counts[sector] = sector_counts.get(sector, 0) + 1

        score = 0.0
        if data.get("revenue_growth") is not None:
            score += 25
        if data.get("earnings_growth") is not None:
            score += 25
        if data.get("debt_to_equity") is not None:
            score += 25
        if data.get("free_cashflow") is not None:
            score += 25

        ticker_scores[ticker] = min(100.0, score)

    recommendations: List[str] = []
    sorted_sectors = sorted(
        sector_counts.items(), key=lambda item: item[1], reverse=True
    )
    if sorted_sectors:
        top_sector, top_count = sorted_sectors[0]
        if top_count / len(current_holdings) >= 0.4:
            recommendations.append(
                f"Reduce concentration in {top_sector} and add exposure to complementary sectors such as Healthcare, Consumer Defensive, or Financials."
            )

    if len(sorted_sectors) < 4:
        recommendations.append(
            "Increase sector diversification by adding new exposures in at least two additional sectors."
        )

    if current_allocation:
        overweight = [
            f"{sector}: {weight:.0f}%"
            for sector, weight in current_allocation.items()
            if sector != "Cash" and weight >= 30
        ]
        if overweight:
            recommendations.append(
                f"Consider trimming overweight positions: {', '.join(overweight)}."
            )

    if not recommendations:
        recommendations.append(
            "Maintain the current allocation, but revisit it periodically for market and risk regime shifts."
        )

    return {
        "rebalance_recommendations": recommendations,
    }
