"""Local HTTP API for the AnshuX OS desktop shell."""

from __future__ import annotations

from flask import Flask, jsonify, request

from .kernel import AnshuXKernel
from .permissions import Risk


def create_app(kernel: AnshuXKernel | None = None) -> Flask:
    app = Flask(__name__)
    core = kernel or AnshuXKernel()

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

    return app
