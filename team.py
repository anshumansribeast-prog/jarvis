#!/usr/bin/env python3
"""ANSHUX terminal work area (Codex / Claude Code style).

  python team.py                 work area prompt (stays open)
  python team.py check the sites
  python team.py sites
  python team.py opencode
  python team.py menu            numbered list (old)
"""

from __future__ import annotations

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
    print("  OpenCode (MAIN) ", mark(bool(which("opencode"))), which("opencode") or "install: npm install -g opencode-ai")
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
    print("  opencode            MAIN agent TUI (Codex-style)")
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
    ("opencode", "Start OpenCode (MAIN)", cmd_opencode),
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
    print("  ANSHUX work area          MAIN OpenCode     CHECK Cursor")
    print("  Terminal UI like Codex / Claude Code. Type here; stay in this prompt.")
    print("=" * 64)
    print(f"  OpenCode {oc}   Ollama {ol}   Ada {ada}   {ROOT}")
    print("  Try:  check the sites   |   status   |   opencode   |   continue")
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
        result = dispatch(line)
        if result is not None:
            print()
            continue
        exe = which("opencode")
        if exe:
            print("Starting OpenCode (MAIN) with that prompt…")
            code = subprocess.call([exe, "run", line], cwd=str(ROOT))
            if code != 0:
                print("OpenCode run failed; opening full TUI. Type your request there.")
                subprocess.call([exe], cwd=str(ROOT))
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
