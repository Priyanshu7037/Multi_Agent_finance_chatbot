from typing import Any, Dict, List, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agents.chair import committee_decision
from agents.coordinator import (
    run_devil,
    run_fundamental,
    run_quant,
    run_sentiment,
    run_summary,
)
from agents.general_assistant import general_assistant_response
from agents.market_workflows import (
    comparison_analysis,
    history_analysis,
    news_analysis,
    portfolio_analysis,
)
from tools.ticker_resolver import resolve_ticker, TickerResolutionError
from agents.compare_and_recommend import compare_and_recommend_analysis
from agents.router import route_query
from agents.tutor import tutor_response
from data.constants import DEFAULT_TICKER
from data.state import InvestmentState


TICKER_WORKFLOWS = {
    "committee",
    "history",
    "comparison",
    "news",
}


class FinanceGraphState(TypedDict, total=False):
    query: str
    route: Dict[str, Any]
    workflow: str
    company_name: str
    ticker: str
    tickers: List[str]
    result: Any
    memory: List[Dict[str, Any]]
    memory_context: str


def get_ticker(route: Dict[str, Any]) -> Optional[str]:
    workflow = route.get("workflow", "general")
    ticker = route.get("ticker")

    if ticker:
        return ticker

    company_name = route.get("company_name")
    if company_name:
        try:
            return resolve_ticker(company_name)
        except TickerResolutionError:
            return None

    tickers = route.get("tickers")
    if tickers:
        return tickers[0]

    if workflow in TICKER_WORKFLOWS:
        return DEFAULT_TICKER

    return None


def summarize_memory(memory: Optional[List[Dict[str, Any]]]) -> str:
    if not memory:
        return ""

    lines = []

    for item in memory[-5:]:
        query = item.get("query", "")
        workflow = item.get("workflow", "general")
        ticker = item.get("ticker")
        tickers = item.get("tickers")
        response = item.get("response_summary", "")

        detail = ticker or ", ".join(tickers or [])

        if detail:
            lines.append(f"- User: {query}")
            lines.append(f"  Workflow: {workflow} ({detail})")
        else:
            lines.append(f"- User: {query}")
            lines.append(f"  Workflow: {workflow}")

        if response:
            lines.append(f"  Assistant: {response}")

    return "\n".join(lines)


def summarize_result(workflow: str, result: Any) -> str:
    if result is None:
        return "No result was produced."

    if workflow == "committee":
        decision = getattr(result, "final_decision", "N/A")
        score = getattr(result, "final_score", "N/A")
        risk = getattr(result, "risk_level", "N/A")

        return (
            f"Committee decision {decision}, score {score}, "
            f"risk {risk}."
        )

    if isinstance(result, dict):
        title = result.get("title", workflow)
        response = result.get("response", "")

        if response:
            return f"{title}: {response[:350]}"

        return str(title)

    return str(result)[:350]


def memory_node(state: FinanceGraphState) -> FinanceGraphState:
    memory = state.get("memory", [])

    return {
        "memory": memory,
        "memory_context": summarize_memory(memory),
    }


def route_node(state: FinanceGraphState) -> FinanceGraphState:
    query = state["query"]
    memory_context = state.get("memory_context", "")
    route = route_query(
        query,
        memory_context=memory_context,
    )
    workflow = route.get("workflow", "general")

    if workflow == "committee" and not route.get("ticker") and not route.get("tickers"):
        route = {
            **route,
            "workflow": "portfolio",
            "tickers": [],
        }
        workflow = "portfolio"

    return {
        "route": route,
        "workflow": workflow,
        "ticker": get_ticker(route),
        "tickers": route.get("tickers") or [],
    }


def committee_node(state: FinanceGraphState) -> FinanceGraphState:
    investment_state = InvestmentState(
        ticker=state.get("ticker") or DEFAULT_TICKER
    )

    investment_state = run_fundamental(investment_state)
    investment_state = run_sentiment(investment_state)
    investment_state = run_quant(investment_state)
    investment_state = run_devil(investment_state)
    investment_state = committee_decision(investment_state)
    investment_state = run_summary(investment_state)

    return {
        "result": investment_state,
    }


