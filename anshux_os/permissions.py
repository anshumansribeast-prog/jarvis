"""Permission gate for OS actions.

Destructive actions are never executed directly by the AI layer. They must
first be represented as a pending action and explicitly approved by the
local user/session.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Risk(str, Enum):
    READ = "read"
    WRITE = "write"
    DANGEROUS = "dangerous"


@dataclass(frozen=True)
class Action:
    name: str
    risk: Risk
    description: str
    args: dict[str, Any]


class PermissionManager:
    def __init__(self) -> None:
        self._pending: dict[str, Action] = {}

    def request(self, action_id: str, action: Action) -> None:
        self._pending[action_id] = action

    def approve(self, action_id: str) -> Action:
        try:
            return self._pending.pop(action_id)
        except KeyError as exc:
            raise ValueError("Unknown or expired action") from exc

    def deny(self, action_id: str) -> None:
        self._pending.pop(action_id, None)

    def pending(self) -> dict[str, Action]:
        return dict(self._pending)
