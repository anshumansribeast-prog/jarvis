"""AnshuX OS control kernel.

The kernel coordinates memory, agents, and permission-aware actions while
keeping hardware/app controllers behind explicit adapters.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .agents import Agent, AgentRegistry
from .memory import MemoryStore
from .permissions import Action, PermissionManager, Risk


class AnshuXKernel:
    def __init__(self, memory: MemoryStore | None = None) -> None:
        self.memory = memory or MemoryStore()
        self.permissions = PermissionManager()
        self.agents = AgentRegistry()
        self.started_at = datetime.now(timezone.utc).isoformat()
        self._register_builtin_agents()

    def _register_builtin_agents(self) -> None:
        self.agents.register(Agent("AnshuX", "orchestrator", ["routing", "memory", "planning"], self._orchestrate))
        self.agents.register(Agent("Ada", "coding agent", ["code", "debug", "project workspace"], self._agent_stub))
        self.agents.register(Agent("Beast", "engineering agent", ["systems", "automation", "analysis"], self._agent_stub))

    def _orchestrate(self, task: str, context: dict[str, Any]) -> dict[str, Any]:
        return {"status": "accepted", "task": task, "context": context}

    @staticmethod
    def _agent_stub(task: str, context: dict[str, Any]) -> dict[str, Any]:
        return {"status": "queued", "task": task, "context": context}

    def status(self) -> dict[str, Any]:
        return {
            "name": "AnshuX OS",
            "version": "0.1.0",
            "started_at": self.started_at,
            "agents": self.agents.list(),
            "pending_actions": len(self.permissions.pending()),
        }

    def request_action(self, name: str, risk: Risk, description: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        action_id = uuid4().hex
        action = Action(name=name, risk=risk, description=description, args=args or {})
        self.permissions.request(action_id, action)
        self.memory.event("action_requested", {"id": action_id, "name": name, "risk": risk.value})
        return {"action_id": action_id, "name": name, "risk": risk.value, "description": description, "args": action.args}
