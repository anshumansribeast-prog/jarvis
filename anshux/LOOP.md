# ANSHUX loop — roles and tasks (no idle)

**STATUS: LOOP** until a human sets `AGENT_TASK.md` to `STOP`.
**Nobody sits idle.** See the floor: `python team.py office` (opens the office).

**OpenCode is inspection in charge** of **both** sites and **both** PR streams (Semicolon + Cosmos).
**Cursor checks the office** (that OpenCode inspected, pytest, this board).
**Aider implements** Semicolon restores.

| Desk | Agent | Role | Task now | Cursor check |
| --- | --- | --- | --- | --- |
| Inspector | **OpenCode** | Sites + PRs in charge | Inspect live Semicolon and Cosmos. Review Semicolon PR #8 and Cosmos PRs (or live-only if no repo). Paste `anshux/OPENCODE_TASK.md`. Ollama, not Claude. | Must inspect both. Office wall shows URLs + PRs. |
| Check | **Cursor** | Office check | Confirm inspector; pytest; refresh `office/state.json`. | This cycle: pytest + live pings + office snapshot. |
| Build | **Aider** | Implementer | Restore Ada API + Concepts + ada.jpg on PR #8. Keep Generator gone. `anshux/AIDER_TASK.md`. | IDLE until `python team.py aider`. |
| Editor | **Continue** | Sidebar chat | `anshux.code-workspace`. | IDLE until workspace open. |
| Optional | **Cline** | Extra implementer | Same as Aider if Aider is off. | IDLE. |
| Tutor | **Ada** | Semicolon brain | Chat only. `anshux/ADA_TASK.md`. | Ada page live 200. |
| Tutor | **Beast** | Cosmos brain | Astronomy only. `anshux/BEAST_TASK.md`. | Cosmos + /back live 200. |
| Out | Codex, Claude Code | — | Off. | — |

## Inspector checklist (OpenCode)

- Semicolon home, Ada, Concepts, Generator (want Generator 404 later)
- PR https://github.com/anshumansribeast-prog/semicolon/pull/8 — do not merge if Ada API/Concepts/ada.jpg are deleted
- Cosmos home + `/back`
- Cosmos open PRs if the repo exists; otherwise live-only

## Cursor check 2026-08-19T08:32Z

| Probe | Result |
| --- | --- |
| Office | `office/index.html` + `python team.py office` |
| Jarvis pytest | run this cycle |
| generate.html | still 200 (not done) |
| Semicolon PR #8 | OPEN — over-deletes Ada API |
| Cosmos GitHub PRs | no `anshumansribeast-prog/cosmos` from this token — inspect **live** Cosmos |

```powershell
cd C:\Users\Anshu\anshux
python team.py office
python team.py
```

At `anshux>`: `office` then `opencode`.
