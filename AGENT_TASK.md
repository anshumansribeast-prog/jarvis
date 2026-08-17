# AGENT_TASK

PROJECT: ANSHUX
STATUS: BUILD

ORCHESTRATOR: Cursor
MAIN IMPLEMENTER: Claude Code
SUB IMPLEMENTER: Codex

## Main spec (Claude Code)

Add Linux-safe tests that document Windows window control, skipped on non-Windows:

- File: `tests/test_window_controller.py`
- `pytest.mark.skipif(sys.platform != "win32", reason="pywin32 / desktop session")`
- Cover: `minimize_active_window`, `maximize_active_window`, `restore_active_window`, `show_desktop`, `switch_to` (found vs missing title)
- Mock `win32gui` / `win32api` so the module can be imported; on `win32` the skip is not used and mocks still isolate the desktop
- Do not break the existing 36 Linux tests

When this file exists and pytest still passes on Linux, Main is done.

## Sub spec (Codex)

See `anshux/SUBTASKS.md`. Codex owns `tests/test_system_controller.py` only.

## Last test run (Cursor)

- PASS — 36 tests — 2026-08-17T17:57:00Z
- `/tmp/jarvis-test-venv/bin/python -m pytest -v --tb=short`
