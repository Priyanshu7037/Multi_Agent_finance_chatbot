from __future__ import annotations

import pickle
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


Role = Literal["user", "assistant"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ChatMessage:
    role: Role
    content: str
    created_at: str = field(default_factory=utc_now)
    workflow: Optional[str] = None
    graph_state: Optional[Dict[str, Any]] = None


@dataclass
class ChatThread:
    id: str
    title: str
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    messages: List[ChatMessage] = field(default_factory=list)


class ChatStore:
    """Small local persistence layer for Streamlit chat sessions.

    When path is None, the store remains fully in-memory and never reads or
    writes to disk. This ensures each visitor only sees their own session
    chat history when the app is served by Streamlit.
    """

    def __init__(self, path: Path | str | None = "storage/chat_store.pkl") -> None:
        if path is None:
            self.path = None
            self._threads: Dict[str, ChatThread] = {}
            return

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._threads = self._load()

    def list_threads(self) -> List[ChatThread]:
        return sorted(
            self._threads.values(),
            key=lambda thread: thread.updated_at,
            reverse=True,
        )

    def create_thread(self) -> ChatThread:
        thread = ChatThread(
            id=str(uuid.uuid4()),
            title="New chat",
        )
        self._threads[thread.id] = thread
        self._save()
        return thread

    def get_thread(self, thread_id: str) -> ChatThread:
        if thread_id not in self._threads:
            return self.create_thread()
        return self._threads[thread_id]

    def delete_thread(self, thread_id: str) -> None:
        self._threads.pop(thread_id, None)
        self._save()

    def append_message(self, thread_id: str, message: ChatMessage) -> None:
        thread = self.get_thread(thread_id)
        thread.messages.append(message)
        thread.updated_at = utc_now()

        if thread.title == "New chat" and message.role == "user":
            thread.title = self._title_from_message(message.content)

        self._save()

    def get_graph_memory(self, thread_id: str) -> List[Dict[str, Any]]:
        thread = self.get_thread(thread_id)

        for message in reversed(thread.messages):
            state = message.graph_state or {}
            memory = state.get("memory")
            if isinstance(memory, list):
                return memory

        return []

    def _load(self) -> Dict[str, ChatThread]:
        if self.path is None:
            return {}

        if not self.path.exists():
            return {}

        try:
            with self.path.open("rb") as file:
                data = pickle.load(file)
        except (OSError, pickle.PickleError, EOFError):
            return {}

        if isinstance(data, dict):
            return data

        return {}

    def _save(self) -> None:
        if self.path is None:
            return

        temp_path = self.path.with_suffix(".tmp")
        with temp_path.open("wb") as file:
            pickle.dump(self._threads, file)
        temp_path.replace(self.path)

    @staticmethod
    def _title_from_message(content: str) -> str:
        cleaned = " ".join(content.split())
        if len(cleaned) <= 42:
            return cleaned or "New chat"
        return f"{cleaned[:39]}..."
