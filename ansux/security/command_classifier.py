"""Terminal command safety classification."""

from __future__ import annotations

import re
from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"


_DANGEROUS = re.compile(
    r"\b(rm\s+-rf|del\s+/[sfq]|format\s+[a-z]:|diskpart|shutdown|restart|"
    r"reg\s+delete|netsh|bcdedit|cipher\s+/w|takeown|icacls|"
    r"git\s+push|npm\s+publish|pip\s+install\s+http|curl\s+.*\|\s*bash)\b",
    re.IGNORECASE,
)
_CAUTION = re.compile(
    r"\b(pip\s+install|npm\s+install|pnpm\s+install|yarn\s+add|"
    r"chmod|chown|set-executionpolicy|install-module|winget\s+install|"
    r"npm\s+run|pnpm\s+run|yarn\s+run|python\s+-m\s+pip)\b",
    re.IGNORECASE,
)


def classify_command(command: str) -> RiskLevel:
    cmd = command.strip()
    if not cmd:
        return RiskLevel.SAFE
    if _DANGEROUS.search(cmd):
        return RiskLevel.DANGEROUS
    if _CAUTION.search(cmd):
        return RiskLevel.CAUTION
    return RiskLevel.SAFE


def confirmation_message(command: str, risk: RiskLevel) -> str:
    if risk == RiskLevel.DANGEROUS:
        return f"Anshu, this command is dangerous: {command}. Proceed?"
    if risk == RiskLevel.CAUTION:
        return f"This will modify your environment: {command}. Proceed?"
    return ""
