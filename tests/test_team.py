"""ANSHUX command hub."""

import json
import shutil
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import request as urlreq

import team


def test_help_exits_zero():
    assert team.main(["help"]) == 0


def test_resolve_check_the_sites():
    assert team.resolve_command("check the sites") == "sites"
    assert team.resolve_command("2") == "sites"
    assert team.resolve_command("ping sites") == "sites"


def test_cli_check_the_sites(capsys, monkeypatch):
    monkeypatch.setattr(team, "http_status", lambda url, timeout=4.0: "200")
    assert team.main(["check", "the", "sites"]) == 0
    out = capsys.readouterr().out
    assert "Live sites" in out
    assert "Semicolon" in out


def test_status_runs(capsys):
    assert team.main(["status"]) == 0
    out = capsys.readouterr().out
    assert "ANSHUX board" in out
    assert "OpenCode" in out
    assert "Ada" in out


def test_office_command():
    assert team.resolve_command("office") == "office"
    assert team.resolve_command("see the team") == "office"


def test_office_snapshot(monkeypatch, tmp_path):
    monkeypatch.setattr(team, "ROOT", tmp_path)
    monkeypatch.setattr(team, "http_status", lambda url, timeout=4.0: "200")
    monkeypatch.setattr(team, "_gh_prs", lambda repo: [])
    monkeypatch.setattr(team, "which", lambda cmd: None)
    monkeypatch.setattr(team, "tcp_open", lambda *a, **k: False)
    path = team.write_office_state()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["architect"] == "OpenCode"
    assert data["inspector"] == "OpenCode"
    assert any(d["role"].lower().startswith("architect") for d in data["desks"])
    assert "cline" in data["members"]
    assert data["loop"]


def test_assign_task(monkeypatch, tmp_path):
    monkeypatch.setattr(team, "ROOT", tmp_path)
    monkeypatch.setattr(team, "http_status", lambda url, timeout=4.0: "200")
    monkeypatch.setattr(team, "_gh_prs", lambda repo: [])
    monkeypatch.setattr(team, "which", lambda cmd: None)
    monkeypatch.setattr(team, "tcp_open", lambda *a, **k: False)
    assert team.main(["assign", "aider", "fix", "Ada", "API"]) == 0
    data = team.collect_office_state()
    assert "Ada API" in data["assignments"]["aider"]
    desk = next(d for d in data["desks"] if d["id"] == "aider")
    assert desk.get("assigned") is True
    for seat in team.DESK_IDS:
        assert data["assignments"].get(seat)
        member = next(d for d in data["desks"] if d["id"] == seat)
        assert member["status"] == "working"


def test_assign_everyone(monkeypatch, tmp_path):
    monkeypatch.setattr(team, "ROOT", tmp_path)
    monkeypatch.setattr(team, "http_status", lambda url, timeout=4.0: "200")
    monkeypatch.setattr(team, "_gh_prs", lambda repo: [])
    monkeypatch.setattr(team, "which", lambda cmd: None)
    monkeypatch.setattr(team, "tcp_open", lambda *a, **k: False)
    team.assign_task("everyone", "Ship Semicolon Ada restore")
    data = team.collect_office_state(network=False)
    assert not data["idle"]
    for seat in team.DESK_IDS:
        assert "Ship Semicolon Ada restore" in data["assignments"][seat]
        assert next(d for d in data["desks"] if d["id"] == seat)["status"] == "working"
    assert data["briefing"]["goal"] == "Ship Semicolon Ada restore"
    assert data["briefing"]["seat"] == "everyone"


def test_architect_chat_queues_without_opencode(monkeypatch, tmp_path):
    monkeypatch.setattr(team, "ROOT", tmp_path)
    monkeypatch.setattr(team, "which", lambda cmd: None)
    result = team.architect_chat("inspect both sites")
    assert "queued" in result["reply"].lower() or "PATH" in result["reply"]
    assert result["chat"][-1]["who"] == "opencode"


