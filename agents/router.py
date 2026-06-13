from __future__ import annotations

from typing import Any, Dict, List

from tools.llm import generate_json


AVAILABLE_WORKFLOWS = [
    "committee",
    "history",
    "comparison",
    "compare_and_recommend",
    "portfolio",
    "news",
    "tutor",
    "general",
]


def validate_route(route: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize router output."""
    workflow = route.get("workflow")
    if not isinstance(workflow, str) or workflow not in AVAILABLE_WORKFLOWS:
        workflow = "general"

    ticker = route.get("ticker")
    if ticker is not None and not isinstance(ticker, str):
        ticker = None

    company_name = route.get("company_name")
    if company_name is not None and not isinstance(company_name, str):
        company_name = None

    tickers = route.get("tickers")
    if isinstance(tickers, list):
        tickers = [str(item) for item in tickers if isinstance(item, str)]
    else:
        tickers = []

    confidence = route.get("confidence")
    if isinstance(confidence, (float, int)):
        confidence = float(confidence)
        confidence = max(0.0, min(1.0, confidence))
    else:
        confidence = 0.0

    reason = route.get("reason")
    if not isinstance(reason, str):
        reason = ""

    agents = route.get("agents")
    if isinstance(agents, list):
        agents = [str(agent) for agent in agents if isinstance(agent, str)]
    else:
        agents = None

    validated: Dict[str, Any] = {
        "workflow": workflow,
        "ticker": ticker,
        "company_name": company_name,
        "tickers": tickers,
        "confidence": confidence,
        "reason": reason,
    }

    if agents is not None:
        validated["agents"] = agents

    return validated


def build_router_prompt(query: str, memory_context: str) -> str:
    """Build the LLM prompt for planner-style routing."""
    memory_text = memory_context.strip() or "No previous chat memory."

    return (
        "You are a planner agent for an AI financial assistant.\n"
        "Your job is to classify only the current user query into one workflow.\n"
        "Use conversation memory only to resolve references such as 'it', 'that stock', 'the other company', or 'compare them'.\n"
        "Do not classify the memory itself.\n"
        "Return valid JSON only with no markdown or additional text.\n"
        "Supported workflows: committee, history, comparison, compare_and_recommend, portfolio, news, tutor, general.\n"
        "Required fields: workflow, confidence, reason.\n"
        "Optional fields: company_name, ticker, tickers, agents.\n"
        "If the user asks for stock recommendation or investment advice about a single stock, prefer 'committee'.\n"
        "If the user asks for price history, choose 'history'.\n"
        "If the user asks for comparison only, choose 'comparison'.\n"
        "If the user asks to compare multiple stocks and choose one, choose 'compare_and_recommend'.\n"
        "If the user asks about a single company, return company_name instead of NSE ticker symbols.\n"
        "If the user asks about portfolio allocation, invest ₹X, build a portfolio, "
        "create diversification, select a retirement portfolio, or allocate money, choose 'portfolio'.\n"
        "If the user asks for news sentiment, choose 'news'.\n"
        "If the user asks for an explanation or definition, choose 'tutor'.\n"
        "Conversation Memory:\n"
        f"{memory_text}\n"
        "User Query:\n"
        f"{query.strip()}\n"
        "Example output:\n"
        "{\n"
        "  \"workflow\": \"committee\",\n"
        "  \"company_name\": \"TCS\",\n"
        "  \"tickers\": [\"TCS.NS\"],\n"
        "  \"confidence\": 0.96,\n"
        "  \"reason\": \"User asks for a recommendation on a single stock.\",\n"
        "}\n"
        "{\n"
        "  \"workflow\": \"comparison\",\n"
        "  \"tickers\": [\"TCS.NS\", \"INFY.NS\"],\n"
        "  \"confidence\": 0.94,\n"
        "  \"reason\": \"User asked to compare two stocks without choosing one.\",\n"
        "}\n"
        "{\n"
        "  \"workflow\": \"compare_and_recommend\",\n"
        "  \"tickers\": [\"WIPRO.NS\", \"TCS.NS\"],\n"
        "  \"confidence\": 0.92,\n"
        "  \"reason\": \"User wants to compare multiple stocks and choose one.\",\n"
        "}\n"
        "{\n"
        "  \"workflow\": \"history\",\n"
        "  \"company_name\": \"Infosys\",\n"
        "  \"confidence\": 0.91,\n"
        "  \"reason\": \"User requested stock price history.\",\n"
        "}"
    )


def route_query(query: str, memory_context: str = "") -> Dict[str, Any]:
    """Route a query using a pure LLM Planner Agent."""
    prompt = build_router_prompt(query, memory_context)

    try:
        raw_result = generate_json(
            prompt=prompt,
            max_tokens=300,
            temperature=0.1,
        )
        return validate_route(raw_result)

    except Exception as error:
        print(f"Router Error: {error}")
        return {
            "workflow": "general",
            "ticker": None,
            "tickers": [],
            "confidence": 0.0,
            "reason": "Planner agent failed to classify the query.",
        }
