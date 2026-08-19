"""ANSHUX command hub."""

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


def test_find_project_semicolon(tmp_path, monkeypatch):
    fake = tmp_path / "semicolon"
    fake.mkdir()
    (fake / "ada_server.py").write_text("# test\n", encoding="utf-8")
    monkeypatch.setattr(team, "ROOT", tmp_path)

    def dirs(name: str):
        return [tmp_path / name]

    monkeypatch.setattr(team, "_candidate_dirs", dirs)
    assert team.find_project("semicolon") == fake.resolve()
