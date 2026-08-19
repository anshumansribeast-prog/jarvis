# ANSHUX team (checked 2026-08-19)

How we start:

| Who | How |
| --- | --- |
| **OpenCode** | `python team.py opencode` from `C:\Users\Anshu\anshux`. Auto-reads `AGENTS.md`. |
| **Aider** | `python team.py aider` |
| **Cursor** | Open `anshux.code-workspace`. `.cursor/rules/*.mdc` injects into new chats. |
| **Continue** | Same workspace. Reads `AGENTS.md` + `.continue/rules/anshux.md`. |
| **Ada** | `python team.py ada` |

| Seat | Agent | Role | Status |
| --- | --- | --- | --- |
| **MAIN** | **OpenCode** (terminal) | Implement Semicolon / Jarvis | ON — `anshux/OPENCODE_START.md`. Semicolon PR: https://github.com/anshumansribeast-prog/semicolon/pull/8 |
| **CHECK** | **Cursor** | Board, pytest, live site | ON (this session) |
| **FREE 1** | **Aider + Ollama** | Backup implementer, $0 | Ready: `anshux/AIDER_START.md` |
| **FREE 2** | **Cline + Ollama** | Optional VS Code agent, $0 | Optional |
| **FREE 3** | **Continue + Ollama** | Completions only | Optional |
| Brains | **Ada** / **Beast** | Semicolon / Cosmos knowledge | Docs only |
| Out | Codex, Claude Code | — | Not on the team |

Prefer the open PR #8, then fix it (see below). One branch for Semicolon.

## Semicolon PR #8 — Cursor check (do not merge yet)

https://github.com/anshumansribeast-prog/semicolon/pull/8 — *Remove the Code Generator and make Ada usable on phones*

**Good:** Deletes Generator pages/JS and Practice `#tabGen` / `#modeGen`. Adds mobile Ada CSS (16px, tall textarea). Cache-bust `?v=20260818a`.

**Too much deleted (bugs):**

- `js/ada-api.js` and `/api/ada` wiring — **Ada chat will break**
- `ada_knowledge.py`
- `pages/concepts.html` and Concepts nav (existed before Generator)
- `img/ada.jpg`

**OpenCode next:** keep Generator gone; **restore** `js/ada-api.js`, Ada `POST /api/ada`, Concepts page + nav, `img/ada.jpg`. Paste `anshux/OPENCODE_TASK.md`. Then Cursor re-checks the live site.

Loop board: **`anshux/LOOP.md`**. Every seat has a task. Cursor checks idle vs done. OpenCode stays MAIN until `AGENT_TASK.md` is `STOP`.
