from __future__ import annotations

from typing import Any, Dict, List

from data.portfolio_state import PortfolioState
from agents.portfolio_planner import parse_portfolio_query
from agents.portfolio_prefilter import prefilter_stock_universe
from tools.ticker_resolver import TickerResolutionError, resolve_ticker
from agents.portfolio_risk import profile_risk
from agents.portfolio_market import determine_market_regime
from agents.portfolio_rebalance import suggest_rebalance
from agents.portfolio_review import review_portfolio
from agents.portfolio_optimizer import optimize_portfolio
from agents.portfolio_sector_ranking import rank_sectors
from agents.portfolio_stock_selector import select_stocks
from agents.portfolio_stock_universe import build_stock_universe


def _normalize_existing_holdings(holdings: list[Any]) -> List[str]:
    normalized: List[str] = []

    for item in holdings:
        if not item:
            continue

        symbol = str(item).strip()
        try:
            resolved_ticker = resolve_ticker(symbol)
            normalized.append(resolved_ticker)
        except TickerResolutionError:
            continue

    return list(dict.fromkeys(normalized))


def _build_summary(state: PortfolioState) -> str:
    active_sectors = [s for s in state.sector_allocation if s != "Cash"]
    lines: List[str] = ["Portfolio Committee Summary"]
    lines.append(f"Goal: {state.goal or 'General investment'}")
    lines.append(f"Risk Profile: {state.risk_profile} ({state.risk_score:.0f})")
    lines.append(
        f"Market Regime: {state.market_regime.title()} ({state.market_confidence * 100:.0f}%)"
    )

    if state.amount is not None:
        lines.append(f"Target investment amount: ₹{state.amount:,.0f}")
    if state.horizon_years is not None:
        lines.append(f"Investment horizon: {state.horizon_years} years")

    if state.health_score:
        lines.append(f"Portfolio Health Score: {state.health_score:.0f}")

    if active_sectors:
        lines.append(
            f"Recommended sector focus includes {', '.join(active_sectors[:4])}."
        )

    lines.append(
        "The committee uses risk alignment, market regime, sector momentum, and stock quality "
        "to construct a dynamically weighted portfolio."
    )

    if state.rebalance_suggestions:
        lines.append(
            f"Rebalance suggestions: {state.rebalance_suggestions[0]}"
        )

    return "\n\n".join(lines)


def _build_score_breakdown(state: PortfolioState) -> Dict[str, float]:
    allocation_weights = [
        value for name, value in state.sector_allocation.items() if name != "Cash"
    ]
    max_sector = max(allocation_weights) if allocation_weights else 0.0
    distinct_sector_count = len(allocation_weights)

    diversification = min(100.0, 18.0 + distinct_sector_count * 14.0)
    concentration = max(10.0, 100.0 - max(0.0, (max_sector - 20.0) * 1.8))

    average_quality = 50.0
    total_scores = 0.0
    count = 0
    for candidates in state.stock_selection.values():
        for candidate in candidates:
            total_scores += float(candidate.get("score", 50.0))
            count += 1
    if count:
        average_quality = total_scores / count

    risk_alignment = min(100.0, max(0.0, state.risk_score))
    market_alignment = min(100.0, max(0.0, getattr(state, "market_score", 50.0)))

    return {
        "diversification": round(diversification, 2),
        "concentration": round(concentration, 2),
        "stock_quality": round(average_quality, 2),
        "risk_alignment": round(risk_alignment, 2),
        "market_alignment": round(market_alignment, 2),
    }


def run_portfolio_committee(query: str, tickers: list[str] | None = None) -> dict[str, Any]:
    state = PortfolioState(query=query)

    plan = parse_portfolio_query(query)
    state.amount = plan.get("amount")
    state.age = plan.get("age")
    state.goal = plan.get("goal", "")
    state.risk_profile = plan.get("risk_profile", "moderate")
    state.horizon_years = plan.get("horizon_years")
    state.existing_holdings = _normalize_existing_holdings(
        plan.get("existing_holdings", []) + (tickers or [])
    )
    state.sector_preferences = plan.get("sector_preferences", [])
    state.constraints = plan.get("constraints", {})

    risk_profile = profile_risk(
        age=state.age,
        horizon_years=state.horizon_years,
        goal=state.goal,
        user_risk_preference=state.risk_profile,
    )
    state.risk_profile = risk_profile["risk_profile"]
    state.risk_score = float(risk_profile["risk_score"])

    market = determine_market_regime()
    state.market_regime = market["regime"]
    state.market_confidence = float(market["confidence"])
    state.market_score = float(market.get("market_score", 50.0))

    stock_universe = build_stock_universe()
    filtered_universe = prefilter_stock_universe(stock_universe)
    if not filtered_universe:
        filtered_universe = stock_universe

    state.sector_rankings = rank_sectors(filtered_universe)
    state.stock_selection = select_stocks(filtered_universe)
    state.sector_allocation = optimize_portfolio(
        risk_score=state.risk_score,
        market_regime=state.market_regime,
        sector_rankings=state.sector_rankings,
        stock_selection=state.stock_selection,
        existing_holdings=state.existing_holdings,
    )

    state.score_breakdown = _build_score_breakdown(state)
    state.portfolio_score = round(
        0.18 * state.score_breakdown["diversification"]
        + 0.17 * state.score_breakdown["concentration"]
        + 0.29 * state.score_breakdown["stock_quality"]
        + 0.18 * state.score_breakdown["risk_alignment"]
        + 0.18 * state.score_breakdown["market_alignment"],
        2,
    )

    state.health_review = review_portfolio(state.existing_holdings)
    state.health_score = float(state.health_review.get("portfolio_health_score", 0.0))
    state.rebalance_suggestions = (
        suggest_rebalance(state.existing_holdings, current_allocation=state.sector_allocation)
        .get("rebalance_recommendations", [])
    )

    state.confidence = round(
        min(
            1.0,
            0.25 * (state.risk_score / 100.0)
            + 0.25 * state.market_confidence
            + 0.25 * (state.score_breakdown["stock_quality"] / 100.0)
            + 0.25 * (state.health_score / 100.0),
        ),
        2,
    )

    state.summary = _build_summary(state)

    return {
        "title": "PORTFOLIO",
        "response": state.summary,
        "query": state.query,
        "amount": state.amount,
        "age": state.age,
        "horizon_years": state.horizon_years,
        "goal": state.goal,
        "risk_profile": state.risk_profile,
        "risk_score": state.risk_score,
        "market_regime": state.market_regime,
        "market_confidence": state.market_confidence,
        "market_score": state.market_score,
        "sector_rankings": state.sector_rankings,
        "sector_allocation": state.sector_allocation,
        "stock_selection": state.stock_selection,
        "portfolio_score": state.portfolio_score,
        "score_breakdown": state.score_breakdown,
        "confidence": state.confidence,
        "summary": state.summary,
        "existing_holdings": state.existing_holdings,
        "constraints": state.constraints,
        "health_review": state.health_review,
        "health_score": state.health_score,
        "rebalance_suggestions": state.rebalance_suggestions,
    }
