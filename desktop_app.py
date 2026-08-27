"""Native Windows desktop host for AnshuX OS.

The OS control plane still runs locally on 127.0.0.1. pywebview hosts the
same desktop UI inside a native application window, so the user does not
need to keep a normal browser tab open.
"""

from __future__ import annotations

import threading
import time
import webbrowser

import webview

from anshux_os.api import create_app

HOST = "127.0.0.1"
PORT = 8765
URL = f"http://{HOST}:{PORT}/"


def run_server() -> None:
    app = create_app()
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


def main() -> None:
    thread = threading.Thread(target=run_server, name="anshux-os-server", daemon=True)
    thread.start()

    for _ in range(50):
        try:
            import urllib.request
            with urllib.request.urlopen(f"http://{HOST}:{PORT}/api/os/status", timeout=0.2):
                break
        except Exception:
            time.sleep(0.1)
    else:
        raise RuntimeError("AnshuX OS server failed to start")

    webview.create_window("AnshuX OS", URL, width=1440, height=900, min_size=(1000, 650), text_select=True)
    webview.start()


if __name__ == "__main__":
    main()
