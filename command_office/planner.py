from __future__ import annotations

import re

from command_office import DESTRUCTIVE


def is_destructive(text: str) -> bool:
    low = text.lower()
    return any(tok in low for tok in DESTRUCTIVE)


def _give_to(text: str) -> str | None:
    m = re.search(
        r"(?:give|assign|ask)\s+(?:the\s+)?(frontend|backend|debugger|testing|test|review|research|devops|security)(?:\s+agent)?",
        text,
        re.I,
    )
    if not m:
        return None
    name = m.group(1).lower()
    return {"test": "testing", "testing": "testing"}.get(name, name)


def plan(text: str) -> dict:
    """Turn a Commander request into agent tasks. Deterministic; no cloud keys."""
    low = text.lower().strip()
    destructive = is_destructive(low)
    title = text.strip()[:80] or "Task"
    targeted = _give_to(low)

    if "progress" in low or "everyone" in low or "status" in low:
        return {"kind": "status", "summary": "Progress report requested.", "tasks": []}

    if targeted and not any(k in low for k in ("complete", "full", "entire", "system", "website", "authentication")):
        return {
            "kind": "assign",
            "summary": f"Commander assigned work to {targeted} agent.",
            "tasks": [
                {
                    "title": title,
                    "description": text.strip(),
                    "agent": targeted,
                    "priority": "normal",
                    "depends": [],
                }
            ],
        }

    auth = "auth" in low or "login" in low or "register" in low
    website = "website" in low or "frontend and backend" in low or "complete" in low
    bug = "bug" in low or "fix" in low or "debug" in low
    check = "check the project" in low or low.startswith("check ")
    tests = "test" in low

    tasks: list[dict] = []

    if auth and ("system" in low or "complete" in low or "full" in low):
        tasks = [
            {"title": "Build authentication API", "description": text, "agent": "backend", "priority": "high", "depends": []},
            {"title": "Build login/register interface", "description": text, "agent": "frontend", "priority": "high", "depends": []},
            {"title": "Review authentication security", "description": text, "agent": "security", "priority": "high", "depends": [0, 1]},
            {"title": "Test the complete auth system", "description": text, "agent": "testing", "priority": "high", "depends": [0, 1]},
            {"title": "Review final implementation", "description": text, "agent": "review", "priority": "normal", "depends": [2, 3]},
        ]
    elif website or "frontend and backend" in low:
        tasks = [
            {"title": "Build frontend", "description": text, "agent": "frontend", "priority": "high", "depends": []},
            {"title": "Build backend", "description": text, "agent": "backend", "priority": "high", "depends": []},
            {"title": "Test frontend and backend", "description": text, "agent": "testing", "priority": "normal", "depends": [0, 1]},
        ]
    elif bug:
        tasks = [
            {"title": title, "description": text, "agent": "debugger", "priority": "high", "depends": []},
            {"title": "Regression tests after fix", "description": text, "agent": "testing", "priority": "normal", "depends": [0]},
        ]
    elif check:
        tasks = [
            {"title": "Inspect project layout", "description": text, "agent": "research", "priority": "normal", "depends": []},
            {"title": "Run test suite", "description": text, "agent": "testing", "priority": "normal", "depends": []},
            {"title": "Git status", "description": text, "agent": "devops", "priority": "low", "depends": []},
        ]
    elif tests:
        tasks = [{"title": "Run tests", "description": text, "agent": "testing", "priority": "high", "depends": []}]
    else:
        tasks = [
            {"title": title, "description": text, "agent": "research", "priority": "normal", "depends": []},
            {"title": "Implement requested work", "description": text, "agent": "backend", "priority": "normal", "depends": [0]},
            {"title": "Verify with tests", "description": text, "agent": "testing", "priority": "normal", "depends": [1]},
        ]

    return {
        "kind": "plan",
        "summary": "Commander split the request into agent tasks.",
        "destructive": destructive,
        "tasks": tasks,
    }
