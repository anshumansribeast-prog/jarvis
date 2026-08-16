"""Multi-step task planning for broad development requests."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from ansux.config import settings


@dataclass
class PlanStep:
    description: str
    action: str
    args: dict


def _detect_package_manager(project_path: str) -> str | None:
    if os.path.isfile(os.path.join(project_path, "package.json")):
        if os.path.isfile(os.path.join(project_path, "pnpm-lock.yaml")):
            return "pnpm"
        if os.path.isfile(os.path.join(project_path, "yarn.lock")):
            return "yarn"
        return "npm"
    if os.path.isfile(os.path.join(project_path, "pyproject.toml")) or os.path.isfile(
        os.path.join(project_path, "requirements.txt")
    ):
        return "python"
    return None


def _read_scripts(project_path: str) -> dict[str, str]:
    pkg = os.path.join(project_path, "package.json")
    if not os.path.isfile(pkg):
        return {}
    with open(pkg, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("scripts", {})


def plan_development_workflow(project_name: str, project_path: str) -> list[PlanStep]:
    steps: list[PlanStep] = [
        PlanStep("Open project folder", "open_folder", {"path": project_path}),
        PlanStep("Open VS Code", "open_vscode", {"path": project_path}),
    ]
    pm = _detect_package_manager(project_path)
    scripts = _read_scripts(project_path)
    if pm in ("npm", "pnpm", "yarn") and "dev" in scripts:
        steps.append(
            PlanStep(
                f"Start development server ({pm} run dev)",
                "run_dev_server",
                {"path": project_path, "manager": pm, "script": "dev"},
            )
        )
    elif pm == "python" and os.path.isfile(os.path.join(project_path, "requirements.txt")):
        steps.append(
            PlanStep(
                "Install Python dependencies",
                "run_command",
                {"path": project_path, "command": "python -m pip install -r requirements.txt"},
            )
        )
    steps.append(
        PlanStep(
            f"Report project status for {project_name}",
            "inspect_project",
            {"path": project_path, "manager": pm or "unknown"},
        )
    )
    return steps


def resolve_project(text: str, context_project: str | None = None) -> tuple[str, str] | None:
    lowered = text.lower()
    for name, path in settings.PROJECTS.items():
        if name in lowered and os.path.isdir(path):
            return name, path
    if context_project and context_project in settings.PROJECTS:
        path = settings.PROJECTS[context_project]
        if os.path.isdir(path):
            return context_project, path
    return None
