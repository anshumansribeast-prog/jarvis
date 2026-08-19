from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from command_office import AGENTS, DATA, MODEL, WORKSPACE

_lock = threading.RLock()


def _now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "frontend").mkdir(exist_ok=True)
    (WORKSPACE / "backend").mkdir(exist_ok=True)


def _path(name: str) -> Path:
    ensure_dirs()
    return DATA / name


def _load(name: str, default):
    path = _path(name)
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _save(name: str, data) -> None:
    _path(name).write_text(json.dumps(data, indent=2), encoding="utf-8")


def snapshot() -> dict:
    with _lock:
        agents = _load("agents.json", [])
        if not agents:
            agents = [
                {
                    **a,
                    "status": "Idle",
                    "current_task": None,
                    "history": [],
                    "logs": [],
                }
                for a in AGENTS
            ]
            _save("agents.json", agents)
        convos = _load("conversations.json", [])
        tasks = _load("tasks.json", [])
        activity = _load("activity.json", [])
        settings = _load("settings.json", {"model": MODEL, "project": "anshux"})
        settings["model"] = MODEL
        return {
            "agents": agents,
            "conversations": convos,
            "tasks": tasks,
            "activity": activity[-80:],
            "settings": settings,
            "files": list_workspace_files(),
            "now": _now(),
            "commander": {"name": "COMMANDER", "status": "Online", "model": MODEL},
        }


def log_activity(text: str) -> None:
    with _lock:
        rows = _load("activity.json", [])
        rows.append({"t": _now(), "text": text})
        _save("activity.json", rows[-200:])


def next_task_id() -> int:
    tasks = _load("tasks.json", [])
    nums = [int(t["id"]) for t in tasks if str(t.get("id", "")).isdigit()]
    return max(nums, default=103) + 1


def add_conversation() -> dict:
    with _lock:
        rows = _load("conversations.json", [])
        cid = f"c{len(rows) + 1:04d}"
        row = {"id": cid, "title": "New chat", "created": _now(), "messages": []}
        rows.append(row)
        _save("conversations.json", rows)
        return row


def get_conversation(cid: str) -> dict | None:
    for row in _load("conversations.json", []):
        if row.get("id") == cid:
            return row
    return None


def append_message(cid: str, msg: dict) -> dict:
    with _lock:
        rows = _load("conversations.json", [])
        found = None
        for row in rows:
            if row.get("id") == cid:
                row.setdefault("messages", []).append(msg)
                if msg.get("role") == "user" and row.get("title") == "New chat":
                    row["title"] = (msg.get("text") or "Chat")[:48]
                found = row
                break
        if found is None:
            found = {"id": cid, "title": "New chat", "created": _now(), "messages": [msg]}
            rows.append(found)
        _save("conversations.json", rows)
        return found


def save_tasks(tasks: list) -> None:
    _save("tasks.json", tasks)


def save_agents(agents: list) -> None:
    _save("agents.json", agents)


def set_agent(agent_id: str, **fields) -> dict | None:
    with _lock:
        agents = _load("agents.json", [])
        hit = None
        for a in agents:
            if a["id"] == agent_id:
                a.update(fields)
                logs = a.setdefault("logs", [])
                if fields.get("log"):
                    logs.append({"t": _now(), "text": fields.pop("log")})
                    a["logs"] = logs[-40:]
                hit = a
        _save("agents.json", agents)
        return hit


def update_settings(patch: dict) -> dict:
    from command_office import MODEL

    with _lock:
        settings = _load("settings.json", {"model": MODEL, "project": "anshux"})
        # Model is server env COMMANDER_MODEL only — never accept keys from the browser.
        settings["model"] = MODEL
        if "project" in patch:
            settings["project"] = str(patch["project"])[:40]
        _save("settings.json", settings)
        return settings


def list_workspace_files() -> list[dict]:
    ensure_dirs()
    rows = []
    for path in sorted(WORKSPACE.rglob("*")):
        if path.is_file() and path.name != ".gitkeep":
            rel = str(path.relative_to(WORKSPACE)).replace("\\", "/")
            rows.append({"path": rel, "bytes": path.stat().st_size})
    return rows


def read_workspace_file(rel: str) -> str:
    ensure_dirs()
    clean = rel.replace("\\", "/").lstrip("/")
    if ".." in clean.split("/"):
        raise ValueError("invalid path")
    path = (WORKSPACE / clean).resolve()
    if WORKSPACE.resolve() not in path.parents and path != WORKSPACE.resolve():
        raise ValueError("outside workspace")
    if not path.is_file():
        raise FileNotFoundError(clean)
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:20000]
