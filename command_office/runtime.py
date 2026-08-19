from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from command_office import ROOT, WORKSPACE
from command_office.store import ensure_dirs

_KEEP_ENV = {"PATH", "HOME", "LANG", "PYTHONPATH", "SYSTEMROOT", "TMP", "TEMP", "USERPROFILE"}


def _safe_env() -> dict[str, str]:
    blocked = ("API_KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL")
    out = {}
    for key, value in os.environ.items():
        upper = key.upper()
        if any(part in upper for part in blocked) and upper not in _KEEP_ENV:
            continue
        out[key] = value
    return out


def _run(argv: list[str], cwd: Path | None = None, timeout: int = 90) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd or ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_safe_env(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, out[-8000:]


def _safe_write(rel: str, content: str) -> str:
    ensure_dirs()
    path = (WORKSPACE / rel).resolve()
    if WORKSPACE.resolve() not in path.parents and path != WORKSPACE.resolve():
        raise ValueError("write outside workspace")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path.relative_to(ROOT)) if str(path).startswith(str(ROOT)) else str(path)


def run_agent(agent_id: str, task: dict) -> tuple[bool, str]:
    ensure_dirs()
    title = task.get("title") or ""
    desc = task.get("description") or title

    if agent_id == "commander":
        names = sorted(p.name for p in ROOT.iterdir() if not p.name.startswith("."))[:30]
        body = (
            f"# Commander slice\n\nRequest:\n\n{desc}\n\n"
            f"OpenCode and Commander are one lead. Floor started.\n\n"
            f"Repo top-level: {', '.join(names)}\n"
        )
        path = _safe_write("commander/plan.md", body)
        note = _safe_write("commander/slice.txt", f"COMMANDER executed this request:\n{title}\n")
        return True, f"Commander wrote {path} and {note}"

    if agent_id == "frontend":
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Auth UI</title></head>"
            "<body><h1>Login</h1><form><input name='user' placeholder='user'>"
            "<input name='pass' type='password' placeholder='password'>"
            "<button>Sign in</button></form>"
            f"<p>Task: {title}</p></body></html>\n"
        )
        path = _safe_write("frontend/login.html", html)
        return True, f"Wrote {path}"

    if agent_id == "backend":
        py = (
            "from http.server import BaseHTTPRequestHandler, HTTPServer\n"
            "class H(BaseHTTPRequestHandler):\n"
            "    def do_GET(self):\n"
            "        self.send_response(200)\n"
            "        self.send_header('Content-Type', 'application/json')\n"
            "        self.end_headers()\n"
            "        self.wfile.write(b'{\"ok\":true,\"auth\":\"stub\"}')\n"
            "    def log_message(self, *a):\n"
            "        return\n"
            "if __name__ == '__main__':\n"
            "    HTTPServer(('127.0.0.1', 8780), H).serve_forever()\n"
        )
        path = _safe_write("backend/auth_stub.py", py)
        return True, f"Wrote {path} (stub auth API, not started)"

    if agent_id == "testing":
        ok, out = _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--tb=line",
                "tests/test_team.py",
                "tests/test_file_controller.py",
                "tests/test_memory_controller.py",
                "tests/test_app_controller.py",
            ],
            timeout=90,
        )
        return ok, out or "(no pytest output)"

    if agent_id == "debugger":
        ok, out = _run(
            [sys.executable, "-m", "pytest", "-q", "tests/test_app_controller.py", "--tb=line"],
            timeout=60,
        )
        extra = "login" if "login" in desc.lower() else "general"
        return ok, f"debugger focus={extra}\n{out}"

    if agent_id == "security":
        hits = []
        for p in ROOT.rglob("*.py"):
            if any(part in p.parts for part in (".git", "venv", "__pycache__", "voices")):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if re.search(r"(api_key|secret|password)\s*=\s*['\"][^'\"]+['\"]", text, re.I):
                if "DESTRUCTIVE" in text or "placeholder" in text.lower():
                    continue
                hits.append(str(p.relative_to(ROOT)))
            if len(hits) > 12:
                break
        msg = "no hardcoded key assignments found in scanned Python" if not hits else "possible secrets:\n" + "\n".join(hits)
        return True, msg

    if agent_id == "research":
        names = sorted(p.name for p in ROOT.iterdir() if not p.name.startswith("."))[:40]
        return True, "project root: " + ", ".join(names)

    if agent_id == "devops":
        ok, out = _run(["git", "status", "--short"], timeout=20)
        return ok, out or "(clean or git missing)"

    if agent_id == "review":
        files = []
        if (WORKSPACE / "frontend" / "login.html").is_file():
            files.append("command_office/workspace/frontend/login.html")
        if (WORKSPACE / "backend" / "auth_stub.py").is_file():
            files.append("command_office/workspace/backend/auth_stub.py")
        note = "reviewed: " + (", ".join(files) if files else "no workspace artifacts yet")
        return True, note + "\nKeep Generator off Semicolon. No secrets in frontend."

    return False, f"unknown agent {agent_id}"
