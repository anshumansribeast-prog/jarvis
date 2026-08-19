"""HTTP routes for AI Command Office. Served by the same 8765 office process."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlparse

from command_office import MODEL, ROOT
from command_office.orchestrator import (
    approve_task,
    cancel_task,
    commander_chat,
    reassign_task,
    retry_task,
    start_worker,
)
from command_office.store import (
    add_conversation,
    list_workspace_files,
    read_workspace_file,
    snapshot,
    update_settings,
)


def _send_bytes(handler, code: int, body: bytes, content_type: str) -> None:
    handler.send_response(code)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _send_file(handler, path: Path, content_type: str) -> None:
    if not path.is_file():
        handler.send_error(404)
        return
    _send_bytes(handler, 200, path.read_bytes(), content_type)


def handle_get(handler, path: str) -> bool:
    parsed = urlparse(handler.path)
    route = parsed.path
    if route in {"/command", "/command/", "/command/index.html"}:
        page = ROOT / "office" / "index.html"
        _send_file(handler, page, "text/html; charset=utf-8")
        return True
    if route == "/api/command":
        payload = snapshot()
        payload["ok"] = True
        payload["files"] = list_workspace_files()
        payload["settings"]["model"] = MODEL
        handler._json(200, payload)
        return True
    if route == "/api/command/file":
        name = (parse_qs(parsed.query).get("path") or [""])[0]
        try:
            text = read_workspace_file(name)
        except (ValueError, FileNotFoundError) as exc:
            handler._json(400, {"ok": False, "error": str(exc)})
            return True
        handler._json(200, {"ok": True, "path": name, "text": text})
        return True
    if route == "/api/command/site":
        from command_office.store import project_slug

        slug = (parse_qs(parsed.query).get("project") or [project_slug()])[0]
        page = (parse_qs(parsed.query).get("page") or ["index.html"])[0]
        clean = page.replace("\\", "/").lstrip("/")
        if ".." in clean.split("/") or "/" in clean:
            handler._json(400, {"ok": False, "error": "invalid page"})
            return True
        from command_office import WORKSPACE

        path = WORKSPACE / "projects" / slug / "site" / clean
        if not path.is_file():
            handler.send_error(404)
            return True
        ctype = "text/html; charset=utf-8" if clean.endswith(".html") else "text/plain; charset=utf-8"
        _send_file(handler, path, ctype)
        return True
    return False


def handle_post(handler, path: str, body: dict) -> bool:
    try:
        if path == "/api/command/chat":
            text = str(body.get("text") or "").strip()
            if not text:
                handler._json(400, {"ok": False, "error": "empty"})
                return True
            cid = body.get("conversation_id") or None
            result = commander_chat(text, cid)
            handler._json(200, {"ok": True, **result})
            return True
        if path == "/api/command/conversation":
            row = add_conversation()
            handler._json(200, {"ok": True, "conversation": row, "state": snapshot()})
            return True
        if path == "/api/command/retry":
            handler._json(200, {"ok": True, "state": retry_task(int(body["id"]))})
            return True
        if path == "/api/command/cancel":
            handler._json(200, {"ok": True, "state": cancel_task(int(body["id"]))})
            return True
        if path == "/api/command/reassign":
            handler._json(
                200,
                {"ok": True, "state": reassign_task(int(body["id"]), str(body.get("agent") or ""))},
            )
            return True
        if path == "/api/command/approve":
            handler._json(200, {"ok": True, "state": approve_task(int(body["id"]))})
            return True
        if path == "/api/command/settings":
            handler._json(200, {"ok": True, "settings": update_settings(body)})
            return True
    except (ValueError, KeyError, TypeError) as exc:
        handler._json(400, {"ok": False, "error": str(exc)})
        return True
    return False


def boot() -> None:
    start_worker()
