"""MCP-style metadata, authorization, execution, and call logging."""

from dataclasses import dataclass
from typing import Any, Callable

from security.authorization import authorize


@dataclass(frozen=True)
class ToolMetadata:
    name: str
    description: str
    allowed_agents: frozenset[str]


@dataclass
class ToolRegistry:
    tools: dict[str, tuple[ToolMetadata, Callable[..., Any]]]

    def __init__(self) -> None:
        self.tools = {}

    def register(self, metadata: ToolMetadata, handler: Callable[..., Any]) -> None:
        if metadata.name in self.tools:
            raise ValueError(f"Tool already registered: {metadata.name}")
        self.tools[metadata.name] = (metadata, handler)

    def discover(self, agent_role: str | None = None) -> list[ToolMetadata]:
        values = [metadata for metadata, _ in self.tools.values()]
        if agent_role is None:
            return values
        return [metadata for metadata in values if agent_role in metadata.allowed_agents]

    def execute(self, agent_role: str, tool_name: str, **kwargs: Any) -> Any:
        if tool_name not in self.tools:
            raise KeyError(f"Unknown tool: {tool_name}")
        metadata, handler = self.tools[tool_name]
        decision = authorize(agent_role, tool_name)
        if not decision.allowed or agent_role not in metadata.allowed_agents:
            raise PermissionError(decision.reason)
        return handler(**kwargs)
