"""AnshuX OS control kernel."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .agents import Agent, AgentRegistry
from .executor import ActionExecutor
from .memory import MemoryStore
from .permissions import Action, PermissionManager, Risk


class AnshuXKernel:
    VERSION = "0.2.0"

    def __init__(self, memory: MemoryStore | None = None) -> None:
        self.memory = memory or MemoryStore()
        self.permissions = PermissionManager()
        self.executor = ActionExecutor()
        self.agents = AgentRegistry()
        self.started_at = datetime.now(timezone.utc).isoformat()
        self._register_builtin_agents()

    def _register_builtin_agents(self) -> None:
        self.agents.register(Agent("AnshuX", "orchestrator", ["routing", "memory", "planning"], self._orchestrate))
        self.agents.register(Agent("Ada", "coding agent", ["code", "debug", "project workspace"], self._agent_stub))
        self.agents.register(Agent("Beast", "engineering agent", ["systems", "automation", "analysis"], self._agent_stub))

    def _orchestrate(self, task: str, context: dict[str, Any]) -> dict[str, Any]:
        result = {"status": "accepted", "task": task, "context": context}
        self.memory.event("task_received", result)
        return result

    @staticmethod
    def _agent_stub(task: str, context: dict[str, Any]) -> dict[str, Any]:
        return {"status": "queued", "task": task, "context": context}

    def status(self) -> dict[str, Any]:
        return {
            "name": "AnshuX OS",
            "version": self.VERSION,
            "started_at": self.started_at,
            "agents": self.agents.list(),
            "pending_actions": len(self.permissions.pending()),
        }

    def request_action(
        self,
        name: str,
        risk: Risk,
        description: str,
        args: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        action_id = uuid4().hex
        action = Action(name=name.strip(), risk=risk, description=description.strip(), args=args or {})
        self.permissions.request(action_id, action)
        self.memory.event("action_requested", {"id": action_id, "name": action.name, "risk": action.risk.value})
        return {
            "action_id": action_id,
            "name": action.name,
            "risk": action.risk.value,
            "description": action.description,
            "args": action.args,
        }

    def pending_actions(self) -> list[dict[str, Any]]:
        return [
            {
                "action_id": action_id,
                "name": action.name,
                "risk": action.risk.value,
                "description": action.description,
                "args": action.args,
            }
            for action_id, action in self.permissions.pending().items()
        ]

    def approve_action(self, action_id: str) -> Any:
        action = self.permissions.approve(action_id)
        try:
            result = self.executor.execute(action.name, action.args, approved=True)
        except Exception:
            self.memory.event("action_failed", {"id": action_id, "name": action.name})
            raise
        self.memory.event("action_executed", {"id": action_id, "name": action.name, "risk": action.risk.value})
        return result

    def deny_action(self, action_id: str) -> None:
        self.permissions.deny(action_id)
        self.memory.event("action_denied", {"id": action_id})
