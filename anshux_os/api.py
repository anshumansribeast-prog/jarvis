"""Local HTTP API and desktop entry point for the AnshuX OS."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .kernel import AnshuXKernel
from .permissions import Risk


ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop"


def create_app(kernel: AnshuXKernel | None = None) -> Flask:
    app = Flask(__name__)
    core = kernel or AnshuXKernel()

    @app.get("/")
    def desktop():
        return send_from_directory(DESKTOP, "index.html")

    @app.get("/api/os/status")
    def os_status():
        return jsonify(core.status())

    @app.get("/api/os/agents")
    def agents():
        return jsonify({"agents": core.agents.list()})

    @app.get("/api/os/memory")
    def memory():
        limit = min(max(request.args.get("limit", default=20, type=int), 1), 100)
        return jsonify({"events": core.memory.recent(limit)})

    @app.post("/api/os/memory")
    def remember():
        body = request.get_json(silent=True) or {}
        key, value = body.get("key"), body.get("value")
        if not isinstance(key, str) or not key.strip() or not isinstance(value, str):
            return jsonify({"error": "key and string value are required"}), 400
        core.memory.remember(key.strip(), value)
        return jsonify({"ok": True})

    @app.get("/api/os/actions")
    def pending_actions():
        return jsonify({
            "actions": [
                {"action_id": key, "name": value.name, "risk": value.risk.value, "description": value.description, "args": value.args}
                for key, value in core.permissions.pending().items()
            ]
        })

    @app.post("/api/os/actions")
    def request_action():
        body = request.get_json(silent=True) or {}
        risk_name = str(body.get("risk", "write")).lower()
        try:
            risk = Risk(risk_name)
        except ValueError:
            return jsonify({"error": "risk must be read, write, or dangerous"}), 400
        return jsonify(core.request_action(
            str(body.get("name", "unknown")),
            risk,
            str(body.get("description", "")),
            body.get("args") if isinstance(body.get("args"), dict) else {},
        )), 202

    @app.post("/api/os/actions/<action_id>/approve")
    def approve_action(action_id: str):
        try:
            result = core.approve_action(action_id)
        except (ValueError, PermissionError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"ok": True, "result": result})

    return app
