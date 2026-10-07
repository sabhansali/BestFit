from pathlib import Path

from tools.default_registry import create_default_registry
from tools.registry import ToolRegistry
from workflow.orchestrator import WorkflowOrchestrator
from workflow.state import WorkflowStage, WorkflowState, WorkflowStatus


ROOT = Path(__file__).parents[1]


class FlakySearchRegistry(ToolRegistry):
    def __init__(self) -> None:
        super().__init__()
        self.search_attempts = 0

    def execute(self, agent_role: str, tool_name: str, **kwargs: object) -> object:
        if tool_name == "search_products":
            self.search_attempts += 1
            if self.search_attempts == 1:
                raise RuntimeError("temporary catalog timeout")
        return super().execute(agent_role, tool_name, **kwargs)


def test_transient_search_failure_uses_bounded_retry_and_cost_metric() -> None:
    registry = FlakySearchRegistry()
    default = create_default_registry()
    registry.tools = default.tools
    state = WorkflowOrchestrator(registry, ROOT / "data" / "products.csv").run(
        WorkflowState("college outfit under Rs 5000"), mode="parallel"
    )
    assert state.status is WorkflowStatus.WAITING_FOR_APPROVAL
    assert state.retry_count == 1
    assert state.retry_history[0]["stage"].startswith("search:")
    assert state.metrics["experimental_cost_units"] > 0
    assert any(event["event"] == "retry_started" for event in state.trace)


def test_checkpoint_results_are_exposed_for_ui_and_trace() -> None:
    state = WorkflowOrchestrator(
        create_default_registry(), ROOT / "data" / "products.csv"
    ).run(WorkflowState("college outfit under Rs 5000"))
    assert state.checkpoint_results["plan"]["status"] == "PASSED"
    assert state.checkpoint_results["filter"]["status"] == "PASSED"
    assert state.checkpoint_results["ranking"]["status"] == "PASSED"
    assert len([event for event in state.trace if event["event"] == "checkpoint_validation"]) == 3


def test_invalid_mode_is_rejected_without_mutating_workflow() -> None:
    state = WorkflowState("college outfit")
    try:
        WorkflowOrchestrator(
            create_default_registry(), ROOT / "data" / "products.csv"
        ).run(state, mode="unknown")
        raise AssertionError("Expected invalid execution mode")
    except ValueError:
        pass
    assert state.stage is WorkflowStage.CREATED
