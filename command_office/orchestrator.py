from __future__ import annotations

import threading
from datetime import datetime, timezone

from command_office.planner import is_destructive, plan
from command_office.runtime import run_agent
from command_office.store import (
    _load,
    _lock,
    _now,
    _save,
    add_conversation,
    append_message,
    get_conversation,
    log_activity,
    next_task_id,
    save_agents,
    save_tasks,
    snapshot,
)


def _stamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _start_open_code_floor(text: str) -> dict:
    """Talking to Commander starts OpenCode and every desk."""
    try:
        import team as team_mod

        team_mod.assign_task("everyone", text, start_command=False)
        team_mod.record_unified_lead(
            text,
            "OpenCode and COMMANDER are one lead. Every desk is started. Commander is doing a slice of the work too.",
        )
        return team_mod.collect_office_state(network=False)
    except Exception:
        return {}


def _tasks() -> list:
    return _load("tasks.json", [])


def _agents() -> list:
    snap = snapshot()
    return snap["agents"]


def create_tasks_from_plan(plan_doc: dict) -> list[dict]:
    created = []
    with _lock:
        tasks = _load("tasks.json", [])
        agents = _load("agents.json", snapshot()["agents"])
        id_map: list[int] = []
        base = next_task_id() if not tasks else max(int(t["id"]) for t in tasks if str(t["id"]).isdigit()) + 1
        n = base
        for spec in plan_doc.get("tasks") or []:
            tid = n
            n += 1
            id_map.append(tid)
            depends = [id_map[i] for i in spec.get("depends") or [] if i < len(id_map)]
            destructive = plan_doc.get("destructive") or is_destructive(spec.get("description") or "")
            status = "NEEDS_REVIEW" if destructive else ("WAITING" if depends else "QUEUED")
            row = {
                "id": tid,
                "title": spec["title"],
                "description": spec.get("description") or spec["title"],
                "priority": spec.get("priority") or "normal",
                "agent": spec["agent"],
                "status": status,
                "progress": 0,
                "created": _stamp(),
                "started": None,
                "completed": None,
                "depends": depends,
                "output": "",
                "errors": "",
            }
            tasks.append(row)
            created.append(row)
            for a in agents:
                if a["id"] == spec["agent"]:
                    a["history"] = (a.get("history") or [])[-20:] + [tid]
            log_activity(f"Task #{tid} {status} → {spec['agent']}: {spec['title']}")
        _save("tasks.json", tasks)
        save_agents(agents)
    return created


def _deps_ok(task: dict, tasks: list) -> bool:
    by_id = {int(t["id"]): t for t in tasks}
    for dep in task.get("depends") or []:
        other = by_id.get(int(dep))
        if not other or other.get("status") != "COMPLETED":
            return False
    return True


def process_due_tasks(limit: int = 8) -> list[dict]:
    """Run queued work. Real tools only — pytest, file writes, git status."""
    done = []
    for _ in range(limit):
        with _lock:
            tasks = _load("tasks.json", [])
            agents = _load("agents.json", snapshot()["agents"])
            pick = None
            for t in tasks:
                if t.get("status") in {"QUEUED", "ASSIGNED"} and _deps_ok(t, tasks):
                    pick = t
                    break
                if t.get("status") == "WAITING" and _deps_ok(t, tasks):
                    t["status"] = "QUEUED"
                    pick = t
                    break
            if pick is None:
                _save("tasks.json", tasks)
                break
            pick["status"] = "RUNNING"
            pick["started"] = pick.get("started") or _stamp()
            pick["progress"] = 10
            agent_id = pick["agent"]
            for a in agents:
                if a["id"] == agent_id:
                    a["status"] = "Working"
                    a["current_task"] = pick["id"]
                    a.setdefault("logs", []).append({"t": _stamp(), "text": f"start #{pick['id']}"})
            _save("tasks.json", tasks)
            save_agents(agents)
            task_copy = dict(pick)
        ok, output = run_agent(task_copy["agent"], task_copy)
        with _lock:
            tasks = _load("tasks.json", [])
            agents = _load("agents.json", snapshot()["agents"])
            for t in tasks:
                if int(t["id"]) == int(task_copy["id"]):
                    t["progress"] = 100 if ok else 100
                    t["status"] = "COMPLETED" if ok else "FAILED"
                    t["completed"] = _stamp()
                    t["output"] = output if ok else ""
                    t["errors"] = "" if ok else output
                    done.append(dict(t))
                    log_activity(f"Task #{t['id']} {t['status']}")
            for a in agents:
                if a["id"] == task_copy["agent"]:
                    a["status"] = "Idle"
                    a["current_task"] = None
                    a.setdefault("logs", []).append({"t": _stamp(), "text": f"end #{task_copy['id']} {ok}"})
                    a["logs"] = a["logs"][-40:]
            _save("tasks.json", tasks)
            save_agents(agents)
    return done