def test_office_site_serves_chat_panel(monkeypatch, tmp_path):
    src = Path(__file__).resolve().parents[1] / "office" / "index.html"
    monkeypatch.setattr(team, "ROOT", tmp_path)
    monkeypatch.setattr(team, "http_status", lambda url, timeout=4.0: "200")
    monkeypatch.setattr(team, "_gh_prs", lambda repo: [])
    monkeypatch.setattr(team, "which", lambda cmd: None)
    monkeypatch.setattr(team, "tcp_open", lambda *a, **k: False)
    office = tmp_path / "office"
    office.mkdir()
    shutil.copy(src, office / "index.html")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), team.OfficeHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    port = httpd.server_address[1]
    try:
        home = urlreq.urlopen(f"http://127.0.0.1:{port}/", timeout=5).read().decode("utf-8")
        assert "OpenCode chat panel" in home
        assert "Assign like a real office" in home or "Assign a task" in home
        assert "Everyone (whole floor)" in home or "Everyone (no idle desks)" in home
        assert "COMMANDER" in home
        assert "Office floor" in home
        assert "Assign to whole office" in home
        req = urlreq.Request(
            f"http://127.0.0.1:{port}/api/chat",
            data=json.dumps({"text": "hello architect"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        chat = json.loads(urlreq.urlopen(req, timeout=5).read().decode("utf-8"))
        assert chat["ok"] is True
        assert chat["chat"]
        assign = urlreq.Request(
            f"http://127.0.0.1:{port}/api/assign",
            data=json.dumps({"seat": "everyone", "task": "Keep LOOP moving"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        assigned = json.loads(urlreq.urlopen(assign, timeout=8).read().decode("utf-8"))
        assert assigned["ok"] is True
        assert not assigned["office"]["idle"]
        assert "Keep LOOP moving" in assigned["office"]["assignments"]["ada"]
        assert assigned["office"]["briefing"]["seat"] == "everyone"
        assert all(
            d["status"] == "working"
            for d in assigned["office"]["desks"]
            if not d.get("boss") and d.get("id") != "anshux"
        )
        assert any(d.get("boss") or d["id"] == "anshux" for d in assigned["office"]["desks"])
        assert "Progress" in home or "progress" in home.lower()
    finally:
        httpd.shutdown()


def test_find_project_semicolon(tmp_path, monkeypatch):
    fake = tmp_path / "semicolon"
    fake.mkdir()
    (fake / "ada_server.py").write_text("# test\n", encoding="utf-8")
    monkeypatch.setattr(team, "ROOT", tmp_path)

    def dirs(name: str):
        return [tmp_path / name]

    monkeypatch.setattr(team, "_candidate_dirs", dirs)
    assert team.find_project("semicolon") == fake.resolve()


def test_office_greets_anshux(monkeypatch, tmp_path):
    monkeypatch.setattr(team, "ROOT", tmp_path)
    monkeypatch.setattr(team, "http_status", lambda url, timeout=4.0: "200")
    monkeypatch.setattr(team, "_gh_prs", lambda repo: [])
    monkeypatch.setattr(team, "which", lambda cmd: None)
    monkeypatch.setattr(team, "tcp_open", lambda *a, **k: False)
    data = team.collect_office_state(network=False)
    assert data["boss"] == "AnshuX"
    assert data["greetings"]
    assert all("AnshuX" in g["text"] for g in data["greetings"])
    boss = next(d for d in data["desks"] if d.get("boss") or d["id"] == "anshux")
    assert boss["name"] == "AnshuX"
    assert "anshux" not in data["members"]
    assert data.get("progress") is not None
    team.assign_task("everyone", "Ship it")
    brief = team.load_assignments()
    assert all("AnshuX" in brief[d] for d in team.DESK_IDS)
    chat = team.architect_chat("hello")
    assert "AnshuX" in chat["reply"]


def test_boss_desk_and_progress_board(monkeypatch, tmp_path):
    monkeypatch.setattr(team, "ROOT", tmp_path)
    monkeypatch.setattr(team, "http_status", lambda url, timeout=4.0: "200")
    monkeypatch.setattr(team, "_gh_prs", lambda repo: [])
    monkeypatch.setattr(team, "which", lambda cmd: None)
    monkeypatch.setattr(team, "tcp_open", lambda *a, **k: False)
    team.assign_task("everyone", "Ship progress charts")
    data = team.collect_office_state(network=False)
    assert data["boss_desk"]["id"] == "anshux"
    assert "Ship progress charts" in data["boss_desk"]["task"]
    assert "Progress" in data["boss_desk"]["task"] or "progress" in data["boss_desk"]["task"].lower()
