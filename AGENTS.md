# AGENTS.md

**ANSHUX** project. Cursor orchestrates. Claude Code is the main implementer. Codex is the sub implementer.

Read `ANSHUX.md` for the loop. Live work lives in `AGENT_TASK.md`.

## Cursor (orchestrator)

- `STATUS: PLAN` or empty spec: write Main (Claude Code) and Sub (Codex) work, set `STATUS: BUILD`.
- `STATUS: TEST`: run `python -m pytest -q`. Fail → `STATUS: BUILD` with errors. Pass → next PLAN or `STATUS: STOP`.
- `STATUS: BUILD`: do **not** implement unless both Claude Code and Codex are unavailable. Assign only.
- Log as **Cursor**.

## Claude Code (main implementer)

- Act when `STATUS: BUILD`.
- Implement **Main spec** in `AGENT_TASK.md` only. Do not take Codex subtasks unless `anshux/SUBTASKS.md` says they are unblocked and idle.
- Log as **Claude Code**.
- When Main is done, if subtasks are still open, leave `STATUS: BUILD` and note that in `AGENT_TASK.md`. When Main and Sub are done, set `STATUS: TEST`.
- `STATUS: STOP`: do nothing.

## Codex (sub implementer)

- Act when `STATUS: BUILD` **and** `anshux/SUBTASKS.md` has open items.
- Implement only those subtasks. Never rewrite the Main spec or take Claude Code’s files unless a subtask names them.
- Mark each subtask done in `anshux/SUBTASKS.md`. Log as **Codex**.
- Do not set `STATUS: TEST` (Claude Code or Cursor does that after Main is done).
- `STATUS: STOP`: do nothing.
