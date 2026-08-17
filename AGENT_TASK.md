# AGENT_TASK

MAIN AGENT: Codex
QA AGENT: AnshX

STATUS: BUILD

## Roles

| Agent | Role | When to act |
| --- | --- | --- |
| **Codex** (main) | Lead Architect | `STATUS: BUILD` — implement the spec below, then set `STATUS: TEST` |
| **AnshX** | Automated QA Tester | `STATUS: TEST` — run the full pytest suite, then `STATUS: BUILD` (fail or next spec) or `STATUS: STOP` |

Codex is the default owner of this file. AnshX never implements product code; Codex never runs the TEST cycle.

Halt only when `STATUS: STOP`. Do not request manual verification.

## Current objective (Codex)

Windows-only integration tests for `window_controller` (minimize / maximize / restore / switch_to / show_desktop) and `system_controller` (volume keys, screenshot via ImageGrab). Those modules need pywin32 and a real desktop session.

If this environment is Linux (no pywin32 / no desktop), skip live window/system calls: add `pytest.mark.skipif(sys.platform != "win32")` tests that document the intended behavior, keep the existing 36 Linux tests green, then set `STATUS: TEST` for AnshX.

## Last test run (AnshX)

- Command: `/tmp/jarvis-test-venv/bin/python -m pytest -v --tb=short`
- Result: PASS
- Timestamp: 2026-08-17T17:57:00Z
- Counts: 36 passed in 0.17s

```
tests/test_app_controller.py .....
tests/test_file_controller.py ........
tests/test_is_speech.py ..
tests/test_jarvis_commands.py ..............
tests/test_memory_controller.py .......
```
