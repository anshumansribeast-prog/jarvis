"""Small persistent memory store for the AnshuX OS control plane."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, path: str | Path = "data/anshux_memory.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        if not self.path.exists():
            self._write({"facts": {}, "events": []})

    def _read(self) -> dict[str, Any]:
        with self._lock:
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return {"facts": {}, "events": []}

    def _write(self, data: dict[str, Any]) -> None:
        with self._lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.path)

    def remember(self, key: str, value: str) -> None:
        data = self._read()
        data.setdefault("facts", {})[key] = value
        self._write(data)

    def recall(self, key: str) -> str | None:
        return self._read().get("facts", {}).get(key)

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._read().get("events", [])[-limit:]

    def event(self, kind: str, payload: dict[str, Any]) -> None:
        data = self._read()
        data.setdefault("events", []).append({"kind": kind, "payload": payload})
        data["events"] = data["events"][-500:]
        self._write(data)
