# ANSHUX board

**Desktop icon (Windows):** double-click `make_desktop_icon.bat` once. That puts **ANSHUX** on the Desktop.

## Deploy the office on a server

Full guide for Abhishek / ops: **[`DEPLOY.md`](DEPLOY.md)**

```bash
git clone https://github.com/anshumansribeast-prog/jarvis.git
cd jarvis
git checkout cursor/anshx-qa-loop-8b8a   # or main after merge
./scripts/deploy-office.sh
# → http://SERVER_IP:8765/
```

Also: `scripts/anshux-office.service` (systemd), `scripts/nginx-office.conf`, `Dockerfile.office`.  
Ship mail default: **abhiis@eleven11.pro**.

---

**Office site (chat panel lives here, not on punah.pro):** double-click `office.bat` or:

```powershell
cd C:\Users\Anshu\anshux
python team.py office
```

Leave that window open. Then on **that same computer** open **http://127.0.0.1:8765/**

That one page is Commander chat, OpenCode chat, office floor, agents, and tasks. `/command/` is the same page. Those links are not the internet. They only work while `team.py office` is running on your PC. They are not semicolon.punah.pro. Do not open `office\index.html` by double-click; that skips the chat API.

On the office page you can **assign a task** to any desk and **chat with OpenCode**. Or:

```powershell
python team.py assign aider Restore Ada API on PR 8
```

LOOP: every member (OpenCode, Cursor, Aider, Continue, Cline, Ada, Beast) must have a desk and a task.

In a terminal (no spaces in `team.py`):

```powershell
python team.py
```

At `anshux>` type `office` or `opencode` (OpenCode is **architect of the office**).

You get an `anshux>` prompt that stays open (like Codex / Claude Code). Type:

```
check the sites
status
opencode
continue
q
```

Wrong: `python team . py` — that looks for a file named `team. py`.

**Continue** is the VS Code extension. At `anshux>` type `continue` (opens `anshux.code-workspace`). Or double-click `open_anshux.bat`.

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
