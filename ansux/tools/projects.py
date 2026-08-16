"""Project and development workflow tools."""

from __future__ import annotations

import json
import os
import platform
import subprocess

from ansux.config import settings
from ansux.security.command_classifier import RiskLevel, classify_command, confirmation_message
from ansux.tools import filesystem


def open_project_in_vscode(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    if platform.system() == "Windows":
        subprocess.Popen(["code", path], shell=True)
        return True
    try:
        subprocess.Popen(["code", path])
        return True
    except FileNotFoundError:
        return False


def open_project_folder(path: str) -> None:
    filesystem.open_path(path)


def inspect_project(path: str) -> dict:
    info: dict = {"path": path, "exists": os.path.isdir(path)}
    if not info["exists"]:
        return info
    entries = os.listdir(path)
    info["top_level"] = entries[:20]
    if os.path.isfile(os.path.join(path, "package.json")):
        with open(os.path.join(path, "package.json"), "r", encoding="utf-8") as f:
            pkg = json.load(f)
        info["package_manager"] = (
            "pnpm" if os.path.isfile(os.path.join(path, "pnpm-lock.yaml"))
            else "yarn" if os.path.isfile(os.path.join(path, "yarn.lock"))
            else "npm"
        )
        info["scripts"] = list(pkg.get("scripts", {}).keys())
    if os.path.isfile(os.path.join(path, "requirements.txt")):
        info["python_project"] = True
    return info


def run_command(path: str, command: str, confirm) -> tuple[bool, str]:
    risk = classify_command(command)
    if risk != RiskLevel.SAFE:
        prompt = confirmation_message(command, risk)
        if not confirm(prompt):
            return False, "Command cancelled."
    try:
        result = subprocess.run(
            command,
            cwd=path,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return False, "The command timed out."
    except OSError as exc:
        return False, f"Command failed: {exc}"
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "unknown error").strip()
        return False, f"Command failed: {err[:200]}"
    return True, "Command completed successfully."


def start_dev_server(path: str, manager: str, script: str, confirm) -> tuple[bool, str]:
    cmd = f"{manager} run {script}"
    return run_command(path, cmd, confirm)