def history_node(state: FinanceGraphState) -> FinanceGraphState:
    return {
        "result": history_analysis(state.get("ticker") or DEFAULT_TICKER),
    }


def comparison_node(state: FinanceGraphState) -> FinanceGraphState:
    tickers = state.get("tickers") or [DEFAULT_TICKER]

    return {
        "result": comparison_analysis(tickers),
    }


def compare_and_recommend_node(state: FinanceGraphState) -> FinanceGraphState:
    tickers = state.get("tickers") or [DEFAULT_TICKER]

    return {
        "result": compare_and_recommend_analysis(tickers),
    }


def portfolio_node(state: FinanceGraphState) -> FinanceGraphState:
    return {
        "result": portfolio_analysis(
            state["query"],
            state.get("tickers"),
        ),
    }


def news_node(state: FinanceGraphState) -> FinanceGraphState:
    return {
        "result": news_analysis(state.get("ticker") or DEFAULT_TICKER),
    }


def tutor_node(state: FinanceGraphState) -> FinanceGraphState:
    return {
        "result": {
            "title": "Finance Tutor",
            "response": tutor_response(
                state["query"],
                state.get("memory_context", ""),
            ),
        },
    }


def general_node(state: FinanceGraphState) -> FinanceGraphState:
    return {
        "workflow": "general",
        "result": {
            "title": "General Assistant",
            "response": general_assistant_response(
                state["query"],
                state.get("memory_context", ""),
            ),
        },
    }


def remember_node(state: FinanceGraphState) -> FinanceGraphState:
    memory = list(state.get("memory", []))
    route = state.get("route", {})
    workflow = state.get("workflow", "general")

    memory.append(
        {
            "query": state.get("query", ""),
            "workflow": workflow,
            "company_name": route.get("company_name"),
            "ticker": route.get("ticker") or state.get("ticker"),
            "tickers": route.get("tickers") or state.get("tickers") or [],
            "response_summary": summarize_result(
                workflow,
                state.get("result"),
            ),
        }
    )

    return {
        "memory": memory[-10:],
    }


def select_workflow(state: FinanceGraphState) -> str:
    workflow = state.get("workflow", "general")

    if workflow in {
        "committee",
        "history",
        "comparison",
        "compare_and_recommend",
        "portfolio",
        "news",
        "tutor",
    }:
        return workflow

    return "general"


graph_checkpointer = MemorySaver()


def build_finance_graph():
    graph = StateGraph(FinanceGraphState)

    graph.add_node("memory", memory_node)
    graph.add_node("router", route_node)
    graph.add_node("committee", committee_node)
    graph.add_node("history", history_node)
    graph.add_node("comparison", comparison_node)
    graph.add_node("compare_and_recommend", compare_and_recommend_node)
    graph.add_node("portfolio", portfolio_node)
    graph.add_node("news", news_node)
    graph.add_node("tutor", tutor_node)
    graph.add_node("general", general_node)
    graph.add_node("remember", remember_node)

    graph.add_edge(START, "memory")
    graph.add_edge("memory", "router")
    graph.add_conditional_edges(
        "router",
        select_workflow,
        {
            "committee": "committee",
            "history": "history",
            "comparison": "comparison",
            "compare_and_recommend": "compare_and_recommend",
            "portfolio": "portfolio",
            "news": "news",
            "tutor": "tutor",
            "general": "general",
        },
    )

    for node in [
        "committee",
        "history",
        "comparison",
        "compare_and_recommend",
        "portfolio",
        "news",
        "tutor",
        "general",
    ]:
        graph.add_edge(node, "remember")

    graph.add_edge("remember", END)

    return graph.compile(checkpointer=graph_checkpointer)


finance_graph = build_finance_graph()


def run_finance_graph(
    query: str,
    memory: Optional[List[Dict[str, Any]]] = None,
    thread_id: Optional[str] = None,
):
    config = None
    if thread_id:
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

    state = finance_graph.invoke(
        {
            "query": query,
            "memory": memory or [],
        },
        config=config,
    )

    return state
