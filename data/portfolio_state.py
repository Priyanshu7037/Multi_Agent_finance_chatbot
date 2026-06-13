from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PortfolioState:
    query: str
    amount: float | None = None
    age: int | None = None
    horizon_years: int | None = None
    goal: str = ""
    risk_profile: str = "moderate"
    risk_score: float = 50.0
    market_regime: str = "neutral"
    market_confidence: float = 0.0
    market_score: float = 0.0
    sector_rankings: dict[str, float] = field(default_factory=dict)
    sector_allocation: dict[str, float] = field(default_factory=dict)
    stock_selection: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    portfolio_score: float = 0.0
    score_breakdown: dict[str, float] = field(default_factory=dict)
    health_score: float = 0.0
    health_review: dict[str, Any] = field(default_factory=dict)
    rebalance_suggestions: list[str] = field(default_factory=list)
    confidence: float = 0.0
    summary: str = ""
    existing_holdings: list[str] = field(default_factory=list)
    sector_preferences: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
