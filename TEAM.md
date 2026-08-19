# TEAM.md

ANSHUX team. Codex auto-reads this file and `AGENTS.md` from `C:\Users\Anshu\anshux`.

| Who | How you start | Role |
| --- | --- | --- |
| **Codex** (MAIN) | `cd C:\Users\Anshu\anshux` then run Codex in the terminal. Reads `AGENTS.md` + `TEAM.md`. | Implement |
| **Aider** | `aider --config .aider.conf.yml` — loads `.team/aider.md` | Free implementer (Ollama) |
| **Cursor** (CHECK) | Open this folder — `.cursor/rules/*.mdc` injects into every chat | Tests, live site |
| **Continue** | Open `anshux.code-workspace` — Continue uses `.continue/rules/` + `AGENTS.md` | Completions / chat |
| **Ada** | `python ada_server.py` from `projects\semicolon` or `C:\Users\Anshu\semicolon` (Ollama) | Semicolon brain |

Do not rebuild the Code Generator. Semicolon PR #8: restore `js/ada-api.js`, Concepts, `img/ada.jpg` before merge. Loop until `AGENT_TASK.md` is `STATUS: STOP`.
