# Get started with OpenCode (MAIN)

**OpenCode** is the terminal coding agent for ANSHUX. It replaces Codex. It auto-reads `AGENTS.md` (same idea as Codex). Extra files: `opencode.json` → `TEAM.md` + `.team/opencode.md`.

Docs: [opencode.ai/docs](https://opencode.ai/docs/)

## Why it is a good fit

- Open source TUI, not ChatGPT Codex Cloud (no Codex quota).
- Reads this repo’s `AGENTS.md` on start.
- Can use the **Ollama** you already run for Ada/Jarvis (`opencode.json` points at `127.0.0.1:11434`).
- Same job as Codex: implement Semicolon/Jarvis; Cursor checks.

Caveat: a small local model (`llama3.2:3b`) is weaker than paid Codex. Prefer `qwen2.5-coder:7b` if RAM allows, or `/connect` a paid provider later.

## 1. Install (Windows)

npm (simplest if Node is installed):

```powershell
npm install -g opencode-ai
```

Or Chocolatey / Scoop: `choco install opencode` / `scoop install opencode`

## 2. Ollama running

```powershell
ollama list
curl http://127.0.0.1:11434/api/version
```

## 3. Start

```powershell
cd C:\Users\Anshu\anshux
opencode
```

In the TUI: `/models` → pick **Ollama** `llama3.2:3b` or `qwen2.5-coder:7b`. Do **not** run `/init` in a way that overwrites the existing `AGENTS.md`.

## 4. First task

Paste `anshux/OPENCODE_TASK.md` (restore Ada API on Semicolon PR #8; keep Generator gone).
