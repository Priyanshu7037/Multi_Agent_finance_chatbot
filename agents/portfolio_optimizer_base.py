from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List


class PortfolioOptimizerBase(ABC):
    def __init__(self, risk_score: float, market_regime: str):
        self.risk_score = risk_score
        self.market_regime = market_regime

    @abstractmethod
    def allocate(
        self,
        sector_rankings: Dict[str, float],
        stock_selection: Dict[str, List[dict[str, object]]],
        existing_holdings: list[str] | None = None,
    ) -> Dict[str, float]:
        pass


class RuleBasedPortfolioOptimizer(PortfolioOptimizerBase):
    def allocate(
        self,
        sector_rankings: Dict[str, float],
        stock_selection: Dict[str, List[dict[str, object]]],
        existing_holdings: list[str] | None = None,
    ) -> Dict[str, float]:
        raise NotImplementedError(
            "RuleBasedPortfolioOptimizer must be implemented by a concrete optimizer."
        )
