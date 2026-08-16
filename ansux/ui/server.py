"""AnshuX HUD web dashboard with text command API."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from ansux.config import settings
from ansux.core import bridge
from ansux.ui import urls

STATIC_DIR = Path(__file__).resolve().parent / "static"
_server_started = False
_get_state_fn: Callable[[], dict] | None = None
_server_instance: ThreadingHTTPServer | None = None


def reset_server_state() -> None:
    """Allow the HUD server to start again (used after a crash/restart)."""
    global _server_started, _get_state_fn, _server_instance
    if _server_instance:
        try:
            _server_instance.shutdown()
        except Exception:
            pass
    _server_started = False
    _get_state_fn = None
    _server_instance = None


class _HUDHandler(BaseHTTPRequestHandler):

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _route(self) -> str:
        return urls.normalize_path(self.path)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        route = self._route()
        if route in ("/", "/index.html"):
            self._serve_index()
        elif route.startswith("/static/"):
            rel = route[len("/static/"):]
            self._serve_file(STATIC_DIR / rel, self._content_type(rel))
        elif route == "/api/status":
            payload = json.dumps((_get_state_fn() if _get_state_fn else {}) or {}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif route == "/api/config":
            config = {
                "basePath": settings.BASE_PATH,
                "publicUrl": settings.PUBLIC_URL,
                "localUrl": urls.local_hud_url(),
                "assistant": settings.ASSISTANT_NAME,
            }
            payload = json.dumps(config).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if self._route() != "/api/command":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            data = {}

        text = str(data.get("text", "")).strip()
        result = bridge.submit_text(text)
        payload = json.dumps(result).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _content_type(self, name: str) -> str:
        if name.endswith(".css"):
            return "text/css"
        if name.endswith(".js"):
            return "application/javascript"
        return "application/octet-stream"

    def _serve_index(self) -> None:
        html_path = STATIC_DIR / "index.html"
        html = html_path.read_text(encoding="utf-8")
        base = settings.BASE_PATH or ""
        html = html.replace("__ANSUX_BASE__", base)
        html = html.replace("__ANSUX_PUBLIC_URL__", settings.PUBLIC_URL)
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        if content_type == "text/css":
            text = data.decode("utf-8").replace("__ANSUX_BASE__", settings.BASE_PATH or "")
            data = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def start_hud_server(
    get_state: Callable[[], dict],
    port: int | None = None,
    host: str | None = None,
) -> None:
    global _server_started, _get_state_fn, _server_instance
    if _server_started:
        return
    _get_state_fn = get_state
    bind_host = host or settings.HUD_HOST
    bind_port = port or settings.HUD_PORT
    _server_instance = ThreadingHTTPServer((bind_host, bind_port), _HUDHandler)
    _server_started = True
    from ansux.ui.urls import local_hud_url

    print(f"AnshuX HUD running at {local_hud_url()}")
    _server_instance.serve_forever()
