"""Short-term conversation and task context."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversationContext:
    last_project: str | None = None
    last_app: str | None = None
    last_url: str | None = None
    last_command: str | None = None
    history: deque[dict[str, str]] = field(default_factory=lambda: deque(maxlen=12))

    def record(self, user_text: str, assistant_reply: str | None = None) -> None:
        self.last_command = user_text
        entry: dict[str, str] = {"user": user_text}
        if assistant_reply:
            entry["assistant"] = assistant_reply
        self.history.append(entry)

    def set_project(self, name: str) -> None:
        self.last_project = name.lower().strip()

    def set_app(self, name: str) -> None:
        self.last_app = name.lower().strip()

    def resolve_project_reference(self, text: str) -> str | None:
        lowered = text.lower()
        if "my project" in lowered or "the project" in lowered:
            return self.last_project
        if "astronomy" in lowered and self.last_project and "astronomy" in self.last_project:
            return self.last_project
        return None

    def recent_summary(self) -> list[dict[str, str]]:
        return list(self.history)


_context = ConversationContext()


def get_context() -> ConversationContext:
    return _context
