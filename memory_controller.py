"""Personal facts Jarvis is told to remember — persisted to config/facts.json
so they survive restarts, unlike Ollama's stateless single-turn calls."""

import json
import os

FACTS_PATH = os.path.join(os.path.dirname(__file__), "config", "facts.json")

# Separate from personal facts above: what Jarvis knows about Anshuman's own
# coding projects (Semicolon/Ada, astronomy-site/Beast, Cosmos v2, Jarvis
# itself), so he can ask Jarvis about them and get a grounded answer instead
# of Ollama guessing. Kept as its own file/functions rather than folded into
# facts.json, since "their X is Y" phrasing for a person doesn't fit project
# descriptions — see how each is worded into the system prompt in jarvis.py.
PROJECTS_PATH = os.path.join(os.path.dirname(__file__), "config", "projects.json")


def _load():
    if not os.path.exists(FACTS_PATH):
        return {}
    with open(FACTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(facts):
    os.makedirs(os.path.dirname(FACTS_PATH), exist_ok=True)
    with open(FACTS_PATH, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2)


def remember(key, value):
    facts = _load()
    facts[key.strip().lower()] = value.strip()
    _save(facts)


def recall(key):
    return _load().get(key.strip().lower())


def all_facts():
    return _load()


def _load_projects():
    if not os.path.exists(PROJECTS_PATH):
        return {}
    with open(PROJECTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_projects(projects):
    os.makedirs(os.path.dirname(PROJECTS_PATH), exist_ok=True)
    with open(PROJECTS_PATH, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)


def remember_project(name, description):
    projects = _load_projects()
    projects[name.strip().lower()] = description.strip()
    _save_projects(projects)


def project_facts():
    return _load_projects()
