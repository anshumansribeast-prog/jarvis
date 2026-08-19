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

## Install Aider (recommended today)

In PowerShell, in `C:\Users\Anshu\semicolon` or `C:\Users\Anshu\jarvis`:

```powershell
pip install aider-chat
# Ollama already used by Jarvis/Ada — pull a stronger coder if the machine can take it:
# ollama pull qwen2.5-coder:7b
aider --model ollama/llama3.2:3b
```

If `qwen2.5-coder:7b` (or `14b`) fits RAM, use that instead of `llama3.2:3b` for better code edits.

Then paste the Semicolon task from `anshux/CODEX_CLOUD_TASK.md` (drop Generator, fix mobile Ada).

## Install Cline (closest to “coding agent”)

1. VS Code → Extensions → **Cline** ([github.com/cline/cline](https://github.com/cline/cline))
2. API provider: **Ollama** → `http://localhost:11434` → model `llama3.2:3b` (or qwen2.5-coder)
3. Open the `semicolon` folder, paste `CODEX_CLOUD_TASK.md`

## Sources (web, Aug 2026)

- [Aider](https://github.com/Aider-AI/aider) — OSS CLI pair programmer  
- [Cline](https://github.com/cline/cline) — OSS VS Code agent  
- [Continue](https://github.com/continuedev/continue) — OSS IDE assistant  
- [OpenHands](https://github.com/OpenHands/OpenHands) — heavier Docker agent (overkill for Semicolon HTML)  
- [GitHub Copilot pricing](https://github.com/features/copilot) — student/OSS free paths  
- Faros / DigitalOcean 2026 agent roundups: Cline + Aider are the usual free/BYOK mains when Codex/Claude Code are paid
