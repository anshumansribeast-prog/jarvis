from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from command_office import ROOT, WORKSPACE
from command_office.store import append_progress, ensure_dirs, ensure_project, project_slug

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


def _note(slug: str, agent_id: str, text: str) -> str:
    rel = f"projects/{slug}/notes/{agent_id}.md"
    path = _safe_write(rel, f"# {agent_id}\n\n{text}\n")
    append_progress(slug, agent_id, text[:240])
    return path


def _python() -> str:
    venv_py = ROOT / ".venv" / "bin" / "python"
    if venv_py.is_file():
        return str(venv_py)
    return sys.executable


def run_agent(agent_id: str, task: dict) -> tuple[bool, str]:
    ensure_dirs()
    info = ensure_project()
    slug = info["slug"] or project_slug()
    title = task.get("title") or ""
    desc = task.get("description") or title
    py = _python()

    if agent_id == "commander":
        names = sorted(p.name for p in ROOT.iterdir() if not p.name.startswith("."))[:30]
        body = (
            f"# Commander slice\n\nRequest:\n\n{desc}\n\n"
            f"OpenCode and Commander are one lead. Floor started.\n\n"
            f"Shared storage: `command_office/workspace/projects/{slug}/`\n\n"
            f"Repo top-level: {', '.join(names)}\n"
        )
        path = _safe_write(f"projects/{slug}/COMMANDER.md", body)
        legacy = _safe_write("commander/plan.md", body)
        note = _safe_write("commander/slice.txt", f"COMMANDER executed this request:\n{title}\n")
        _note(slug, "commander", f"Wrote plan → {path}")
        return True, f"Commander wrote {path} (also {legacy}, {note}). Open Storage to see progress."

    if agent_id == "frontend":
        site_title = slug.replace("-", " ").title()
        html = (
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>{site_title}</title>"
            "<style>body{font-family:Georgia,serif;margin:0;background:#0f1418;color:#e8eef2}"
            "header{padding:2.5rem 1.5rem;background:linear-gradient(120deg,#1a2a22,#0f1418)}"
            "main{padding:1.5rem;max-width:42rem}a{color:#8ec8ff}</style></head>"
            f"<body><header><h1>{site_title}</h1>"
            f"<p>Shared site build · task: {title}</p></header>"
            "<main><p>Frontend Agent saved this page into the shared project storage.</p>"
            "<p>Everyone’s progress is in <code>PROGRESS.md</code> next to this folder.</p>"
            "</main></body></html>\n"
        )
        path = _safe_write(f"projects/{slug}/site/index.html", html)
        login = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Auth UI</title></head>"
            "<body><h1>Login</h1><form><input name='user' placeholder='user'>"
            "<input name='pass' type='password' placeholder='password'>"
            "<button>Sign in</button></form>"
            f"<p>Task: {title}</p></body></html>\n"
        )
        login_path = _safe_write(f"projects/{slug}/site/login.html", login)
        _safe_write("frontend/login.html", login)
        _note(slug, "frontend", f"Wrote site pages → {path}, {login_path}")
        return True, f"Wrote {path} and {login_path}"

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
        path = _safe_write(f"projects/{slug}/backend/auth_stub.py", py)
        _safe_write("backend/auth_stub.py", py)
        _note(slug, "backend", f"Wrote API stub → {path}")
        return True, f"Wrote {path} (stub auth API, not started)"

    if agent_id == "testing":
        ok, out = _run(
            [
                py,
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
        _note(slug, "testing", f"pytest {'ok' if ok else 'failed'}: {(out or '')[:180]}")
        return ok, out or "(no pytest output)"

    if agent_id == "debugger":
        ok, out = _run(
            [py, "-m", "pytest", "-q", "tests/test_app_controller.py", "--tb=line"],
            timeout=60,
        )
        extra = "login" if "login" in desc.lower() else "general"
        _note(slug, "debugger", f"debugger focus={extra}")
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
        _note(slug, "security", msg.split("\n")[0])
        return True, msg

    if agent_id == "research":
        names = sorted(p.name for p in ROOT.iterdir() if not p.name.startswith("."))[:40]
        project_files = sorted(
            str(p.relative_to(WORKSPACE)).replace("\\", "/")
            for p in (WORKSPACE / "projects" / slug).rglob("*")
            if p.is_file()
        )[:30]
        msg = "project root: " + ", ".join(names) + "\nstorage: " + ", ".join(project_files)
        _note(slug, "research", f"Mapped {len(project_files)} storage files")
        return True, msg

    if agent_id == "devops":
        ok, out = _run(["git", "status", "--short"], timeout=20)
        _note(slug, "devops", (out or "clean")[:200])
        return ok, out or "(clean or git missing)"

    if agent_id == "review":
        files = []
        site = WORKSPACE / "projects" / slug / "site"
        if site.is_dir():
            files.extend(
                f"command_office/workspace/projects/{slug}/site/{p.name}"
                for p in sorted(site.iterdir())
                if p.is_file()
            )
        note = "reviewed: " + (", ".join(files) if files else "no workspace artifacts yet")
        _note(slug, "review", note[:200])
        return True, note + "\nKeep Generator off Semicolon. No secrets in frontend."

    return False, f"unknown agent {agent_id}"
