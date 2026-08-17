# ANSHUX subtasks — Codex only

STATUS of parent board: see `AGENT_TASK.md` (`BUILD` / `TEST` / `STOP`).

Codex implements **open** rows. Do not edit Claude Code’s Main spec files.

| ID | State | File | Work |
| --- | --- | --- | --- |
| SUB-1 | OPEN | `tests/test_system_controller.py` | `skipif` not Windows. Cover `volume_up`, `volume_down`, `mute`, `take_screenshot` (mock ImageGrab / win32 keybd). No real volume or screenshot side effects. |

When SUB-1 is done: set State to `DONE`, log as **Codex** in `AGENT_LOG.md`. Do not set `STATUS: TEST`.
