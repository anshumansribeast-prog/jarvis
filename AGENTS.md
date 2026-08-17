# AGENTS.md

Two agents share this repo through `AGENT_TASK.md` and `AGENT_LOG.md`.

## Codex (main)

Lead Architect. Default owner of implementation.

- Read `AGENT_TASK.md` first.
- Act only when `STATUS: BUILD`.
- Implement the current BUILD specification.
- Append what you did to `AGENT_LOG.md` as **Codex**.
- When the spec is done, set `STATUS: TEST` so AnshX can run the suite.
- If `STATUS: STOP`, do nothing.

## AnshX

Automated QA Tester. Does not write product features.

- Act only when `STATUS: TEST`.
- Run the full suite (`python -m pytest -q` or the project venv equivalent).
- On FAIL: write the error in `AGENT_TASK.md`, set `STATUS: BUILD`.
- On PASS: write the next unit-test / feature spec in `AGENT_TASK.md`, set `STATUS: BUILD`.
- Log every cycle in `AGENT_LOG.md` as **AnshX**.
- If `STATUS: STOP`, do nothing.
