#!/usr/bin/env python3
"""ANSHUX terminal work area (Codex / Claude Code style).

  python team.py                 work area prompt (stays open)
  python team.py check the sites
  python team.py sites
  python team.py office          office floor (see the team)
  python team.py opencode        architect of the office (sites + PRs)
  python team.py menu            numbered list (old)
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITES = (
    ("Semicolon", "https://semicolon.punah.pro/"),
    ("Ada chat", "https://semicolon.punah.pro/pages/ada.html"),
    ("Concepts", "https://semicolon.punah.pro/pages/concepts.html"),
    ("Generator (should 404 later)", "https://semicolon.punah.pro/pages/generate.html"),
    ("Cosmos", "https://cosmos.punah.pro/"),
    ("Cosmos /back", "https://cosmos.punah.pro/back"),
)

# Plain English -> command key
ALIASES: dict[str, tuple[str, ...]] = {
    "status": (
        "status", "board", "show all systems", "show systems", "systems",
        "all systems", "1",
    ),
    "sites": (
        "sites", "site", "check the sites", "check sites", "check site",
        "ping", "ping sites", "live", "live sites", "semicolon", "cosmos",
        "2",
    ),
    "opencode": (
        "opencode", "open code", "opencod", "main", "agent", "codex",
        "claude code", "3",
    ),
    "aider": ("aider", "4"),
    "ada": ("ada", "tutor", "5"),
    "jarvis": ("jarvis", "voice", "6"),
    "pytest": ("pytest", "test", "tests", "7"),
    "start-all": ("start-all", "start all", "startall", "8"),
    "continue": (
        "continue", "workspace", "open workspace", "open anshux",
        "anshux.code-workspace", "open_anshux.bat", "open anshux.bat",
        "code-workspace", "9",
    ),
    "office": (
        "office", "floor", "see the team", "see team", "work office",
        "open office", "10",
    ),
    "help": ("help", "/help", "?", "h"),
    "quit": ("q", "quit", "exit", "/q", "/quit"),
}


def _candidate_dirs(name: str) -> list[Path]:
    home = Path.home()
    return [
        ROOT / "projects" / name,
        ROOT.parent / name,
        home / name,
        home / "anshux" / "projects" / name,
        Path(f"C:/Users/Anshu/{name}"),
        Path(f"C:/Users/Anshu/anshux/projects/{name}"),
    ]


def find_project(name: str) -> Path | None:
    seen: set[Path] = set()
    for path in _candidate_dirs(name):
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        markers = (".git", "ada_server.py", "index.html")
        if resolved.is_dir() and any((resolved / m).exists() for m in markers):
            return resolved
    for path in _candidate_dirs(name):
        if path.is_dir():
            return path
    return None


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def tcp_open(host: str, port: int, timeout: float = 0.6) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def http_status(url: str, timeout: float = 4.0) -> str:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "ANSHUX-team/1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return str(resp.status)
    except urllib.error.HTTPError as exc:
        return str(exc.code)
    except Exception as exc:  # noqa: BLE001 — board should keep going
        return f"err ({type(exc).__name__})"


def mark(ok: bool) -> str:
    return "ON " if ok else "off"


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("_", " ").replace("/", " ").split())


def resolve_command(text: str) -> str | None:
    n = normalize(text)
    if not n:
        return None
    for key, names in ALIASES.items():
        if n == key or n in names:
            return key
    if "office" in n or "floor" in n or "desk" in n:
        return "office"
    if "site" in n or "semicolon" in n or "cosmos" in n or "punah" in n:
        return "sites"
    if "system" in n or n == "board" or n == "status":
        return "status"
    if "workspace" in n or "continue" in n:
        return "continue"
    return None


def cmd_status() -> int:
    semicolon = find_project("semicolon")
    cosmos = find_project("cosmos")
    ollama = tcp_open("127.0.0.1", 11434)
    ada = tcp_open("127.0.0.1", 8420)
    print("ANSHUX board — systems")
    print("Workspace:", ROOT)
    print()
    print("  OpenCode (ARCH) ", mark(bool(which("opencode"))), which("opencode") or "install: npm install -g opencode-ai")
    print("  Aider           ", mark(bool(which("aider"))), which("aider") or "install: anshux/AIDER_START.md")
    print("  Ollama :11434   ", mark(ollama), "http://127.0.0.1:11434")
    print("  Ada    :8420    ", mark(ada), "python team.py ada")
    print("  Python          ", mark(True), sys.executable)
    print("  Semicolon repo  ", mark(bool(semicolon)), semicolon or "clone next to this folder or projects/semicolon")
    print("  Cosmos repo     ", mark(bool(cosmos)), cosmos or "clone next to this folder or projects/cosmos")
    print("  Cursor rules    ", mark((ROOT / ".cursor" / "rules" / "anshux.mdc").is_file()), ".cursor/rules/")
    print("  Continue        ", mark((ROOT / ".continue" / "config.yaml").is_file()), "type: continue")
    return 0


def cmd_sites() -> int:
    print("Live sites")
    for name, url in SITES:
        print(f"  {http_status(url):>4}  {name:28}  {url}")
    return 0


def _gh_prs(repo: str) -> list[dict]:
    try:
        raw = subprocess.check_output(
            [
                "gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "5",
                "--json", "number,title,url,state",
            ],
            text=True,
            timeout=20,
            stderr=subprocess.DEVNULL,
        )
        rows = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return [{
            "number": "—",
            "title": f"{repo}: {type(exc).__name__}",
            "url": "",
            "state": "n/a",
            "repo": repo.split("/")[-1],
        }]
    for row in rows:
        row["repo"] = repo.split("/")[-1]
    return rows


def collect_office_state() -> dict:
    oc = bool(which("opencode"))
    ollama = tcp_open("127.0.0.1", 11434)
    ada = tcp_open("127.0.0.1", 8420)
    sites = [{"name": n, "url": u, "code": http_status(u)} for n, u in SITES]
    prs = _gh_prs("anshumansribeast-prog/semicolon")
    cosmos_prs = _gh_prs("anshumansribeast-prog/cosmos")
    if cosmos_prs and cosmos_prs[0].get("number") == "—":
        prs.append({
            "number": "live",
            "repo": "cosmos",
            "title": "No GitHub repo access — inspect live cosmos.punah.pro + /back",
            "url": "https://cosmos.punah.pro/",
            "state": "live-only",
        })
    else:
        prs.extend(cosmos_prs)
    desks = [
        {
            "id": "opencode",
            "name": "OpenCode",
            "role": "Architect of the office",
            "task": "Design the floor; inspect Semicolon + Cosmos; assign tasks in the office chat.",
            "status": "on" if oc else "idle",
        },
        {
            "id": "cursor",
            "name": "Cursor",
            "role": "Checker",
            "task": "Check the architect’s drawing; pytest; every loop member is on the floor.",
            "status": "on",
        },
        {
            "id": "aider",
            "name": "Aider",
            "role": "Builder",
            "task": "Restore Ada API + Concepts on Semicolon PR #8",
            "status": "on" if which("aider") else "idle",
        },
        {
            "id": "continue",
            "name": "Continue",
            "role": "Editor chat",
            "task": "Open anshux.code-workspace; follow assigned task",
            "status": "idle",
        },
        {
            "id": "cline",
            "name": "Cline",
            "role": "Optional builder",
            "task": "Help Aider if OpenCode assigns you work. Stay off if unused.",
            "status": "idle",
        },
        {
            "id": "ada",
            "name": "Ada",
            "role": "Semicolon tutor",
            "task": "pages/ada.html — teach only, no git",
            "status": "on" if ada else "idle",
        },
        {
            "id": "beast",
            "name": "Beast",
            "role": "Cosmos tutor",
            "task": "cosmos.punah.pro — astronomy only",
            "status": "idle",
        },
    ]
    assigned = load_assignments()
    for desk in desks:
        extra = assigned.get(desk["id"])
        if extra:
            desk["task"] = extra
            desk["assigned"] = True
    return {
        "updated": _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "architect": "OpenCode",
        "inspector": "OpenCode",
        "loop": "Every office member must have a desk and a task. STATUS LOOP until STOP.",
        "members": [d["id"] for d in desks],
        "ollama": ollama,
        "desks": desks,
        "sites": sites,
        "prs": prs,
        "chat": load_chat()[-40:],
        "assignments": assigned,
    }


def _office_dir() -> Path:
    folder = ROOT / "office"
    folder.mkdir(exist_ok=True)
    return folder


def load_assignments() -> dict:
    path = _office_dir() / "assignments.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def save_assignments(data: dict) -> None:
    (_office_dir() / "assignments.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def assign_task(seat: str, task: str) -> dict:
    seat = seat.lower().strip().replace(" ", "")
    aliases = {"opencod": "opencode", "open": "opencode", "arch": "opencode"}
    seat = aliases.get(seat, seat)
    task = task.strip()
    if not seat or not task:
        raise ValueError("Need a desk id and a task")
    data = load_assignments()
    data[seat] = task
    save_assignments(data)
    write_office_state()
    return data


def load_chat() -> list:
    path = _office_dir() / "chat.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_chat(rows: list) -> None:
    (_office_dir() / "chat.json").write_text(json.dumps(rows[-80:], indent=2), encoding="utf-8")


def architect_chat(text: str) -> dict:
    text = text.strip()
    now = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%H:%M")
    log = load_chat()
    log.append({"who": "you", "text": text, "t": now})
    exe = which("opencode")
    if not exe:
        reply = (
            "Architect queued this. OpenCode is not on PATH "
            "(npm install -g opencode-ai). Loop reminder: every office member "
            "needs a task — assign from this floor."
        )
    else:
        try:
            out = subprocess.check_output(
                [exe, "--model", "ollama/llama3.2:3b", "run", text],
                cwd=str(ROOT),
                timeout=90,
                text=True,
                stderr=subprocess.STDOUT,
            )
            reply = (out or "").strip()[-4000:] or "(empty OpenCode reply)"
        except Exception as exc:  # noqa: BLE001
            reply = f"OpenCode did not answer ({type(exc).__name__}). Message is in the chat log."
    log.append({"who": "opencode", "text": reply, "t": now})
    save_chat(log)
    return {"reply": reply, "chat": load_chat()[-40:]}


def write_office_state() -> Path:
    path = _office_dir() / "state.json"
    path.write_text(json.dumps(collect_office_state(), indent=2), encoding="utf-8")
    return path


class OfficeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "office"), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        return

    def _json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        from command_office.http import handle_get

        if handle_get(self, path):
            return
        if path in {"/", "/office", "/office/", "/index.html"}:
            self.path = "/index.html"
        if path == "/api/office":
            self._json(200, collect_office_state())
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        body = self._read_json()
        from command_office.http import handle_post

        if handle_post(self, path, body):
            return
        if path == "/api/assign":
            try:
                assign_task(str(body.get("seat") or ""), str(body.get("task") or ""))
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
                return
            self._json(200, {"ok": True, "office": collect_office_state()})
            return
        if path == "/api/chat":
            text = str(body.get("text") or "").strip()
            if not text:
                self._json(400, {"ok": False, "error": "empty"})
                return
            result = architect_chat(text)
            self._json(200, {"ok": True, **result, "office": collect_office_state()})
            return
        self._json(404, {"ok": False})


def _open_office_browser(url: str) -> None:
    try:
        if sys.platform == "win32":
            os.startfile(url)  # type: ignore[attr-defined]
        else:
            webbrowser.open(url)
    except OSError:
        print("Open this URL in your browser:", url)


def cmd_office() -> int:
    path = write_office_state()
    print("Office snapshot:", path)
    print("OpenCode is architect: assign tasks on the floor, chat in the panel.")
    print("Loop: every office member (OpenCode, Cursor, Aider, Continue, Cline, Ada, Beast) must have a task.")
    if os.environ.get("ANSHUX_OFFICE_NO_SERVE") or "--snap" in sys.argv:
        print("View:", ROOT / "office" / "index.html")
        return 0
    httpd = None
    port = 8765
    for port in range(8765, 8773):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), OfficeHandler)
            break
        except OSError:
            httpd = None
    if httpd is None:
        print("Could not bind 8765-8772. Close the other office window.")
        return 1
    from command_office.http import boot as boot_command_office

    boot_command_office()
    url = f"http://127.0.0.1:{port}/"
    print()
    print("OFFICE SITE (chat panel is on this page):")
    print(" ", url)
    print("AI COMMAND OFFICE (Commander + agents):")
    print(" ", url + "command/")
    print("Do not double-click index.html. That hides the chat API.")
    print("Leave this window open.")
    print()
    _open_office_browser(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("office closed")
    return 0


def _run(argv: list[str], cwd: Path | None = None) -> int:
    cwd = cwd or ROOT
    print(">", " ".join(argv))
    print("cwd:", cwd)
    try:
        return subprocess.call(argv, cwd=str(cwd))
    except FileNotFoundError:
        print("Not installed:", argv[0])
        return 1


def cmd_opencode() -> int:
    exe = which("opencode")
    if not exe:
        print("OpenCode not on PATH. In PowerShell:")
        print("  npm install -g opencode-ai")
        print("  cd C:\\Users\\Anshu\\anshux")
        print("  python team.py")
        return 1
    return _run([exe, "--model", "ollama/llama3.2:3b"])


def cmd_aider() -> int:
    exe = which("aider")
    conf = ROOT / ".aider.conf.yml"
    if not exe:
        print("Aider not on PATH. See anshux/AIDER_START.md")
        return 1
    args = [exe]
    if conf.is_file():
        args.extend(["--config", str(conf)])
    return _run(args)


def cmd_ada() -> int:
    folder = find_project("semicolon")
    if not folder:
        print("Semicolon folder not found. Put it at ../semicolon or projects/semicolon")
        return 1
    script = folder / "ada_server.py"
    if not script.is_file():
        print("No ada_server.py in", folder)
        return 1
    return _run([sys.executable, str(script)], cwd=folder)


def cmd_jarvis() -> int:
    script = ROOT / "jarvis.py"
    if not script.is_file():
        print("jarvis.py missing")
        return 1
    return _run([sys.executable, str(script)])


def cmd_pytest() -> int:
    return _run([sys.executable, "-m", "pytest", "-q"])


def cmd_start_all() -> int:
    cmd_status()
    print()
    if tcp_open("127.0.0.1", 8420):
        print("Ada already on :8420")
        return 0
    folder = find_project("semicolon")
    if not folder or not (folder / "ada_server.py").is_file():
        print("Ada not started (no semicolon clone). OpenCode still runs from this repo.")
        return 0
    print("Starting Ada in the background…")
    log = ROOT / "_ada_server.log"
    handle = log.open("ab")
    subprocess.Popen(
        [sys.executable, str(folder / "ada_server.py")],
        cwd=str(folder),
        stdout=handle,
        stderr=handle,
    )
    print("Ada log:", log)
    return 0


def cmd_continue() -> int:
    ws = ROOT / "anshux.code-workspace"
    if not ws.is_file():
        print("Missing", ws)
        return 1
    for name in ("cursor", "code"):
        exe = which(name)
        if exe:
            print("Opening Continue work area:", ws)
            return _run([exe, str(ws)])
    print("Open this file in Cursor or VS Code (Continue lives there, not in this prompt):")
    print(" ", ws)
    print("Or double-click open_anshux.bat")
    return 0


def cmd_help() -> int:
    print("Work area prompt — type a sentence or a number.")
    print("  check the sites     ping Semicolon + Cosmos")
    print("  status              board")
    print("  assign aider …      give that desk a task (also in the office UI)")
    print("  office              floor + assign + OpenCode chat")
    print("  opencode            ARCHITECT TUI (office + both sites + PRs)")
    print("  aider / ada / jarvis / pytest / start-all")
    print("  continue            open anshux.code-workspace (Continue in the editor)")
    print("  q                   quit")
    print("Anything else starts OpenCode if it is installed.")
    return 0


def cmd_quit() -> int:
    return 0


MENU = [
    ("status", "Show all systems (board)", cmd_status),
    ("sites", "Ping live Semicolon + Cosmos", cmd_sites),
    ("office", "Open the office floor (see the team)", cmd_office),
    ("opencode", "Start OpenCode (architect of the office)", cmd_opencode),
    ("aider", "Start Aider", cmd_aider),
    ("ada", "Start Ada (Ollama tutor)", cmd_ada),
    ("jarvis", "Start Jarvis voice", cmd_jarvis),
    ("pytest", "Run Jarvis tests", cmd_pytest),
    ("start-all", "Board + start Ada if possible", cmd_start_all),
    ("continue", "Open anshux.code-workspace (Continue)", cmd_continue),
    ("help", "Help", cmd_help),
    ("quit", "Quit", cmd_quit),
]

COMMANDS = {key: fn for key, _, fn in MENU}


def dispatch(text: str) -> int | None:
    """Run a built-in. None means hand off to OpenCode."""
    key = resolve_command(text)
    if key == "quit":
        return 0
    if key and key in COMMANDS:
        return COMMANDS[key]()
    return None


def print_banner() -> None:
    oc = "ON" if which("opencode") else "off"
    ol = "ON" if tcp_open("127.0.0.1", 11434) else "off"
    ada = "ON" if tcp_open("127.0.0.1", 8420) else "off"
    print()
    print("=" * 64)
    print("  ANSHUX work area     ARCHITECT OpenCode     CHECK Cursor")
    print("  Terminal UI like Codex / Claude Code. Type here; stay in this prompt.")
    print("=" * 64)
    print(f"  OpenCode {oc}   Ollama {ol}   Ada {ada}   {ROOT}")
    print("  Try:  office   |   check the sites   |   opencode   |   continue")
    print("  Quit: q")
    print()


def cmd_tui() -> int:
    print_banner()
    cmd_status()
    print()
    cmd_help()
    print()
    while True:
        try:
            line = input("anshux> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if resolve_command(line) == "quit":
            print("bye")
            return 0
        if line.lower().startswith("assign "):
            parts = line.split(None, 2)
            if len(parts) < 3:
                print("assign <desk> <task>   desks: opencode cursor aider continue cline ada beast")
                print()
                continue
            assign_task(parts[1], parts[2])
            print("Assigned", parts[1], "→", parts[2])
            print()
            continue
        result = dispatch(line)
        if result is not None:
            print()
            continue
        exe = which("opencode")
        if exe:
            print("Starting OpenCode (MAIN). Use /models → Ollama, not Claude Sonnet (invalid x-api-key).")
            code = subprocess.call([exe, "--model", "ollama/llama3.2:3b", "run", line], cwd=str(ROOT))
            if code != 0:
                print("OpenCode run failed; opening full TUI. Type your request there.")
                subprocess.call([exe, "--model", "ollama/llama3.2:3b"], cwd=str(ROOT))
            print()
            continue
        print("No built-in for that, and OpenCode is not installed.")
        print("  npm install -g opencode-ai")
        print("  Or type: check the sites | status | help")
        print()
    return 0


def cmd_menu() -> int:
    print_banner()
    cmd_status()
    print()
    for i, (key, label, _) in enumerate(MENU, 1):
        if key in {"help", "quit"}:
            continue
        print(f"  {i}) {key:10} {label}")
    print("  q) quit")
    try:
        choice = input("anshux> ").strip()
    except EOFError:
        return 0
    if not choice or resolve_command(choice) == "quit":
        return 0
    result = dispatch(choice)
    if result is not None:
        return result
    print("Unknown:", choice)
    return 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        if sys.stdin.isatty():
            return cmd_tui()
        return cmd_status()
    if argv[0] in {"menu", "--menu"}:
        return cmd_menu()
    if argv[0] == "assign":
        if len(argv) < 3:
            print("python team.py assign <desk> <task>")
            print("desks: opencode cursor aider continue cline ada beast")
            return 1
        assign_task(argv[1], " ".join(argv[2:]))
        print("Assigned", argv[1], "→", " ".join(argv[2:]))
        return 0
    joined = " ".join(argv)
    if joined in {"-h", "--help", "help"}:
        print(__doc__)
        return cmd_help()
    result = dispatch(joined)
    if result is not None:
        return result
    print("Unknown command:", joined)
    print("Try: python team.py          (work area)")
    print("     python team.py check the sites")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
