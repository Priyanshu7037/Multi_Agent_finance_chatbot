from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st
from agents.graph_workflow import run_finance_graph
from memory import ChatMessage, ChatStore
from ui import (
    render_assistant_message,
    render_sidebar,
    summarize_assistant_response,
)
import uuid


QUERY_TEMPLATES: Dict[str, List[Dict[str, str]]] = {
    "📊 Portfolio": [
        {
            "label": "Build a Portfolio",
            "query": "I am 25 years old and have ₹10 lakh to invest for 15 years. Build a portfolio.",
        },
        {
            "label": "Review Existing Portfolio",
            "query": "I own TCS, Infosys and Reliance. Review my portfolio.",
        },
    ],
    "📈 Stocks": [
        {
            "label": "Compare Stocks",
            "query": "Compare TCS and Infosys and tell me which is better.",
        },
        {
            "label": "Stock Recommendation",
            "query": "Should I invest in Reliance Industries?",
        },
        {
            "label": "Stock History",
            "query": "Show historical performance of HDFC Bank.",
        },
    ],
    "📰 News": [
        {
            "label": "Latest News",
            "query": "What is the latest news about TCS?",
        },
    ],
    "🎓 Learn": [
        {
            "label": "Learn a Finance Concept",
            "query": "What is EBITDA?",
        },
    ],
}


def initialize_session() -> None:
    if "_session_id" not in st.session_state:
        st.session_state["_session_id"] = str(uuid.uuid4())

    if "guided_query_text" not in st.session_state:
        st.session_state.guided_query_text = ""

    if "guided_query_category" not in st.session_state:
        st.session_state.guided_query_category = next(iter(QUERY_TEMPLATES))


def get_store() -> ChatStore:
    session_key = "chat_store"

    if session_key not in st.session_state:
        # Use session-only memory for chat history by default.
        # No cross-user persistence or disk I/O occurs when path=None.
        st.session_state[session_key] = ChatStore(path=None)

    return st.session_state[session_key]


def configure_page() -> None:
    st.set_page_config(
        page_title="Finance Assistant",
        page_icon=":chart_with_upwards_trend:",
        layout="wide",
    )
    st.title("Finance Assistant")
    st.caption("Multi-agent equity analysis with LangGraph routing and memory.")


def ensure_active_chat(store: ChatStore) -> str:
    active_chat_id = st.session_state.get("active_chat_id")
    threads = store.list_threads()

    if active_chat_id:
        return active_chat_id

    if threads:
        active_chat_id = threads[0].id
    else:
        active_chat_id = store.create_thread().id

    st.session_state.active_chat_id = active_chat_id
    return active_chat_id


def render_history(store: ChatStore, chat_id: str) -> None:
    thread = store.get_thread(chat_id)

    for message in thread.messages:
        with st.chat_message(message.role):
            if message.role == "assistant":
                render_assistant_message(
                    message.content,
                    message.graph_state,
                )
            else:
                st.markdown(message.content)


def handle_user_prompt(store: ChatStore, chat_id: str, prompt: str) -> None:
    user_message = ChatMessage(role="user", content=prompt)
    store.append_message(chat_id, user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Running finance graph...", expanded=False):
            try:
                graph_state = run_finance_graph(
                    prompt,
                    memory=store.get_graph_memory(chat_id),
                    thread_id=chat_id,
                )
            except Exception as error:
                graph_state = build_error_state(prompt, error)

        content = summarize_assistant_response(graph_state)
        render_assistant_message(content, graph_state, stream=True)

    store.append_message(
        chat_id,
        ChatMessage(
            role="assistant",
            content=content,
            workflow=graph_state.get("workflow", "general"),
            graph_state=graph_state,
        ),
    )


def render_guided_query_input() -> str | None:
    st.markdown("### 💡 Try one of these examples")

    category = st.radio(
        "Suggested Queries",
        list(QUERY_TEMPLATES.keys()),
        key="guided_query_category",
        horizontal=True,
    )

    templates = QUERY_TEMPLATES[category]
    columns = st.columns(len(templates))

    for column, template in zip(columns, templates):
        with column:
            if st.button(
                template["label"],
                key=f"template-{category}-{template['label']}",
                use_container_width=True,
            ):
                st.session_state.guided_query_text = template["query"]

    query_text = st.text_area(
        "Edit your query",
        key="guided_query_text",
        placeholder="Choose a suggested query above, edit it, or type your own question here.",
        height=96,
    )

    if st.button("Ask Assistant", type="primary", use_container_width=True):
        prompt = query_text.strip()
        if prompt:
            return prompt
        st.warning("Enter a question or choose one of the examples first.")

    return None


def build_error_state(prompt: str, error: Exception) -> Dict[str, Any]:
    return {
        "query": prompt,
        "workflow": "general",
        "route": {
            "workflow": "general",
        },
        "result": (
            "I could not complete the finance workflow because an external "
            f"data or model request failed: {error}"
        ),
        "memory": [],
    }


def main() -> None:
    initialize_session()
    configure_page()
    st.sidebar.caption(f"Session: {st.session_state['_session_id'][:8]}")

    store = get_store()
    active_chat_id = ensure_active_chat(store)
    active_chat_id = render_sidebar(store, active_chat_id)

    render_history(store, active_chat_id)

    guided_prompt = render_guided_query_input()
    if guided_prompt:
        handle_user_prompt(store, active_chat_id, guided_prompt)
        st.rerun()

    prompt = st.chat_input("Ask about a stock, portfolio, history, or news")
    if prompt:
        handle_user_prompt(store, active_chat_id, prompt)
        st.rerun()


if __name__ == "__main__":
    main()
