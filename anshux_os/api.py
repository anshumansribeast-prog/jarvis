"""Local HTTP API for the AnshuX OS desktop shell."""

from __future__ import annotations

from flask import Flask, jsonify, request, send_from_directory

from .kernel import AnshuXKernel
from .permissions import Risk


KNOWN_ACTIONS = {
    "volume_up": Risk.WRITE,
    "volume_down": Risk.WRITE,
    "mute": Risk.WRITE,
    "screenshot": Risk.WRITE,
    "lock": Risk.WRITE,
    "open_app": Risk.WRITE,
    "close_app": Risk.WRITE,
    "shutdown": Risk.DANGEROUS,
    "restart": Risk.DANGEROUS,
}


def create_app(kernel: AnshuXKernel | None = None) -> Flask:
    app = Flask(__name__)
    core = kernel or AnshuXKernel()

    @app.get("/")
    def desktop():
        return send_from_directory(app.root_path + "/../desktop", "index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "service": "anshux-os", "version": core.VERSION})

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
    def action_catalog():
        return jsonify({"actions": [{"name": name, "risk": risk.value} for name, risk in KNOWN_ACTIONS.items()]})

    @app.get("/api/os/actions/pending")
    def pending_actions():
        return jsonify({"actions": core.pending_actions()})

    @app.post("/api/os/actions")
    def request_action():
        body = request.get_json(silent=True) or {}
        name = str(body.get("name", "")).strip()
        if name not in KNOWN_ACTIONS:
            return jsonify({"error": "unsupported action", "supported": sorted(KNOWN_ACTIONS)}), 400
        args = body.get("args") if isinstance(body.get("args"), dict) else {}
        description = str(body.get("description", name))
        requested_risk = body.get("risk")
        if requested_risk is not None and str(requested_risk).lower() != KNOWN_ACTIONS[name].value:
            return jsonify({"error": "risk does not match registered action"}), 400
        return jsonify(core.request_action(name, KNOWN_ACTIONS[name], description, args)), 202

    @app.post("/api/os/actions/<action_id>/approve")
    def approve_action(action_id: str):
        try:
            result = core.approve_action(action_id)
        except (ValueError, PermissionError) as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": "action failed", "detail": str(exc)}), 500
        return jsonify({"ok": True, "action_id": action_id, "result": result})

    @app.post("/api/os/actions/<action_id>/deny")
    def deny_action(action_id: str):
        core.deny_action(action_id)
        return jsonify({"ok": True, "action_id": action_id, "status": "denied"})

    @app.post("/api/os/task")
    def task():
        body = request.get_json(silent=True) or {}
        text = body.get("task")
        agent = str(body.get("agent", "AnshuX"))
        if not isinstance(text, str) or not text.strip():
            return jsonify({"error": "task must be a non-empty string"}), 400
        try:
            result = core.agents.route(agent, text.strip(), {"source": "desktop"})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(result), 202

    return app
