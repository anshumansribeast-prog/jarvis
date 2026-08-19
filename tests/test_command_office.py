"""AI Command Office: Commander, agents, real task execution."""

from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import request as urlreq

import pytest

import command_office
import command_office.runtime as runtime
import command_office.store as store
import team
from command_office.orchestrator import (
    approve_task,
    cancel_task,
    commander_chat,
    reassign_task,
    retry_task,
)
from command_office.planner import plan
from command_office.runtime import run_agent


@pytest.fixture
def office_data(tmp_path, monkeypatch):
    data = tmp_path / "data"
    work = tmp_path / "workspace"
    monkeypatch.setattr(command_office, "DATA", data)
    monkeypatch.setattr(command_office, "WORKSPACE", work)
    monkeypatch.setattr(store, "DATA", data)
    monkeypatch.setattr(store, "WORKSPACE", work)
    monkeypatch.setattr(runtime, "WORKSPACE", work)
    monkeypatch.setattr(team, "ROOT", tmp_path)
    store.ensure_dirs()
    return tmp_path


def test_plan_auth_system():
    doc = plan("Build a complete authentication system.")
    agents = [t["agent"] for t in doc["tasks"]]
    assert agents[0] == "commander"
    assert "backend" in agents and "frontend" in agents
    sec = next(t for t in doc["tasks"] if t["title"] == "Review authentication security")
    assert sec["depends"] == [1, 2]


def test_commander_chat_writes_workspace(office_data):
    result = commander_chat("Build a complete authentication system.")
    assert result["created"]
    state = result["state"]
    statuses = {t["id"]: t["status"] for t in state["tasks"]}
    assert "COMPLETED" in statuses.values() or "FAILED" in statuses.values()
    login = office_data / "workspace" / "frontend" / "login.html"
    stub = office_data / "workspace" / "backend" / "auth_stub.py"
    assert login.is_file()
    assert stub.is_file()
    planf = office_data / "workspace" / "commander" / "plan.md"
    assert planf.is_file()
    site = office_data / "workspace" / "projects" / "anshux" / "site" / "index.html"
    progress = office_data / "workspace" / "projects" / "anshux" / "PROGRESS.md"
    assert site.is_file()
    assert progress.is_file()
    assert "frontend" in progress.read_text(encoding="utf-8")
    assert result.get("storage", {}).get("path") == "projects/anshux"
    assert state.get("storage", {}).get("path") == "projects/anshux"
    frontend = next(t for t in state["tasks"] if t["agent"] == "frontend")
    assert frontend["status"] == "COMPLETED"
    assert "login.html" in frontend["output"]
    cmd = next(t for t in state["tasks"] if t["agent"] == "commander")
    assert cmd["status"] == "COMPLETED"
    assert result.get("office")
    assert not result["office"].get("idle")
    # Finished agents must not look unused ("Idle") — Ready/Failed + last_task.
    fe_agent = next(a for a in state["agents"] if a["id"] == "frontend")
    assert fe_agent["status"] in {"Ready", "Failed"}
    assert fe_agent.get("last_task") == frontend["id"]
    assert fe_agent.get("last_result") in {"COMPLETED", "FAILED"}


def test_snapshot_upgrades_legacy_idle_status(office_data):
    """Agents that already finished should not stay Idle forever in the live panel."""
    result = commander_chat("Build a website.")
    agents = store._load("agents.json", [])
    for a in agents:
        a["status"] = "Idle"
        a["current_task"] = None
        a.pop("last_task", None)
        a.pop("last_result", None)
    store.save_agents(agents)
    snap = store.snapshot()
    worked = [a for a in snap["agents"] if a.get("history")]
    assert worked
    assert all(a["status"] in {"Ready", "Failed", "Assigned", "Working"} for a in worked)
    assert result["created"]


def test_named_site_gets_own_storage(office_data):
    result = commander_chat("Build a website called bakery-shop")
    assert result["storage"]["slug"] == "bakery-shop"
    root = office_data / "workspace" / "projects" / "bakery-shop"
    assert (root / "site" / "index.html").is_file()
    assert (root / "PROGRESS.md").is_file()
    assert "Storage" in result["message"]["text"] or "storage" in result["message"]["text"].lower()


def test_infer_project_from_text():
    assert store.infer_project_from_text("Build a website called MyCafe") == "mycafe"
    assert store.infer_project_from_text("just say hi") is None

    first = commander_chat("Check the project.")
    cid = first["conversation_id"]
    second = commander_chat("Show me everyone's progress.", cid)
    assert second["message"]["kind"] == "progress"
    assert "Everyone" in second["message"]["text"]
    assert any(c["id"] == cid for c in second["state"]["conversations"])


