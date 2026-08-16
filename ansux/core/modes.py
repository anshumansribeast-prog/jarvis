"""Assistant personality modes."""

from __future__ import annotations

from enum import Enum


class AssistantMode(str, Enum):
    ASSISTANT = "assistant"
    SERIOUS = "serious"


_mode = AssistantMode.ASSISTANT


def current_mode() -> AssistantMode:
    return _mode


def set_mode(mode: AssistantMode) -> None:
    global _mode
    _mode = mode


def handle_mode_command(text: str) -> str | None:
    """Return a spoken response if text changes mode, else None."""
    lowered = text.lower().strip()
    if "serious mode" in lowered:
        set_mode(AssistantMode.SERIOUS)
        return "Serious mode activated. I'll keep responses concise and task-focused."
    if "normal mode" in lowered:
        set_mode(AssistantMode.ASSISTANT)
        return "Back to assistant mode. How can I help you?"
    return None


def format_reply(text: str) -> str:
    if current_mode() == AssistantMode.SERIOUS:
        return text.replace("Sir,", "").replace("sir,", "").strip()
    return text
