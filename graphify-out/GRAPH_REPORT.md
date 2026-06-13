# Graph Report - .  (2026-06-13)

## Corpus Check
- Corpus is ~12,062 words - fits in a single context window. You may not need a graph.

## Summary
- 246 nodes · 629 edges · 11 communities
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]

## God Nodes (most connected - your core abstractions)
1. `resolve_ticker()` - 23 edges
2. `run_portfolio_committee()` - 19 edges
3. `ChatStore` - 16 edges
4. `FinanceGraphState` - 15 edges
5. `generate_text()` - 15 edges
6. `analyze()` - 14 edges
7. `generate_json()` - 12 edges
8. `comparison_analysis()` - 11 edges
9. `analyze()` - 11 edges
10. `AgentOutput` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Any` --uses--> `TickerResolutionError`  [INFERRED]
  agents/portfolio_chair.py → tools/ticker_resolver.py
- `PortfolioState` --uses--> `TickerResolutionError`  [INFERRED]
  agents/portfolio_chair.py → tools/ticker_resolver.py
- `compare_and_recommend_analysis()` --calls--> `generate_text()`  [EXTRACTED]
  agents/compare_and_recommend.py → tools/llm.py
- `analyze()` --calls--> `resolve_ticker()`  [EXTRACTED]
  agents/fundamental.py → tools/ticker_resolver.py
- `FinanceGraphState` --uses--> `InvestmentState`  [INFERRED]
  agents/graph_workflow.py → data/state.py

## Import Cycles
- None detected.

## Communities (11 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (30): build_votes(), committee_decision(), has_earnings_decline(), has_governance_risk(), normalize_recommendation(), run_devil(), run_fundamental(), run_quant() (+22 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (29): generate_summary(), fallback_general_response(), general_assistant_response(), fallback_tutor_response(), tutor_response(), main(), extract_json_from_text(), _find_first_balanced_json() (+21 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (25): _build_score_breakdown(), _build_summary(), _normalize_existing_holdings(), Any, run_portfolio_committee(), determine_market_regime(), Any, prefilter_stock_universe() (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (26): run_finance_graph(), build_error_state(), configure_page(), ensure_active_chat(), get_store(), handle_user_prompt(), initialize_session(), main() (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (21): _build_company_insight(), compare_and_recommend_analysis(), _determine_winner(), _format_list(), _parse_response(), Any, analyze(), calculate_confidence() (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (17): build_report(), comparison_analysis(), format_percent(), format_value(), history_analysis(), llm_response(), news_analysis(), _cached_news_headlines() (+9 more)

### Community 6 - "Community 6"
Cohesion: 0.20
Nodes (7): ChatMessage, ChatStore, ChatThread, Any, Path, Small local persistence layer for Streamlit chat sessions.      When path is Non, utc_now()

### Community 7 - "Community 7"
Cohesion: 0.26
Nodes (12): build_stock_universe(), Return a mapping of sector -> tickers. Supports optional filtering by market_cap, _find_universe_csv_paths(), get_all_tickers(), group_by_sector(), load_nse_universe(), _normalize_text(), Path (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (5): ABC, PortfolioOptimizerBase, RuleBasedPortfolioOptimizer, optimize_portfolio(), PortfolioOptimizer

### Community 9 - "Community 9"
Cohesion: 0.31
Nodes (8): build_router_prompt(), Any, Route a query using a pure LLM Planner Agent., Validate and normalize router output., Build the LLM prompt for planner-style routing., route_query(), validate_route(), main()

### Community 10 - "Community 10"
Cohesion: 0.67
Nodes (5): build_portfolio_planner_prompt(), _normalize_risk_profile(), _parse_numeric_value(), parse_portfolio_query(), Any

## Knowledge Gaps
- **9 isolated node(s):** `Any`, `Any`, `Any`, `Exception`, `Any` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ChatStore` connect `Community 6` to `Community 3`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `resolve_ticker()` connect `Community 5` to `Community 2`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `TickerResolutionError` connect `Community 5` to `Community 1`, `Community 2`, `Community 4`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **What connects `Any`, `Any`, `Any` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.12100840336134454 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.14408602150537633 - nodes in this community are weakly interconnected._