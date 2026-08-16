"""Shared confirmation flow for dangerous actions."""

from __future__ import annotations

from typing import Callable


class ConfirmationManager:
    def __init__(self, ask_yes_no: Callable[[str], bool]):
        self._ask = ask_yes_no

    def confirm(self, prompt: str) -> bool:
        return self._ask(prompt)

    def confirm_destructive(self, action: str, detail: str = "") -> bool:
        msg = f"Anshu, this will {action}."
        if detail:
            msg += f" {detail}"
        msg += " Proceed?"
        return self._ask(msg)
