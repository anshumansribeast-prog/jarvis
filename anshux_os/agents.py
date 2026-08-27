"""Agent registry and routing for the AnshuX OS."""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Agent:
    name: str
    role: str
    capabilities: list[str] = field(default_factory=list)
    handler: Callable[[str, dict[str, Any]], Any] | None = None


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        key = agent.name.strip().lower()
        if not key:
            raise ValueError("Agent name cannot be empty")
        self._agents[key] = agent

    def list(self) -> list[dict[str, Any]]:
        return [
            {"name": a.name, "role": a.role, "capabilities": a.capabilities}
            for a in self._agents.values()
        ]

    def route(self, name: str, task: str, context: dict[str, Any] | None = None) -> Any:
        agent = self._agents.get(name.strip().lower())
        if not agent or not agent.handler:
            raise ValueError(f"Agent not available: {name}")
        return agent.handler(task, context or {})
