"""ANSHUX command hub."""

import json

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


def test_architect_chat_queues_without_opencode(monkeypatch, tmp_path):
    monkeypatch.setattr(team, "ROOT", tmp_path)
    monkeypatch.setattr(team, "which", lambda cmd: None)
    result = team.architect_chat("inspect both sites")
    assert "queued" in result["reply"].lower() or "PATH" in result["reply"]
    assert result["chat"][-1]["who"] == "opencode"


def test_find_project_semicolon(tmp_path, monkeypatch):
    fake = tmp_path / "semicolon"
    fake.mkdir()
    (fake / "ada_server.py").write_text("# test\n", encoding="utf-8")
    monkeypatch.setattr(team, "ROOT", tmp_path)

    def dirs(name: str):
        return [tmp_path / name]

    monkeypatch.setattr(team, "_candidate_dirs", dirs)
    assert team.find_project("semicolon") == fake.resolve()
