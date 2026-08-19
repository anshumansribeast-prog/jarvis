# Free coding agents

**MAIN is OpenCode** (`anshux/OPENCODE_START.md`). Codex is off the team. Other **$0** options for ANSHUX (Jarvis + Semicolon + Cosmos), ranked for *this* laptop: you already run **Ollama**.

## Use these (best fit)

| Rank | Agent | Cost | Why it fits |
| --- | --- | --- | --- |
| 1 | **OpenCode** + Ollama | Free | Terminal agent like Codex. Reads `AGENTS.md`. Wired in `opencode.json`. |
| 2 | **Aider** + Ollama | Free | Terminal, git-aware, edits Python/HTML/JS like Semicolon. Same Ollama as Ada/Jarvis. |
| 3 | **Cline** (VS Code) + Ollama | Free | Closest *agent* feel in a sidebar: plan, edit files, run commands. You approve diffs. |
| 4 | **Continue** (VS Code) + Ollama | Free | Completions + chat in the editor. Weaker as a full agent. |
| 5 | **GitHub Copilot Free** | Free tier | If you qualify as student / teacher / OSS maintainer: [education.github.com](https://education.github.com). |
| 6 | **Cursor Hobby** | Free tier | You already use Cursor here (CHECK seat). |

## Do not count on (for this team)

- **Codex / Codex Cloud** — removed from ANSHUX.
- **Claude Code** — paid; not in ANSHUX.
- **Old Gemini CLI “1000/day”** — Google ended consumer Gemini CLI / Code Assist individuals on **18 Jun 2026**.

## Getting started: OpenCode (MAIN)

Full steps: **`anshux/OPENCODE_START.md`**.

```powershell
npm install -g opencode-ai
cd C:\Users\Anshu\anshux
opencode
```

## Getting started: Aider (backup)

Full steps: **`anshux/AIDER_START.md`**.

```powershell
python -m pip install aider-install
aider-install
setx OLLAMA_API_BASE http://127.0.0.1:11434
```

New PowerShell window:

```powershell
cd C:\Users\Anshu\anshux
aider --config .aider.conf.yml
```

Prefer `ollama_chat/qwen2.5-coder:7b` if you ran `ollama pull qwen2.5-coder:7b`. Then paste `anshux/OPENCODE_TASK.md`.

## Sources (web, Aug 2026)

- [OpenCode](https://opencode.ai/docs/) — OSS terminal coding agent  
- [Aider](https://github.com/Aider-AI/aider) — OSS CLI pair programmer  
- [Cline](https://github.com/cline/cline) — OSS VS Code agent  
- [Continue](https://github.com/continuedev/continue) — OSS IDE assistant  
