#!/usr/bin/env python3
"""ANSHUX command hub — see every system and start teammates from here.

  python team.py           interactive menu
  python team.py status    board (what is up)
  python team.py opencode  MAIN terminal agent
  python team.py aider
  python team.py ada
  python team.py jarvis
  python team.py pytest
  python team.py sites
  python team.py start-all status + Ada (if Semicolon found)
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
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


def cmd_status() -> int:
    semicolon = find_project("semicolon")
    cosmos = find_project("cosmos")
    ollama = tcp_open("127.0.0.1", 11434)
    ada = tcp_open("127.0.0.1", 8420)
    print("ANSHUX board — systems")
    print("Workspace:", ROOT)
    print()
    print("  OpenCode (MAIN) ", mark(bool(which("opencode"))), which("opencode") or "install: anshux/OPENCODE_START.md")
    print("  Aider           ", mark(bool(which("aider"))), which("aider") or "install: anshux/AIDER_START.md")
    print("  Ollama :11434   ", mark(ollama), "http://127.0.0.1:11434")
    print("  Ada    :8420    ", mark(ada), "python ada_server.py")
    print("  Python          ", mark(True), sys.executable)
    print("  Semicolon repo  ", mark(bool(semicolon)), semicolon or "clone next to this folder or projects/semicolon")
    print("  Cosmos repo     ", mark(bool(cosmos)), cosmos or "clone next to this folder or projects/cosmos")
    print("  Cursor rules    ", mark((ROOT / ".cursor" / "rules" / "anshux.mdc").is_file()), ".cursor/rules/")
    print("  Continue        ", mark((ROOT / ".continue" / "config.yaml").is_file()), "open anshux.code-workspace")
    print()
    print("Commands from this folder:")
    print("  python team.py opencode | aider | ada | jarvis | pytest | sites")
    print("  Cursor/VS Code: Terminal > Run Task…")
    print("  Open the work area:  anshux.code-workspace   or   open_anshux.bat")
    return 0


def cmd_sites() -> int:
    print("Live sites")
    for name, url in SITES:
        print(f"  {http_status(url):>4}  {name:28}  {url}")
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
        print("OpenCode not on PATH. Install: npm install -g opencode-ai")
        print("Then: cd", ROOT, "&& opencode")
        return 1
    return _run([exe])


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
        print("Ada not started (no semicolon clone). OpenCode/Aider still run from this repo.")
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
    print("Interactive agents (new terminals): python team.py opencode   and   python team.py aider")
    return 0


MENU = [
    ("status", "Show all systems (board)", cmd_status),
    ("sites", "Ping live Semicolon + Cosmos", cmd_sites),
    ("opencode", "Start OpenCode (MAIN)", cmd_opencode),
    ("aider", "Start Aider", cmd_aider),
    ("ada", "Start Ada (Ollama tutor)", cmd_ada),
    ("jarvis", "Start Jarvis voice", cmd_jarvis),
    ("pytest", "Run Jarvis tests", cmd_pytest),
    ("start-all", "Board + start Ada if possible", cmd_start_all),
]


def cmd_menu() -> int:
    cmd_status()
    print()
    for i, (key, label, _) in enumerate(MENU, 1):
        print(f"  {i}) {key:10} {label}")
    print("  q) quit")
    try:
        choice = input("Command number or name: ").strip().lower()
    except EOFError:
        return 0
    if not choice or choice in {"q", "quit", "exit"}:
        return 0
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(MENU):
            return MENU[idx][2]()
    for key, _, fn in MENU:
        if key == choice:
            return fn()
    print("Unknown:", choice)
    return 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        if sys.stdin.isatty():
            return cmd_menu()
        return cmd_status()
    cmd = argv[0]
    for key, _, fn in MENU:
        if key == cmd:
            return fn()
    if cmd in {"-h", "--help", "help"}:
        print(__doc__)
        return 0
    print("Unknown command:", cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
