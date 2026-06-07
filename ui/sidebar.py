from __future__ import annotations

from typing import Optional

import streamlit as st

from memory import ChatStore

st.sidebar.write(
    "Session ID:",
    st.session_state.get("_session_id")
)
def render_sidebar(store: ChatStore, active_chat_id: Optional[str]) -> str:
    st.sidebar.title("Finance Assistant")

    if st.sidebar.button("Create New Chat", use_container_width=True):
        active_chat_id = store.create_thread().id
        st.session_state.active_chat_id = active_chat_id
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("Previous chats")

    threads = store.list_threads()
    if not threads:
        active_chat_id = store.create_thread().id
        st.session_state.active_chat_id = active_chat_id
        st.rerun()

    for thread in threads:
        selected = thread.id == active_chat_id
        label = f"* {thread.title}" if selected else thread.title

        if st.sidebar.button(
            label,
            key=f"switch-{thread.id}",
            use_container_width=True,
        ):
            st.session_state.active_chat_id = thread.id
            st.rerun()

    st.sidebar.divider()

    if active_chat_id and st.sidebar.button(
        "Delete Current Chat",
        type="secondary",
        use_container_width=True,
    ):
        store.delete_thread(active_chat_id)
        next_thread = store.list_threads()
        if next_thread:
            st.session_state.active_chat_id = next_thread[0].id
        else:
            st.session_state.active_chat_id = store.create_thread().id
        st.rerun()

    return st.session_state.active_chat_id