def test_assign_testing_agent(office_data):
    result = commander_chat("Ask the testing agent to test it.")
    task = next(t for t in result["created"] if t["agent"] == "testing")
    assert task["agent"] == "testing"
    saved = next(t for t in result["state"]["tasks"] if t["id"] == task["id"])
    assert saved["status"] in {"COMPLETED", "FAILED"}
    assert saved["output"] or saved["errors"]


def test_retry_and_cancel(office_data):
    result = commander_chat("Give the frontend work to Frontend Agent.")
    tid = result["created"][0]["id"]
    cancel_task(tid)
    cancelled = next(t for t in store.snapshot()["tasks"] if t["id"] == tid)
    assert cancelled["status"] == "CANCELLED"
    with pytest.raises(ValueError):
        retry_task(tid)
    again = commander_chat("Build a website.")
    tid2 = again["created"][0]["id"]
    retry_task(tid2)
    row = next(t for t in store.snapshot()["tasks"] if t["id"] == tid2)
    assert row["status"] in {"COMPLETED", "FAILED", "QUEUED", "RUNNING"}


def test_reassign(office_data):
    result = commander_chat("Give the frontend work to Frontend Agent.")
    tid = result["created"][0]["id"]
    state = reassign_task(tid, "backend")
    row = next(t for t in state["tasks"] if t["id"] == tid)
    assert row["agent"] == "backend"


def test_destructive_needs_approval(office_data):
    result = commander_chat("rm -rf the project and rebuild")
    created = result["created"]
    assert created
    assert all(t["status"] == "NEEDS_REVIEW" for t in created)
    assert result["message"].get("needs_approval")
    tid = created[0]["id"]
    approve_task(tid)
    row = next(t for t in store.snapshot()["tasks"] if t["id"] == tid)
    assert row["status"] in {"COMPLETED", "FAILED", "QUEUED", "RUNNING", "WAITING"}


def test_runtime_unknown_agent_fails():
    ok, out = run_agent("nope", {"title": "x"})
    assert ok is False
    assert "unknown" in out


def test_command_office_http(office_data, monkeypatch):
    src = Path(__file__).resolve().parents[1] / "office" / "index.html"
    monkeypatch.setattr(team, "ROOT", office_data)
    office = office_data / "office"
    office.mkdir()
    office.joinpath("index.html").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), team.OfficeHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    port = httpd.server_address[1]
    try:
        home = urlreq.urlopen(f"http://127.0.0.1:{port}/", timeout=5).read().decode("utf-8")
        assert "OpenCode chat panel" in home
        assert "COMMANDER" in home
        assert "Assign a task" in home
        page = urlreq.urlopen(f"http://127.0.0.1:{port}/command/", timeout=5).read().decode("utf-8")
        assert "AI Command Office" in page
        assert "OpenCode chat panel" in page
        assert "sk-" not in page
        assert "api_key" not in page.lower()
        req = urlreq.Request(
            f"http://127.0.0.1:{port}/api/command/chat",
            data=json.dumps({"text": "Build a website."}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        chat = json.loads(urlreq.urlopen(req, timeout=60).read().decode("utf-8"))
        assert chat["ok"] is True
        assert chat["created"]
        state = json.loads(urlreq.urlopen(f"http://127.0.0.1:{port}/api/command", timeout=5).read().decode())
        assert state["commander"]["name"] == "COMMANDER"
        assert any(a["name"] == "Frontend Agent" for a in state["agents"])
        conv = urlreq.Request(
            f"http://127.0.0.1:{port}/api/command/conversation",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        newc = json.loads(urlreq.urlopen(conv, timeout=5).read().decode())
        assert newc["conversation"]["id"]
        files = state.get("files") or chat["state"].get("files")
        if files:
            path = files[0]["path"]
            got = json.loads(
                urlreq.urlopen(
                    f"http://127.0.0.1:{port}/api/command/file?path={path}", timeout=5
                ).read().decode()
            )
            assert got["ok"] is True
            assert got["text"]
        tid = chat["created"][0]["id"]
        stop = urlreq.Request(
            f"http://127.0.0.1:{port}/api/command/cancel",
            data=json.dumps({"id": tid}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        stopped = json.loads(urlreq.urlopen(stop, timeout=5).read().decode())
        assert any(t["id"] == tid and t["status"] == "CANCELLED" for t in stopped["state"]["tasks"])
    finally:
        httpd.shutdown()


def test_commander_greets_anshux(office_data):
    from command_office.store import add_conversation

    row = add_conversation()
    assert "AnshuX" in row["messages"][0]["text"]
    result = commander_chat("Build a website.")
    assert "AnshuX" in result["message"]["text"]
    assert "AnshuX" in result["follow"]["text"]
