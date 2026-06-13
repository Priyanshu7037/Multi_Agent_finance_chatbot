from __future__ import annotations

from typing import Any, Dict, List

from tools.cache import cached_company_data


def review_portfolio(holdings: List[str]) -> Dict[str, Any]:
    if not holdings:
        return {
            "portfolio_health_score": 50,
            "diversification_score": 50,
            "issues": ["No holdings were provided."],
            "recommendations": ["Share the holdings and allocation percentages for a more accurate review."],
        }

    sector_counts: Dict[str, int] = {}
    qualities: List[float] = []
    missing_data: List[str] = []

    for ticker in holdings:
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

        if score == 0:
            missing_data.append(ticker)
        qualities.append(min(100.0, score))

    total_holdings = len(holdings)
    distinct_sectors = len(sector_counts)
    max_sector_share = max(sector_counts.values(), default=0) / total_holdings

    diversification_score = int(min(100.0, 15 + distinct_sectors * 16))
    concentration_score = int(max(10.0, 100.0 - (max_sector_share * 100.0 - 20.0) * 1.5))
    quality_score = int(sum(qualities) / len(qualities)) if qualities else 50

    issues: List[str] = []
    recommendations: List[str] = []

    if distinct_sectors < 3:
        issues.append("Portfolio is under-diversified across sectors.")
        recommendations.append("Add exposure to at least two additional sectors.")

    if max_sector_share >= 0.5:
        top_sector = max(sector_counts, key=sector_counts.get)
        issues.append(
            f"High concentration in {top_sector} with {max_sector_share * 100:.0f}% of positions."
        )
        recommendations.append(
            f"Reduce exposure to {top_sector} and add defensive or cyclical sectors."
        )

    if missing_data:
        issues.append(
            f"Fundamental data missing for {', '.join(missing_data)}."
        )
        recommendations.append(
            "Review these holdings when full company metrics are available."
        )

    if not issues:
        recommendations.append(
            "Maintain the current holdings while monitoring sector and concentration risk."
        )

    health_score = int(
        (diversification_score * 0.4)
        + (concentration_score * 0.3)
        + (quality_score * 0.3)
    )

    return {
        "portfolio_health_score": min(100, max(0, health_score)),
        "diversification_score": diversification_score,
        "concentration_score": concentration_score,
        "issues": issues,
        "recommendations": recommendations,
    }