def commander_chat(text: str, conversation_id: str | None = None) -> dict:
    snap = snapshot()
    if not conversation_id:
        conversation_id = add_conversation()["id"]
    append_message(conversation_id, {"role": "user", "text": text, "t": _stamp(), "kind": "text"})
    planned = plan(text)
    office = {}
    if planned["kind"] != "status":
        office = _start_open_code_floor(text)
    if planned["kind"] == "status":
        tasks = snapshot()["tasks"]
        agents = snapshot()["agents"]
        lines = ["## Everyone's progress"]
        for a in agents:
            lines.append(f"- {a['name']}: {a.get('status') or 'Idle'} task={a.get('current_task')}")
        for t in tasks[-12:]:
            lines.append(f"- #{t['id']} {t['title']} — {t['status']} ({t['agent']})")
        msg = {
            "role": "commander",
            "kind": "progress",
            "text": "\n".join(lines),
            "t": _stamp(),
        }
        append_message(conversation_id, msg)
        return {"conversation_id": conversation_id, "message": msg, "state": snapshot(), "office": office}

    created = create_tasks_from_plan(planned)
    if created and not planned.get("destructive"):
        process_due_tasks(limit=max(12, len(created) + 4))
    state = snapshot()
    ids = {int(t["id"]) for t in created}
    created = [t for t in state["tasks"] if int(t["id"]) in ids]
    cmd_row = next((t for t in created if t.get("agent") == "commander"), None)
    cmd_note = ""
    if cmd_row:
        cmd_note = f" COMMANDER also ran: {cmd_row.get('output') or cmd_row.get('errors') or cmd_row.get('status')}."
    msg = {
        "role": "commander",
        "kind": "plan",
        "text": planned["summary"] + cmd_note,
        "tasks": created,
        "t": _stamp(),
        "needs_approval": planned.get("destructive", False),
    }
    append_message(conversation_id, msg)
    follow = {
        "role": "commander",
        "kind": "progress",
        "text": "OpenCode + COMMANDER started every desk. Commander did a slice of the work.",
        "t": _stamp(),
    }
    append_message(conversation_id, follow)
    return {
        "conversation_id": conversation_id,
        "message": msg,
        "follow": follow,
        "state": state,
        "created": created,
        "office": office,
    }


def retry_task(tid: int) -> dict:
    with _lock:
        tasks = _load("tasks.json", [])
        for t in tasks:
            if int(t["id"]) == int(tid):
                if t.get("status") == "CANCELLED":
                    raise ValueError("cancelled")
                t["status"] = "QUEUED"
                t["errors"] = ""
                t["progress"] = 0
                t["completed"] = None
        _save("tasks.json", tasks)
    process_due_tasks(limit=3)
    return snapshot()


def cancel_task(tid: int) -> dict:
    with _lock:
        tasks = _load("tasks.json", [])
        for t in tasks:
            if int(t["id"]) == int(tid):
                t["status"] = "CANCELLED"
                t["completed"] = _stamp()
        _save("tasks.json", tasks)
    log_activity(f"Task #{tid} CANCELLED")
    return snapshot()


def reassign_task(tid: int, agent: str) -> dict:
    ids = {a["id"] for a in snapshot()["agents"]}
    if agent not in ids:
        raise ValueError("unknown agent")
    with _lock:
        tasks = _load("tasks.json", [])
        for t in tasks:
            if int(t["id"]) == int(tid):
                t["agent"] = agent
                if t.get("status") in {"FAILED", "NEEDS_REVIEW"}:
                    t["status"] = "QUEUED"
        _save("tasks.json", tasks)
    log_activity(f"Task #{tid} reassigned to {agent}")
    process_due_tasks(limit=2)
    return snapshot()


def approve_task(tid: int) -> dict:
    with _lock:
        tasks = _load("tasks.json", [])
        for t in tasks:
            if int(t["id"]) == int(tid) and t.get("status") == "NEEDS_REVIEW":
                t["status"] = "QUEUED"
        _save("tasks.json", tasks)
    process_due_tasks(limit=3)
    return snapshot()


_worker_started = False


def start_worker() -> None:
    global _worker_started
    if _worker_started:
        return
    _worker_started = True

    def loop():
        import time
        while True:
            try:
                process_due_tasks(limit=2)
            except Exception:
                pass
            time.sleep(1.5)

    threading.Thread(target=loop, daemon=True).start()
