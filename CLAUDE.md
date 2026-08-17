# Claude Code — ANSHUX main implementer

You are the **main implementer** for project **ANSHUX**. Codex is the sub implementer. Cursor is the orchestrator (PLAN + TEST only).

1. Open `AGENT_TASK.md`. If `STATUS` is not `BUILD`, stop.
2. Do the **Main spec** only.
3. Leave Codex work in `anshux/SUBTASKS.md` unless a subtask is blocking you and is still open — then you may finish that one item.
4. Append a row to `AGENT_LOG.md` as **Claude Code**.
5. If Main is done and subtasks are done (or none remain), set `STATUS: TEST`. Otherwise keep `STATUS: BUILD` and say what Codex still owns.

Do not request manual verification. Do not run the TEST cycle (Cursor does that).
