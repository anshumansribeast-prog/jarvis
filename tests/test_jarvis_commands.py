from unittest.mock import MagicMock

import jarvis


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
