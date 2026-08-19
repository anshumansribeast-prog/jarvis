from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from command_office import AGENTS, DATA, MODEL, WORKSPACE

_lock = threading.RLock()


def _now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(name: str) -> str:
    raw = (name or "site").strip().lower()
    slug = re.sub(r"[^a-z0-9._-]+", "-", raw).strip("-._")
    return (slug or "site")[:40]


def ensure_dirs() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "frontend").mkdir(exist_ok=True)
    (WORKSPACE / "backend").mkdir(exist_ok=True)
    (WORKSPACE / "commander").mkdir(exist_ok=True)
    (WORKSPACE / "projects").mkdir(exist_ok=True)


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
        have = {a.get("id") for a in agents}
        changed = False
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
            changed = True
        else:
            for spec in AGENTS:
                if spec["id"] not in have:
                    agents.insert(0 if spec["id"] == "commander" else len(agents), {
                        **spec,
                        "status": "Idle",
                        "current_task": None,
                        "history": [],
                        "logs": [],
                    })
                    have.add(spec["id"])
                    changed = True
        # Older runs flipped every agent to Idle after work. If they have history,
        # surface Ready/Failed from the last task so the live panel is honest.
        tasks_preview = _load("tasks.json", [])
        by_id = {int(t["id"]): t for t in tasks_preview if str(t.get("id", "")).isdigit()}
        for a in agents:
            if a.get("status") not in {None, "Idle"}:
                continue
            hist = a.get("history") or []
            if not hist:
                continue
            last_id = hist[-1]
            try:
                last_id = int(last_id)
            except (TypeError, ValueError):
                continue
            row = by_id.get(last_id)
            if not row:
                a["status"] = "Ready"
                a["last_task"] = last_id
                changed = True
                continue
            st = row.get("status")
            if st == "COMPLETED":
                a["status"] = "Ready"
                a["last_task"] = last_id
                a["last_result"] = "COMPLETED"
                changed = True
            elif st == "FAILED":
                a["status"] = "Failed"
                a["last_task"] = last_id
                a["last_result"] = "FAILED"
                changed = True
            elif st in {"QUEUED", "WAITING", "ASSIGNED", "NEEDS_REVIEW", "RUNNING"}:
                a["status"] = "Working" if st == "RUNNING" else "Assigned"
                a["current_task"] = last_id
                changed = True
        if changed:
            _save("agents.json", agents)
        convos = _load("conversations.json", [])
        tasks = tasks_preview
        activity = _load("activity.json", [])
        settings = _load("settings.json", {"model": MODEL, "project": "anshux"})
        settings["model"] = MODEL
        storage = project_snapshot()
        return {
            "agents": agents,
            "conversations": convos,
            "tasks": tasks,
            "activity": activity[-80:],
            "settings": settings,
            "files": list_workspace_files(),
            "storage": storage,
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
    from command_office import greet

    with _lock:
        rows = _load("conversations.json", [])
        cid = f"c{len(rows) + 1:04d}"
        row = {
            "id": cid,
            "title": "New chat",
            "created": _now(),
            "messages": [
                {
                    "role": "commander",
                    "kind": "greet",
                    "text": greet(
                        "COMMANDER here. OpenCode and I are one lead. "
                        "Tell us what to build — everyone greets you as AnshuX and gets to work."
                    ),
                    "t": _now(),
                }
            ],
        }
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
            settings["project"] = slugify(str(patch["project"]))
        _save("settings.json", settings)
        return settings


def project_slug() -> str:
    settings = _load("settings.json", {"model": MODEL, "project": "anshux"})
    return slugify(str(settings.get("project") or "anshux"))


def infer_project_from_text(text: str) -> str | None:
    """Pull a site/project name from chat when the user names one."""
    patterns = [
        r"(?:site|website|project|app)\s+(?:called|named)\s+[\"']?([A-Za-z0-9][\w.-]{0,39})",
        r"(?:build|create|make)\s+(?:a\s+)?(?:site|website|project)\s+(?:for|called|named)\s+[\"']?([A-Za-z0-9][\w.-]{0,39})",
        r"(?:called|named)\s+[\"']([A-Za-z0-9][\w.-]{0,39})[\"']",
    ]
    for pat in patterns:
        m = re.search(pat, text or "", re.I)
        if m:
            return slugify(m.group(1))
    return None


def project_dir(slug: str | None = None) -> Path:
    ensure_dirs()
    slug = slugify(slug or project_slug())
    root = WORKSPACE / "projects" / slug
    (root / "site").mkdir(parents=True, exist_ok=True)
    (root / "backend").mkdir(parents=True, exist_ok=True)
    (root / "notes").mkdir(parents=True, exist_ok=True)
    return root


def ensure_project(goal: str = "", slug: str | None = None) -> dict:
    """Shared storage folder where every agent saves progress for one site."""
    with _lock:
        if slug:
            update_settings({"project": slug})
        name = project_slug()
        root = project_dir(name)
        readme = root / "README.md"
        progress = root / "PROGRESS.md"
        if not readme.is_file():
            readme.write_text(
                f"# {name}\n\nShared storage for this site.\n"
                f"Everyone (COMMANDER + agents + desks) writes here.\n\n"
                f"- `site/` — pages the Frontend Agent builds\n"
                f"- `backend/` — API stubs from Backend Agent\n"
                f"- `notes/` — per-agent notes\n"
                f"- `PROGRESS.md` — running log of who saved what\n",
                encoding="utf-8",
            )
        if not progress.is_file():
            progress.write_text(
                f"# Progress — {name}\n\nStarted {_now()}\n\n",
                encoding="utf-8",
            )
        if goal.strip():
            goal_path = root / "GOAL.md"
            old = goal_path.read_text(encoding="utf-8") if goal_path.is_file() else ""
            goal_path.write_text(
                f"# Goal\n\n{goal.strip()}\n\nUpdated {_now()}\n",
                encoding="utf-8",
            )
            if goal.strip() not in old:
                append_progress(name, "commander", f"Goal set: {goal.strip()[:200]}")
        rel = f"projects/{name}"
        return {
            "slug": name,
            "path": rel,
            "abs": str(root),
            "progress": f"{rel}/PROGRESS.md",
            "site": f"{rel}/site",
            "files": [
                {
                    "path": str(p.relative_to(WORKSPACE)).replace("\\", "/"),
                    "bytes": p.stat().st_size,
                }
                for p in sorted(root.rglob("*"))
                if p.is_file()
            ],
        }


def append_progress(slug: str, who: str, text: str) -> str:
    root = project_dir(slug)
    progress = root / "PROGRESS.md"
    if not progress.is_file():
        progress.write_text(f"# Progress — {slugify(slug)}\n\n", encoding="utf-8")
    line = f"- {_now()} · **{who}**: {text.strip()}\n"
    with progress.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return f"projects/{slugify(slug)}/PROGRESS.md"


def list_projects() -> list[dict]:
    ensure_dirs()
    root = WORKSPACE / "projects"
    rows = []
    active = project_slug()
    if not root.is_dir():
        return rows
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        files = [p for p in path.rglob("*") if p.is_file()]
        prog = root / path.name / "PROGRESS.md"
        preview = ""
        if prog.is_file():
            preview = prog.read_text(encoding="utf-8", errors="replace")[-1200:]
        rows.append({
            "slug": path.name,
            "path": f"projects/{path.name}",
            "active": path.name == active,
            "files": len(files),
            "progress_tail": preview,
        })
    return rows


def project_snapshot() -> dict:
    info = ensure_project()
    progress_rel = info["progress"]
    try:
        progress_text = read_workspace_file(progress_rel)
    except FileNotFoundError:
        progress_text = ""
    return {
        **info,
        "projects": list_projects(),
        "progress_text": progress_text[-4000:],
    }


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
