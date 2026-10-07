"""Common execution contract for all Phase 3 agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any

from tools.registry import ToolRegistry
from workflow.state import WorkflowState


class Agent(ABC):
    """An agent can update shared state but cannot call another agent."""

    name: str
    role: str

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, state: WorkflowState) -> WorkflowState:
        started = perf_counter()
        state.record_agent_execution()
        state.add_trace({"agent": self.name, "event": "agent_started"})
        try:
            self.run(state)
        except Exception as error:
            state.errors.append({"agent": self.name, "error": str(error)})
            state.add_trace({"agent": self.name, "event": "agent_failed", "error": str(error)})
            raise
        duration_ms = round((perf_counter() - started) * 1000, 3)
        state.metrics[f"{self.name}_duration_ms"] = duration_ms
        state.add_trace(
            {"agent": self.name, "event": "agent_completed", "duration_ms": duration_ms}
        )
        return state

    @abstractmethod
    def run(self, state: WorkflowState) -> None:
        """Perform this agent's state transition."""

    def call_tool(self, state: WorkflowState, tool_name: str, **kwargs: Any) -> Any:
        started = perf_counter()
        try:
            result = self.registry.execute(self.role, tool_name, **kwargs)
        except Exception as error:
            state.tool_calls.append(
                {"agent": self.name, "tool": tool_name, "status": "failed", "error": str(error)}
            )
            state.add_trace({"agent": self.name, "event": "tool_call_failed", "tool": tool_name})
            raise
        duration_ms = round((perf_counter() - started) * 1000, 3)
        state.record_tool_execution()
        call = {
            "agent": self.name,
            "tool": tool_name,
            "status": "success",
            "duration_ms": duration_ms,
        }
        state.tool_calls.append(call)
        state.add_trace({"agent": self.name, "event": "tool_call", **call})
        return result
