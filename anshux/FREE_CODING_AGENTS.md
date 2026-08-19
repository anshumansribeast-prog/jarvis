# Free coding agents (Codex quota used up)

Codex Cloud free limit is hit. Use these **$0** options for ANSHUX (Jarvis + Semicolon + Cosmos). Ranked for *this* laptop: you already run **Ollama**.

## Use these (best fit)

| Rank | Agent | Cost | Why it fits |
| --- | --- | --- | --- |
| 1 | **Aider** + Ollama | Free | Terminal, git-aware, edits Python/HTML/JS like Semicolon. Same Ollama as Ada/Jarvis. |
| 2 | **Cline** (VS Code) + Ollama | Free | Closest *agent* feel to Codex: plan, edit files, run commands. You approve diffs. |
| 3 | **Continue** (VS Code) + Ollama | Free | Completions + chat in the editor. Weaker as a full agent. |
| 4 | **GitHub Copilot Free** | Free tier | If you qualify as student / teacher / OSS maintainer: [education.github.com](https://education.github.com). Limited premium requests on the public free plan. |
| 5 | **Cursor Hobby** | Free tier | You already use Cursor here. Stay on the free/hobby allowance when Cloud Codex is empty. |

Skip paying Codex until you want Cloud PRs again.

## Do not count on (for free)

- **Codex Cloud** — your free limit is done.
- **Claude Code** — paid; not in ANSHUX.
- **Old Gemini CLI “1000/day”** — Google ended consumer Gemini CLI / Code Assist individuals on **18 Jun 2026**. Replacement is **Antigravity**; quota is tighter and not a Codex clone. Try only if you already have a Google account and it still offers a free Antigravity slice: [Google I/O / Antigravity CLI note](https://developers.googleblog.com/en/an-important-update-transitioning-gemini-cli-to-antigravity-cli/).

## Getting started: Aider (do this)

Full steps: **`anshux/AIDER_START.md`**.

```powershell
python -m pip install aider-install
aider-install
setx OLLAMA_API_BASE http://127.0.0.1:11434
```

New PowerShell window:

```powershell
cd C:\Users\Anshu\semicolon
aider --model ollama_chat/llama3.2:3b
```

Prefer `ollama_chat/qwen2.5-coder:7b` if you ran `ollama pull qwen2.5-coder:7b`. Then paste `anshux/CODEX_CLOUD_TASK.md`.

## Cline (optional)

Only if you want a VS Code sidebar instead of the terminal. Same Ollama. See the previous Cline section in git history or Cline’s docs — Aider is the default for ANSHUX now.

## Sources (web, Aug 2026)

- [Aider](https://github.com/Aider-AI/aider) — OSS CLI pair programmer  
- [Cline](https://github.com/cline/cline) — OSS VS Code agent  
- [Continue](https://github.com/continuedev/continue) — OSS IDE assistant  
- [OpenHands](https://github.com/OpenHands/OpenHands) — heavier Docker agent (overkill for Semicolon HTML)  
- [GitHub Copilot pricing](https://github.com/features/copilot) — student/OSS free paths  
- Faros / DigitalOcean 2026 agent roundups: Cline + Aider are the usual free/BYOK mains when Codex/Claude Code are paid
