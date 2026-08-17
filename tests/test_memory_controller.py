import json

import memory_controller


def test_remember_and_recall(facts_file):
    memory_controller.remember("favorite song", "Perfect by Ed Sheeran")
    assert memory_controller.recall("favorite song") == "Perfect by Ed Sheeran"
    stored = json.loads(facts_file.read_text(encoding="utf-8"))
    assert stored["favorite song"] == "Perfect by Ed Sheeran"


def test_recall_is_case_insensitive(facts_file):
    memory_controller.remember("  Favorite Color  ", "  Blue  ")
    assert memory_controller.recall("FAVORITE COLOR") == "Blue"


def test_recall_unknown_key_returns_none(facts_file):
    assert memory_controller.recall("middle name") is None


def test_all_facts_returns_everything_remembered(facts_file):
    memory_controller.remember("dog", "Rex")
    memory_controller.remember("city", "Delhi")
    assert memory_controller.all_facts() == {"dog": "Rex", "city": "Delhi"}


def test_load_missing_file_is_empty(facts_file):
    assert not facts_file.exists()
    assert memory_controller.all_facts() == {}
