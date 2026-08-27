# AnshuX OS Foundation

An AI-first desktop control plane built on the existing Jarvis repository.

## What is in this first foundation

- **Kernel:** central runtime coordinating agents, memory and actions.
- **Agent registry:** AnshuX orchestrator plus Ada and Beast adapters.
- **Persistent memory:** JSON-backed facts and bounded event history.
- **Permission gate:** every requested operation is represented as an action; dangerous operations require an explicit approval call.
- **Controller bridge:** uses the existing app/system controllers through a strict allowlist; arbitrary shell commands are not exposed to the AI layer.
- **Local API:** Flask server on `127.0.0.1:8765`.
- **Desktop shell:** browser UI served from `/` with live kernel status and agent visibility.

## Run

```powershell
python -m pip install -r requirements.txt
python os_server.py
```

Open `http://127.0.0.1:8765/`.

## Next layers

The foundation is deliberately separate from the existing voice/runtime code. The next stages are to connect voice input, the existing Jarvis conversation loop, real Ada/Beast endpoints, file/project workspace APIs, richer desktop windows, and a mobile companion without giving the model unrestricted operating-system access.
