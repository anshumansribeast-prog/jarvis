# ANSHUX

Project name: **ANSHUX**

Jarvis is the voice-assistant product in this repo. **ANSHUX** is the agent team around it.

There is **no Claude Code** agent. “Claude” means normal Claude (claude.ai / Claude chat), not the terminal CLI.

```
                    ANSHUX
                      │
        ┌─────────────┴─────────────┐
        │         MAINS              │         KNOWLEDGE (chat only)
        ▼                           ▼              ▼
     Cursor                       Codex      Claude · ChatGPT · Gemini
     plan, code, test             code, review, sites     answers / drafts
```

## Mains

**Cursor** and **Codex** are both main. Either may PLAN, BUILD, TEST, or check Semicolon/Cosmos. Log as **Cursor** or **Codex**.

## Knowledge (not mains)

**Claude**, **ChatGPT**, and **Gemini** answer questions and draft text. They do not own `STATUS`, do not merge code, and do not run pytest unless a main pastes a question to them.

## Subtasks

`anshux/SUBTASKS.md` is a list, not a third agent. Mains pick rows. Knowledge agents may comment; they do not mark rows DONE.

## Loop

1. PLAN — a main writes `AGENT_TASK.md`, sets `STATUS: BUILD` or `REVIEW`.
2. BUILD / REVIEW — Cursor and/or Codex do the work.
3. TEST — Cursor or Codex runs pytest. Fail → BUILD. Pass → next PLAN or STOP.
4. STOP — nobody acts.

Do not request manual verification.
