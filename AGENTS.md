# AGENTS.md

Team name: **Anshux**. Control files: `AGENT_TASK.md`, `AGENT_LOG.md`.

## Anshux (main) — Cursor

Main agent. Runs in Cursor (Cloud or desktop). Owns this repo’s TEST/BUILD loop.

- Read `AGENT_TASK.md` first.
- On `STATUS: BUILD`: implement the spec (or hand it to Claude Code), log as **Anshux**, then set `STATUS: TEST`.
- On `STATUS: TEST`: run `python -m pytest -q` (or the project venv). FAIL → `STATUS: BUILD` with errors. PASS → next spec and `STATUS: BUILD`, or `STATUS: STOP`.
- On `STATUS: STOP`: do nothing.

## Claude Code

Co-architect. Same BUILD rights as Anshux; not the main agent.

- Act on `STATUS: BUILD` when Anshux has not already claimed the spec.
- Implement the current BUILD specification.
- Log as **Claude Code**.
- Set `STATUS: TEST` when done so Anshux can run QA.
- On `STATUS: STOP`: do nothing.

Jarvis can launch Claude Code on Windows (`wt.exe` + `claude`) for interactive coding. That launch does not send commands; Anshuman types them.

## Codex

Co-architect helper. Not main.

- Act on `STATUS: BUILD` only if Anshux and Claude Code are not already implementing.
- Log as **Codex**.
- Set `STATUS: TEST` when done.
