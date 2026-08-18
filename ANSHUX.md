# ANSHUX

Project: **ANSHUX**. Product: Jarvis. Semicolon / Cosmos are sister sites.

## Mains (loop until STOP)

**Cursor** and **Codex** are both main. While `AGENT_TASK.md` is not `STATUS: STOP`, they keep working: next open subtask, site check, tests, log, repeat. Only **Anshuman** setting `STATUS: STOP` ends the loop.

## Knowledge sub-agencies (brains)

| Agency | Brain for | File |
| --- | --- | --- |
| **Ada** | Semicolon | `anshux/knowledge/ADA.md` |
| **Beast** | Cosmos | `anshux/knowledge/BEAST.md` |

Ada and Beast do not own STATUS. Mains ask them for site/domain answers.

Optional extra chats: Claude, ChatGPT, Gemini (`anshux/knowledge/`). **Not Claude Code.**

## Subtasks

`anshux/SUBTASKS.md` — a list. Mains pick rows. Not a third implementer.

## Loop

1. Read `AGENT_TASK.md`. If `STOP`, halt.
2. Do open work (sites, bugs, subtasks).
3. Log in `AGENT_LOG.md`.
4. Leave STATUS as `LOOP` (or `BUILD` / `REVIEW`) until Anshuman writes `STOP`.
