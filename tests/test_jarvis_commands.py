import os

import jarvis


def test_backend_site_uses_live_back_path():
    assert jarvis.SITES["backend"].rstrip("/") == "https://cosmos.punah.pro/back"


def test_looks_related_shares_meaningful_word():
    assert jarvis._looks_related("how many moons does Jupiter have", "Jupiter")


def test_looks_related_rejects_unrelated_topic():
    assert not jarvis._looks_related(
        "study motivation quote",
        "Subhas Chandra Bose",
    )


def test_looks_related_ignores_stopwords():
    assert not jarvis._looks_related("what is the the", "The")


def test_handle_remember_and_recall(monkeypatch, facts_file):
    spoken = []
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))

    assert jarvis.handle_command("remember my favorite song is Perfect") is True
    assert spoken[-1] == "Got it. I'll remember your favorite song is Perfect."

    spoken.clear()
    assert jarvis.handle_command("what's my favorite song") is True
    assert spoken[-1] == "Your favorite song is Perfect."


def test_handle_remember_without_is_prompts(monkeypatch):
    spoken = []
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    jarvis.handle_command("remember my favorite song")
    assert "Tell me what to remember" in spoken[-1]


def test_handle_time(monkeypatch):
    spoken = []
    real_datetime = jarvis.datetime.datetime

    class FrozenDateTime:
        @staticmethod
        def now():
            return real_datetime(2026, 8, 17, 9, 5)

    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    monkeypatch.setattr(jarvis.datetime, "datetime", FrozenDateTime)
    jarvis.handle_command("what time is it")
    assert spoken[-1] == "It's 09:05 AM."


def test_handle_joke(monkeypatch):
    spoken = []
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    monkeypatch.setattr(jarvis.random, "choice", lambda jokes: jokes[0])
    jarvis.handle_command("tell me a joke")
    assert spoken[-1] == jarvis.JOKES[0]


def test_handle_goodbye_stops_loop(monkeypatch):
    spoken = []
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    assert jarvis.handle_command("goodbye") is False
    assert spoken[-1] == "Goodbye, Anshuman."


def test_handle_empty_text_keeps_running():
    assert jarvis.handle_command("") is True


def test_unknown_command_falls_back_to_answer_question(monkeypatch):
    spoken = []
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    monkeypatch.setattr(jarvis, "answer_question", lambda _query: False)
    jarvis.handle_command("blorptastic frobnicate")
    assert spoken[-1] == "I don't know that one, and I couldn't find an answer either."


def test_open_unknown_project(monkeypatch):
    spoken = []
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    jarvis.handle_command("open widget project")
    assert "don't have a project called widget" in spoken[-1]


def test_create_folder_called_on_desktop(monkeypatch, isolated_home):
    spoken = []
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    jarvis.handle_command("create a folder called qa-notes")
    _home, folders = isolated_home
    assert os.path.isdir(os.path.join(folders["desktop"], "qa-notes"))
    assert spoken[-1] == "Created the folder qa-notes on your desktop."


def test_delete_aborts_without_confirm(monkeypatch, isolated_home):
    spoken = []
    _home, folders = isolated_home
    target = os.path.join(folders["desktop"], "keep.txt")
    with open(target, "w", encoding="utf-8"):
        pass
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    monkeypatch.setattr(jarvis, "confirm", lambda _prompt: False)
    jarvis.handle_command("delete keep.txt")
    assert os.path.isfile(target)
    assert spoken[-1] == "Okay, I won't delete it."


def test_delete_removes_file_when_confirmed(monkeypatch, isolated_home):
    spoken = []
    _home, folders = isolated_home
    target = os.path.join(folders["desktop"], "gone.txt")
    with open(target, "w", encoding="utf-8"):
        pass
    monkeypatch.setattr(jarvis, "speak", lambda text: spoken.append(text))
    monkeypatch.setattr(jarvis, "confirm", lambda _prompt: True)
    jarvis.handle_command("delete gone.txt")
    assert not os.path.exists(target)
    assert spoken[-1] == "Deleted gone.txt."
