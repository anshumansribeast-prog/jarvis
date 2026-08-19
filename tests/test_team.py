"""ANSHUX command hub."""

import team


def test_help_exits_zero():
    assert team.main(["help"]) == 0


def test_unknown_command():
    assert team.main(["not-a-command"]) == 1


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
