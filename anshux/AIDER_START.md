# Get started with Aider (free backup)

**OpenCode is MAIN.** Use **Aider** when OpenCode is busy, or if you want git-aware edits in the terminal without the OpenCode TUI. Aider talks to the **Ollama** you already run for Jarvis/Ada. $0.

Official install: [aider.chat/docs/install](https://aider.chat/docs/install.html)  
Ollama: [aider.chat/docs/llms/ollama](https://aider.chat/docs/llms/ollama.html)

## 1. Ollama running

PowerShell:

```powershell
ollama list
curl http://127.0.0.1:11434/api/version
```

If the list is empty: `ollama pull llama3.2:3b`  
Better for code (if RAM allows): `ollama pull qwen2.5-coder:7b`

Leave the Ollama app running in the Windows tray.

## 2. Install Aider

```powershell
python -m pip install aider-install
aider-install
```

Windows one-liner if that fails:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://aider.chat/install.ps1 | iex"
```

## 3. Point Aider at Ollama

```powershell
setx OLLAMA_API_BASE http://127.0.0.1:11434
```

Close PowerShell and open a **new** window (setx only applies to new shells).

## 4. Start (loads the Aider role card)

From ANSHUX (preferred — `.aider.conf.yml` reads `.team/aider.md`):

```powershell
cd C:\Users\Anshu\anshux
aider --config .aider.conf.yml
```

That config uses `ollama_chat/llama3.2:3b` and auto-reads `.team/aider.md`, `AGENTS.md`, and `TEAM.md`.

To work in the Semicolon clone instead:

```powershell
cd C:\Users\Anshu\semicolon
aider --model ollama_chat/llama3.2:3b
```

If you pulled the coder model (either folder):

```powershell
aider --model ollama_chat/qwen2.5-coder:7b
```

Use `ollama_chat/` not `ollama/` (Aider’s docs).

## 5. First task

At the Aider prompt, paste the Semicolon job from `anshux/OPENCODE_TASK.md` (drop Generator, fix mobile Ada).

Useful keys: `/help`  `/undo`  `/commit`

## If it fails

| Problem | Fix |
| --- | --- |
| `aider` not found | New terminal, or `python -m aider` |
| Connection refused | Start Ollama from the tray; check `127.0.0.1:11434` |
| Tiny/confused replies | Default Ollama context is small; use `qwen2.5-coder:7b` and keep one task at a time |
| Git errors | `git status` in that folder; Aider needs a git repo |

Cline is optional (VS Code sidebar). Aider is the one to use for this project.
