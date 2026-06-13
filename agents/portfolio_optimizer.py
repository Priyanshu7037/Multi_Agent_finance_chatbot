from __future__ import annotations

from typing import Dict, List

from agents.portfolio_optimizer_base import RuleBasedPortfolioOptimizer


class PortfolioOptimizer(RuleBasedPortfolioOptimizer):
    def allocate(
        self,
        sector_rankings: Dict[str, float],
        stock_selection: Dict[str, List[dict[str, object]]],
        existing_holdings: list[str] | None = None,
    ) -> Dict[str, float]:
        if not sector_rankings:
            return {"Cash": 100.0}

        reduced_sector_rankings = {
            sector: score
            for sector, score in sector_rankings.items()
            if score > 0
        }

        if not reduced_sector_rankings:
            reduced_sector_rankings = dict(sector_rankings)

        cash_target = 8.0
        if self.risk_score < 35:
            cash_target += 12.0
        elif self.risk_score < 50:
            cash_target += 8.0
        elif self.risk_score > 75:
            cash_target -= 3.0

        if self.market_regime == "bearish":
            cash_target += 12.0
        elif self.market_regime == "neutral":
            cash_target += 6.0
        elif self.market_regime == "bullish":
            cash_target -= 2.0

        cash_target = max(8.0, min(cash_target, 30.0))
        equity_capacity = 100.0 - cash_target

        sorted_sectors = sorted(
            reduced_sector_rankings.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        top_sectors = [sector for sector, _ in sorted_sectors[:8]]
        sector_values = {
            sector: reduced_sector_rankings[sector]
            for sector in top_sectors
        }

        allocation: Dict[str, float] = {}
        sector_sum = sum(sector_values.values()) or 1.0

        for sector, score in sector_values.items():
            allocation[sector] = (score / sector_sum) * equity_capacity

        if self.risk_score < 50:
            max_sector = 24.0
        elif self.risk_score < 70:
            max_sector = 28.0
        else:
            max_sector = 32.0

        excess = 0.0
        for sector, weight in list(allocation.items()):
            if weight > max_sector:
                excess += weight - max_sector
                allocation[sector] = max_sector

        if excess > 0:
            remaining_sectors = [s for s, w in allocation.items() if w < max_sector]
            remaining_total = sum(allocation[s] for s in remaining_sectors) or 1.0
            for sector in remaining_sectors:
                allocation[sector] += (allocation[sector] / remaining_total) * excess

        allocation = {
            sector: round(weight, 2)
            for sector, weight in allocation.items()
        }

        current_equity = sum(allocation.values())
        if current_equity < equity_capacity:
            slack = equity_capacity - current_equity
            scale = current_equity or 1.0
            for sector in allocation:
                allocation[sector] = round(
                    allocation[sector] + (allocation[sector] / scale) * slack,
                    2,
                )

        allocation["Cash"] = round(cash_target, 2)

        return allocation


def optimize_portfolio(
    risk_score: float,
    market_regime: str,
    sector_rankings: Dict[str, float],
    stock_selection: Dict[str, List[dict[str, object]]],
    existing_holdings: list[str] | None = None,
) -> Dict[str, float]:
    optimizer = PortfolioOptimizer(risk_score=risk_score, market_regime=market_regime)
    return optimizer.allocate(
        sector_rankings=sector_rankings,
        stock_selection=stock_selection,
        existing_holdings=existing_holdings,
    )
