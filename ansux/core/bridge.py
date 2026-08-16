"""Thread-safe bridge between HUD text input and the assistant."""

from __future__ import annotations

import threading
from typing import Callable

_lock = threading.Lock()
_handler: Callable[[str], str] | None = None
_confirm_handler: Callable[[str], bool] | None = None
_awaiting_confirmation: str | None = None
_confirm_event = threading.Event()
_confirm_result = False


def register_handlers(
    command_handler: Callable[[str], str],
    confirm_handler: Callable[[str], bool] | None = None,
) -> None:
    global _handler, _confirm_handler
    _handler = command_handler
    _confirm_handler = confirm_handler


def awaiting_confirmation() -> str | None:
    return _awaiting_confirmation


def set_awaiting_confirmation(prompt: str | None) -> None:
    global _awaiting_confirmation
    _awaiting_confirmation = prompt


def wait_for_confirmation(timeout: float) -> bool:
    if _confirm_event.wait(timeout=timeout):
        return _confirm_result
    return False


def signal_confirmation(approved: bool) -> None:
    global _confirm_result
    _confirm_result = approved
    set_awaiting_confirmation(None)
    _confirm_event.set()


def begin_confirmation(prompt: str) -> None:
    _confirm_event.clear()
    set_awaiting_confirmation(prompt)


def submit_text(text: str) -> dict:
    text = text.strip()
    if not text:
        return {"ok": False, "reply": "Please enter a command."}
    if _handler is None:
        return {"ok": False, "reply": "AnshuX is still starting. Try again in a moment."}

    with _lock:
        if _awaiting_confirmation and _confirm_handler:
            approved = _confirm_handler(text)
            signal_confirmation(approved)
            reply = "Confirmed." if approved else "Cancelled."
            return {"ok": True, "reply": reply, "confirmed": approved}

        reply = _handler(text)
        return {"ok": True, "reply": reply or "Done."}
