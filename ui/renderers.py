from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

import streamlit as st


def summarize_assistant_response(graph_state: Dict[str, Any]) -> str:
    workflow = graph_state.get("workflow", "general")
    result = graph_state.get("result")

    if workflow == "committee" and result is not None:
        ticker = getattr(result, "ticker", "the stock")
        decision = getattr(result, "final_decision", "N/A")
        score = getattr(result, "final_score", "N/A")
        confidence = getattr(result, "committee_confidence", "N/A")
        risk = getattr(result, "risk_level", "N/A")
        return (
            f"For {ticker}, the committee decision is {decision} "
            f"with score {score}, confidence {confidence}%, and {risk} risk."
        )

    if isinstance(result, dict):
        title = result.get("title", workflow.title())
        response = result.get("response", "")
        if response:
            return f"{title}\n\n{response}"
        return str(title)

    return (
        "I could not map this query to an implemented workflow yet."
        if not result
        else str(result)
    )


def stream_text(text: str) -> Iterable[str]:
    for token in text.split(" "):
        yield f"{token} "
        time.sleep(0.01)


def render_assistant_message(
    content: str,
    graph_state: Optional[Dict[str, Any]] = None,
    stream: bool = False,
) -> None:
    if stream:
        st.write_stream(stream_text(content))
    else:
        st.markdown(content)

    if graph_state:
        render_workflow_output(graph_state)


def render_workflow_output(graph_state: Dict[str, Any]) -> None:
    workflow = graph_state.get("workflow", "general")
    route = graph_state.get("route", {})

    workflow_label = {
        "compare_and_recommend": "Compare & Recommend",
    }.get(workflow, workflow.title())

    with st.expander("Workflow details", expanded=True):
        cols = st.columns(3)
        cols[0].metric("Workflow", workflow_label)
        cols[1].metric("Ticker", graph_state.get("ticker") or "N/A")
        cols[2].metric(
            "Tickers",
            ", ".join(graph_state.get("tickers") or route.get("tickers") or [])
            or "N/A",
        )

    result = graph_state.get("result")

    if workflow == "committee":
        render_committee(result)
    elif workflow == "compare_and_recommend":
        render_compare_and_recommend(result)
    elif workflow in {
        "history",
        "comparison",
        "portfolio",
        "news",
        "tutor",
        "general",
    }:
        render_report(result)
    else:
        st.info("No implemented workflow matched this query.")


def render_committee(state: Any) -> None:
    if state is None:
        st.warning("No committee result was produced.")
        return

    st.subheader("Committee Decision")
    cols = st.columns(4)
    cols[0].metric("Decision", getattr(state, "final_decision", "N/A"))
    cols[1].metric("Score", getattr(state, "final_score", "N/A"))
    cols[2].metric(
        "Confidence",
        f"{getattr(state, 'committee_confidence', 'N/A')}%",
    )
    cols[3].metric("Risk", getattr(state, "risk_level", "N/A"))

    votes = getattr(state, "committee_votes", None)
    if votes:
        st.write("Committee votes")
        st.table(
            [
                {"Vote": vote, "Count": count}
                for vote, count in votes.items()
            ]
        )

    agents = [
        getattr(state, "fundamental_result", None),
        getattr(state, "sentiment_result", None),
        getattr(state, "quant_result", None),
        getattr(state, "devil_result", None),
    ]

    st.subheader("Agent Analysis")
    for agent in agents:
        render_agent(agent)

    st.subheader("Chair Reasoning")
    st.markdown(getattr(state, "committee_reasoning", "") or "N/A")

    summary = getattr(state, "committee_summary", "")
    if summary:
        st.subheader("Committee Summary")
        st.markdown(summary)


def render_agent(agent: Any) -> None:
    if agent is None:
        return

    with st.container(border=True):
        st.markdown(f"**{agent.agent_name} Agent**")
        cols = st.columns(3)
        cols[0].metric("Score", agent.score)
        cols[1].metric("Confidence", f"{agent.confidence}%")
        cols[2].metric("Recommendation", agent.recommendation)

        left, right = st.columns(2)
        with left:
            st.markdown("**Strengths**")
            render_list(agent.strengths)
        with right:
            st.markdown("**Weaknesses**")
            render_list(agent.weaknesses)

        with st.expander("Reasoning"):
            st.text(agent.reasoning or "N/A")


def render_report(report: Any) -> None:
    if not isinstance(report, dict):
        st.warning("No report was produced.")
        return

    st.subheader(str(report.get("title", "Report")).title())

    data_lines = report.get("data_lines") or []
    if data_lines:
        st.markdown("**Fetched Data**")
        st.code("\n".join(data_lines), language="text")

    response = report.get("response")
    if response:
        st.markdown("**Analysis**")
        st.markdown(response)


def render_compare_and_recommend(result: Any) -> None:
    if not isinstance(result, dict):
        st.warning("No recommendation report was produced.")
        return

    st.subheader("Compare & Recommend")
    cols = st.columns(4)
    cols[0].metric("Winner", result.get("winner") or "N/A")
    cols[1].metric("Confidence", f"{result.get('confidence', 0.0) * 100:.1f}%")
    cols[2].metric("Compared Stocks", ", ".join(result.get("tickers") or []))
    cols[3].metric("Workflow", "Compare & Recommend")

    recommendation = result.get("recommendation")
    if recommendation:
        st.markdown("**Recommendation**")
        st.markdown(recommendation)

    comparison_summary = result.get("comparison_summary")
    if comparison_summary:
        st.markdown("**Detailed Comparison**")
        st.markdown(comparison_summary)


def render_list(items: List[str]) -> None:
    if not items:
        st.caption("None")
        return

    for item in items:
        st.markdown(f"- {item}")
