"""Persistent memory — wraps legacy memory_controller with AnshuX features."""

from __future__ import annotations

import json
import os
import re

import memory_controller

from ansux.config import settings

PREFS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "preferences.json")
SECRET_PATTERN = re.compile(
    r"(password|api[_-]?key|token|secret|private[_-]?key|credential)",
    re.IGNORECASE,
)


def _load_prefs() -> dict:
    path = os.path.normpath(PREFS_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_prefs(prefs: dict) -> None:
    path = os.path.normpath(PREFS_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2)


def remember(key: str, value: str) -> tuple[bool, str]:
    key = key.strip().lower()
    value = value.strip()
    if SECRET_PATTERN.search(key) or SECRET_PATTERN.search(value):
        return False, "I won't store passwords, API keys, or other secrets in memory."
    memory_controller.remember(key, value)
    return True, f"Got it. I'll remember your {key} is {value}."


def recall(key: str) -> str | None:
    return memory_controller.recall(key.strip().lower())


def forget(key: str) -> tuple[bool, str]:
    facts = memory_controller.all_facts()
    key = key.strip().lower()
    if key not in facts:
        return False, f"I don't have anything stored for {key}."
    del facts[key]
    path = memory_controller.FACTS_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2)
    return True, f"Forgotten: {key}."


def all_facts() -> dict:
    return memory_controller.all_facts()


def project_facts() -> dict:
    return memory_controller.project_facts()


def remember_project(name: str, description: str) -> tuple[bool, str]:
    if SECRET_PATTERN.search(description):
        return False, "I won't store secrets in project memory."
    memory_controller.remember_project(name, description)
    return True, f"I'll remember your {name} project as {description}."


def summarize_memory() -> str:
    facts = all_facts()
    prefs = _load_prefs()
    projects = project_facts()
    parts = [f"User: {settings.USER_NAME}", f"Assistant: {settings.ASSISTANT_NAME}"]
    if facts:
        parts.append("Facts: " + "; ".join(f"{k}={v}" for k, v in facts.items()))
    if projects:
        parts.append("Projects: " + ", ".join(projects.keys()))
    if prefs:
        parts.append("Preferences: " + "; ".join(f"{k}={v}" for k, v in prefs.items()))
    return ". ".join(parts) if parts else "I don't have anything stored yet."


def clear_all() -> str:
    path = memory_controller.FACTS_PATH
    if os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)
    prefs_path = os.path.normpath(PREFS_PATH)
    if os.path.exists(prefs_path):
        os.remove(prefs_path)
    return "Memory cleared. I kept project descriptions in config/projects.json."
