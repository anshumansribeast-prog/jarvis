"""AI Command Office — Commander, agents, and a real task queue.

Same process as the ANSHUX office on port 8765. No API keys in the browser.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = Path(__file__).resolve().parent
STATIC = PKG / "static"
DATA = PKG / "data"
WORKSPACE = PKG / "workspace"
MODEL = os.environ.get("COMMANDER_MODEL", "ollama/llama3.2:3b")

AGENTS = [
    {
        "id": "commander",
        "name": "COMMANDER",
        "role": "Lead + doer",
        "capabilities": ["plan", "assign the floor", "write the plan", "do a slice"],
        "model": MODEL,
    },
    {
        "id": "frontend",
        "name": "Frontend Agent",
        "role": "UI",
        "capabilities": ["html", "css", "js", "login screens"],
        "model": MODEL,
    },
    {
        "id": "backend",
        "name": "Backend Agent",
        "role": "API",
        "capabilities": ["python", "http", "auth stubs"],
        "model": MODEL,
    },
    {
        "id": "debugger",
        "name": "Debugger Agent",
        "role": "Bugs",
        "capabilities": ["pytest", "tracebacks", "login bugs"],
        "model": MODEL,
    },
    {
        "id": "testing",
        "name": "Testing Agent",
        "role": "QA",
        "capabilities": ["pytest"],
        "model": MODEL,
    },
    {
        "id": "review",
        "name": "Code Review Agent",
        "role": "Review",
        "capabilities": ["diff skim", "conventions"],
        "model": MODEL,
    },
    {
        "id": "research",
        "name": "Research Agent",
        "role": "Inspect",
        "capabilities": ["repo map", "live GET"],
        "model": MODEL,
    },
    {
        "id": "devops",
        "name": "DevOps Agent",
        "role": "Git/ops",
        "capabilities": ["git status"],
        "model": MODEL,
    },
    {
        "id": "security",
        "name": "Security Agent",
        "role": "Security",
        "capabilities": ["secret scan", "auth review"],
        "model": MODEL,
    },
]

STATUSES = (
    "QUEUED",
    "ASSIGNED",
    "RUNNING",
    "WAITING",
    "COMPLETED",
    "FAILED",
    "NEEDS_REVIEW",
    "CANCELLED",
)

DESTRUCTIVE = ("rm -rf", "delete all", "drop database", "format disk", "wipe")
