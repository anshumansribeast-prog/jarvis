"""Permission-aware bridge from OS actions to existing Jarvis controllers."""

from __future__ import annotations

from typing import Any, Callable

import app_controller
import system_controller


class ActionExecutor:
    """Execute only named, registered operations; never arbitrary shell text."""

    def __init__(self) -> None:
        self._safe: dict[str, Callable[..., Any]] = {
            "volume_up": system_controller.volume_up,
            "volume_down": system_controller.volume_down,
            "mute": system_controller.mute,
            "screenshot": system_controller.take_screenshot,
            "lock": system_controller.lock,
            "open_app": app_controller.launch_app,
            "close_app": app_controller.close_app,
        }
        self._dangerous = {"shutdown": system_controller.shutdown, "restart": system_controller.restart}

    def execute(self, name: str, args: dict[str, Any], approved: bool = False) -> Any:
        if name in self._safe:
            return self._safe[name](**args)
        if name in self._dangerous:
            if not approved:
                raise PermissionError("Dangerous OS action requires explicit approval")
            return self._dangerous[name](**args)
        raise ValueError(f"Unsupported OS action: {name}")
