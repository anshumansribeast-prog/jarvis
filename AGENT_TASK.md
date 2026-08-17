# AGENT_TASK

MAIN AGENT: Anshux
RUNTIME: Cursor
CO-AGENTS: Claude Code, Codex

STATUS: BUILD

## Roles

| Agent | Runtime | Role | When to act |
| --- | --- | --- | --- |
| **Anshux** (main) | Cursor | Lead Architect + QA owner | Always the default. On `BUILD`, implement (or assign Claude Code). On `TEST`, run pytest. |
| **Claude Code** | Claude Code CLI / Windows Terminal | Co-architect | `STATUS: BUILD` — implement the spec, log as Claude Code, then set `STATUS: TEST` for Anshux |
| **Codex** | OpenAI Codex | Co-architect (not main) | `STATUS: BUILD` only if Anshux or Claude Code is not already implementing |

Anshux is the name of the main agent. Cursor is how Anshux runs. Claude Code is also on the team and may implement BUILD work. Codex is a helper, not the main agent.

Halt only when `STATUS: STOP`. Do not request manual verification.

## Current objective (Anshux / Claude Code)

Windows-only integration tests for `window_controller` (minimize / maximize / restore / switch_to / show_desktop) and `system_controller` (volume keys, screenshot via ImageGrab). Those modules need pywin32 and a real desktop session.

If this environment is Linux (no pywin32 / no desktop), skip live window/system calls: add `pytest.mark.skipif(sys.platform != "win32")` tests that document the intended behavior, keep the existing 36 Linux tests green, then set `STATUS: TEST`.

## Last test run

- Agent: Anshux (legacy log name AnshX)
- Command: `/tmp/jarvis-test-venv/bin/python -m pytest -v --tb=short`
- Result: PASS
- Timestamp: 2026-08-17T17:57:00Z
- Counts: 36 passed in 0.17s
