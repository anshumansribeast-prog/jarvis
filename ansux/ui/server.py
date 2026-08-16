"""AnshuX HUD web dashboard."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from ansux.config import settings

STATIC_DIR = Path(__file__).resolve().parent / "static"
_server_started = False
_get_state_fn: Callable[[], dict] | None = None


class _HUDHandler(BaseHTTPRequestHandler):

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._serve_file(STATIC_DIR / "index.html", "text/html")
        elif self.path.startswith("/static/"):
            rel = self.path[len("/static/"):]
            self._serve_file(STATIC_DIR / rel, self._content_type(rel))
        elif self.path == "/api/status":
            payload = json.dumps((_get_state_fn() if _get_state_fn else {}) or {}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_error(404)

    def _content_type(self, name: str) -> str:
        if name.endswith(".css"):
            return "text/css"
        if name.endswith(".js"):
            return "application/javascript"
        return "application/octet-stream"

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def start_hud_server(get_state: Callable[[], dict], port: int | None = None) -> None:
    global _server_started, _get_state_fn
    if _server_started:
        return
    _get_state_fn = get_state
    server = ThreadingHTTPServer(("127.0.0.1", port or settings.HUD_PORT), _HUDHandler)
    _server_started = True
    print(f"AnshuX HUD running at http://127.0.0.1:{port or settings.HUD_PORT}")
    server.serve_forever()
