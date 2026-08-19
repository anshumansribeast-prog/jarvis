# ANSHUX board

**Desktop icon (Windows):** double-click `make_desktop_icon.bat` once. That puts **ANSHUX** on the Desktop. Double-click it to open the work area.

In a terminal, type this **with no spaces in the filename**:

```powershell
cd C:\Users\Anshu\anshux
python team.py
```

Wrong: `python team . py` — Python then looks for a file named `team. py` and fails.

Open **`anshux.code-workspace`** (or `open_anshux.bat`). You should see:

- **ANSHUX-board** — this repo (commands live here)
- **team-cards** — `.team/` role files
- **semicolon** / **cosmos** — sister sites if they sit next to this folder

On open, the **ANSHUX: board** task prints what is ON/off (Ollama, Ada, OpenCode, Aider, clones).

## Give commands from here

| Do this | How |
| --- | --- |
| See every system | `python team.py status`  or  **Terminal → Run Task → ANSHUX: board** |
| Menu (type a number) | `python team.py`  or  Run Task **ANSHUX: command menu** |
| OpenCode (MAIN) | `python team.py opencode` |
| Aider | `python team.py aider` |
| Ada (Ollama tutor) | `python team.py ada` |
| Jarvis | `python team.py jarvis` |
| Tests | `python team.py pytest` |
| Live sites | `python team.py sites` |
| Board + start Ada | `python team.py start-all` |

Continue (VS Code chat) loads when this workspace is open. Cursor rules inject from `.cursor/rules/`. Codex is not on the team.

Paste for OpenCode: `anshux/OPENCODE_TASK.md`.
