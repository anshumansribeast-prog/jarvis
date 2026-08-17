# ANSHUX

Project name: **ANSHUX**

Jarvis (the voice assistant in this repo) is the product. **ANSHUX** is the agent system that builds and tests it.

```
                 ┌─────────────┐
                 │   ANSHUX    │
                 │  (project)  │
                 └──────┬──────┘
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     Cursor         Claude Code      Codex
   orchestrator    MAIN implementer  SUB implementer
   PLAN + TEST         BUILD            SUBTASKS
```

## Loop

1. **PLAN** — Cursor writes the spec in `AGENT_TASK.md`, splits **Main** vs **Sub**, sets `STATUS: BUILD`.
2. **BUILD** — Claude Code implements the Main spec. Codex implements only items in `anshux/SUBTASKS.md`. When both are done, Claude Code sets `STATUS: TEST`.
3. **TEST** — Cursor runs pytest. Fail → `BUILD` with logs. Pass → next PLAN or `STOP`.
4. **STOP** — nobody acts.

Do not request manual verification. Log every action in `AGENT_LOG.md` with the agent name.

## Who does what

| Role | Agent | Files to read first |
| --- | --- | --- |
| Orchestrator | Cursor | `AGENT_TASK.md`, then `AGENTS.md` |
| Main implementer | Claude Code | `CLAUDE.md`, then `AGENT_TASK.md` |
| Sub implementer | Codex | `anshux/SUBTASKS.md`, then `AGENT_TASK.md` |

Claude Code never waits for Codex if the Main spec can ship alone. Codex never takes Main work. Cursor does not implement BUILD while Claude Code is the assigned main implementer.
