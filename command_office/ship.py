"""Ship the office: status report, GitHub push note, mail Abhishek."""

from __future__ import annotations

import os
import smtplib
import subprocess
import urllib.parse
from email.message import EmailMessage

from command_office import BOSS_NAME, ROOT, greet
from command_office.store import (
    _load,
    _now,
    _save,
    progress_board,
    project_snapshot,
    snapshot,
    update_settings,
)

DEFAULT_ABHISHEK = os.environ.get("ANSHUX_ABHISHEK_EMAIL", "abhiis@eleven11.pro").strip()


def _git(*args: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, out[-4000:]


def abhishek_email() -> str:
    settings = _load("settings.json", {})
    return str(settings.get("abhishek_email") or DEFAULT_ABHISHEK or "").strip()


def set_abhishek_email(email: str) -> dict:
    email = (email or "").strip()[:120]
    return update_settings({"abhishek_email": email})


def build_report() -> dict:
    state = snapshot()
    board = state.get("progress") or progress_board()
    storage = state.get("storage") or project_snapshot()
    agents = board.get("agents") or []
    lines = [
        f"# ANSHUX office report for Abhishek",
        f"",
        f"From: {BOSS_NAME}",
        f"When: {_now()}",
        f"",
        greet("here is what the floor shipped."),
        f"",
        f"## Overall",
        f"- Progress: {board.get('overall_percent', 0)}% "
        f"({board.get('overall_completed', 0)}/{board.get('overall_total', 0)} tasks)",
        f"- Storage: `command_office/workspace/{storage.get('path', 'projects/…')}/`",
        f"- PR: https://github.com/anshumansribeast-prog/jarvis/pull/2",
        f"",
        f"## Per-agent work",
    ]
    for a in agents:
        lines.append(
            f"- **{a.get('name')}**: {a.get('percent', 0)}% · "
            f"{a.get('completed', 0)}/{a.get('total', 0)} done · status {a.get('status')} · "
            f"last #{a.get('last_task') or '—'} {a.get('last_result') or ''}"
        )
    lines.extend(["", "## Recent tasks"])
    for t in (state.get("tasks") or [])[-12:]:
        lines.append(
            f"- #{t.get('id')} {t.get('title')} — {t.get('status')} ({t.get('agent')})"
        )
    ok, branch = _git("branch", "--show-current")
    ok2, status = _git("status", "--short")
    lines.extend(
        [
            "",
            "## Git",
            f"- Branch: {branch if ok else 'unknown'}",
            f"- Status:",
            "```",
            status if ok2 else "(git status failed)",
            "```",
            "",
            f"— {BOSS_NAME} / COMMANDER",
        ]
    )
    body = "\n".join(lines)
    path = ROOT / "office" / "briefing-abhishek.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return {
        "body": body,
        "path": "office/briefing-abhishek.md",
        "branch": branch if ok else "",
        "progress": board,
        "storage": storage,
        "abhishek_email": abhishek_email(),
        "pr_url": "https://github.com/anshumansribeast-prog/jarvis/pull/2",
        "repo": "https://github.com/anshumansribeast-prog/jarvis",
    }


def mailto_link(report: dict | None = None) -> str:
    report = report or build_report()
    to = report.get("abhishek_email") or abhishek_email()
    subject = f"ANSHUX office report from {BOSS_NAME}"
    body = report.get("body") or ""
    # Keep mailto bodies reasonable for clients.
    return "mailto:{to}?subject={sub}&body={body}".format(
        to=urllib.parse.quote(to, safe="@.+-_"),
        sub=urllib.parse.quote(subject),
        body=urllib.parse.quote(body[:1800]),
    )


def push_github() -> dict:
    ok_b, branch = _git("branch", "--show-current")
    branch = branch if ok_b else "cursor/anshx-qa-loop-8b8a"
    ok, out = _git("push", "-u", "origin", branch)
    return {"ok": ok, "branch": branch, "output": out, "pr_url": "https://github.com/anshumansribeast-prog/jarvis/pull/2"}


def send_mail_smtp(report: dict | None = None) -> dict:
    report = report or build_report()
    to = abhishek_email()
    host = os.environ.get("ANSHUX_SMTP_HOST", "").strip()
    user = os.environ.get("ANSHUX_SMTP_USER", "").strip()
    password = os.environ.get("ANSHUX_SMTP_PASS", "").strip()
    port = int(os.environ.get("ANSHUX_SMTP_PORT", "587") or 587)
    sender = os.environ.get("ANSHUX_SMTP_FROM", user or f"{BOSS_NAME.lower()}@localhost")
    if not to:
        return {"ok": False, "error": "Set Abhishek email in Settings (or ANSHUX_ABHISHEK_EMAIL)."}
    if not host or not user or not password:
        return {
            "ok": False,
            "error": "SMTP not configured. Use mailto link, or set ANSHUX_SMTP_HOST/USER/PASS.",
            "mailto": mailto_link(report),
            "saved": report.get("path"),
        }
    msg = EmailMessage()
    msg["Subject"] = f"ANSHUX office report from {BOSS_NAME}"
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(report["body"])
    try:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "mailto": mailto_link(report)}
    return {"ok": True, "to": to, "saved": report.get("path")}


def ship_all(*, push: bool = True, mail: bool = True) -> dict:
    """End-of-loop: report + optional push + mail Abhishek."""
    report = build_report()
    result = {
        "ok": True,
        "greet": greet("shipping the office to GitHub and Abhishek."),
        "report": report,
        "mailto": mailto_link(report),
        "push": None,
        "mail": None,
    }
    if push:
        result["push"] = push_github()
        if not result["push"].get("ok"):
            result["ok"] = False
    if mail:
        result["mail"] = send_mail_smtp(report)
        # Mailto fallback still counts as a delivered path for the boss.
        if not result["mail"].get("ok") and result["mail"].get("mailto"):
            result["mail"]["fallback"] = "mailto"
    _save(
        "ship_log.json",
        (_load("ship_log.json", []) + [{"t": _now(), "branch": report.get("branch"), "to": abhishek_email()}])[-40:],
    )
    return result
