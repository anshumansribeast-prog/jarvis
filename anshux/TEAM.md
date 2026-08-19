# ANSHUX team (checked 2026-08-19)

How we start (Codex's layout, wired in this repo):

| Who | How |
| --- | --- |
| **Codex** | `cd C:\Users\Anshu\anshux` then `codex`. Auto-reads `AGENTS.md` + `TEAM.md`. |
| **Aider** | Same folder: `aider --config .aider.conf.yml`. Role card: `.team/aider.md`. |
| **Cursor** | Open this folder. `.cursor/rules/*.mdc` injects into new chats. |
| **Continue** | Open `anshux.code-workspace`. Reads `AGENTS.md` + `.continue/rules/anshux.md`. |
| **Ada** | `cd C:\Users\Anshu\semicolon` (or `projects\semicolon`) then `python ada_server.py`. Ollama. |

Codex is running in the **terminal** and as Cloud. This is the roster Cursor verified.

| Seat | Agent | Role | Status |
| --- | --- | --- | --- |
| **MAIN** | **Codex** (terminal + Cloud) | Implement Semicolon / Jarvis | ON — new account. Cloud: task_e_6a8542fc5b5c832598c087710241dfcf. Semicolon PR: https://github.com/anshumansribeast-prog/semicolon/pull/8 |
| **CHECK** | **Cursor** | Board, pytest, live site | ON (this session) |
| **FREE 1** | **Aider + Ollama** | Backup implementer, $0 | Ready: `anshux/AIDER_START.md` |
| **FREE 2** | **Cline + Ollama** | Optional VS Code agent, $0 | Optional |
| **FREE 3** | **Continue + Ollama** | Completions only | Optional |
| Brains | **Ada** / **Beast** | Semicolon / Cosmos knowledge | Docs only |
| Out | Claude Code, paid Codex extra seats | — | Not on the team |

If Codex terminal and Cloud both edit Semicolon, use **one** branch. Prefer the open PR #8, then fix it (see below).

## Codex PR #8 — Cursor check (do not merge yet)

https://github.com/anshumansribeast-prog/semicolon/pull/8 — *Remove the Code Generator and make Ada usable on phones*

**Good:** Deletes Generator pages/JS and Practice `#tabGen` / `#modeGen`. Adds mobile Ada CSS (16px, tall textarea). Cache-bust `?v=20260818a`.

**Too much deleted (bugs):**

- `js/ada-api.js` and `/api/ada` wiring — **Ada chat will break**
- `ada_knowledge.py`
- `pages/concepts.html` and Concepts nav (existed before Generator)
- `img/ada.jpg`

**Codex next (terminal):** keep Generator gone; **restore** `js/ada-api.js`, Ada `POST /api/ada`, Concepts page + nav, `img/ada.jpg`. Then Cursor re-checks the live site.

Free agents do not own STATUS. Codex remains MAIN until `AGENT_TASK.md` is `STOP`.
