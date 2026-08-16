"""Safe terminal command execution."""

from __future__ import annotations

import subprocess
from typing import Callable

from ansux.security.command_classifier import RiskLevel, classify_command, confirmation_message


def run(command: str, cwd: str | None = None, confirm: Callable[[str], bool] | None = None) -> tuple[bool, str]:
    risk = classify_command(command)
    if risk != RiskLevel.SAFE:
        prompt = confirmation_message(command, risk)
        if confirm is None or not confirm(prompt):
            return False, "Command cancelled."
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return False, "Command timed out."
    except OSError as exc:
        return False, str(exc)
    if result.returncode != 0:
        return False, (result.stderr or result.stdout or "Command failed.").strip()[:300]
    return True, (result.stdout or "Done.").strip()[:300]
