# AnshuX OS

An AI-first local control plane that runs in your **web browser**. The backend stays on your own Windows laptop at `127.0.0.1:8765`.

## Browser-first design

There is **no native AnshuX desktop app required** for normal use. Start the local Python server and open the browser UI.

- **Kernel:** coordinates agents, memory, permissions and computer actions.
- **Agent registry:** AnshuX orchestrator plus Ada and Beast adapters.
- **Persistent memory:** JSON-backed facts and bounded event history.
- **Permission gate:** dangerous operations require explicit approval.
- **Controller bridge:** uses a strict allowlist rather than exposing arbitrary shell commands to the AI.
- **Local API:** Flask server on `127.0.0.1:8765`.
- **Browser desktop:** the AnshuX interface is served directly from `/`.

## First-time setup on Windows

1. Open the `jarvis` folder.
2. Double-click `setup_anshux_os.bat` once.
3. Double-click `start_anshux_localhost.bat` whenever you want to use AnshuX OS.
4. Your normal browser opens `http://127.0.0.1:8765/`.

You can also start it from PowerShell inside the folder:

```powershell
.\start_anshux_localhost.bat
```

## Site development / localhost previews

AnshuX OS itself is served from localhost. Your individual web projects remain separate development servers (for example Vite, Next.js, or another local server) and can be launched from the project workspace. The next integration layer will add project discovery, start/stop controls and one-click localhost preview links inside the AnshuX browser UI.

## Important

This is a browser-based local control plane, not a replacement kernel for Windows. It can orchestrate the existing Jarvis runtime and Windows controllers without replacing the operating system itself.
