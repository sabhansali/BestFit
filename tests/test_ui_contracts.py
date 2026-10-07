from pathlib import Path

from tools.default_registry import create_default_registry
from ui.workflow_view import execute_query
from workflow.orchestrator import WorkflowOrchestrator
from workflow.state import WorkflowStage, WorkflowState, WorkflowStatus


ROOT = Path(__file__).parents[1]


def test_ui_workflow_view_returns_ui_ready_state() -> None:
    state = execute_query("college outfit under Rs 5000", "parallel")
    assert state.status is WorkflowStatus.WAITING_FOR_APPROVAL
    assert state.requirements is not None
    assert state.ranking_results
    assert state.trace
    assert state.metrics["experimental_cost_units"] > 0


def test_human_approval_completes_workflow() -> None:
    state = WorkflowOrchestrator(
        create_default_registry(), ROOT / "data" / "products.csv"
    ).run(WorkflowState("college outfit under Rs 5000"))
    state.record_human_decision(True)
    assert state.human_approval is True
    assert state.stage is WorkflowStage.COMPLETED
    assert state.status is WorkflowStatus.COMPLETED


def test_human_rejection_reopens_reanalysis() -> None:
    state = WorkflowOrchestrator(
        create_default_registry(), ROOT / "data" / "products.csv"
    ).run(WorkflowState("college outfit under Rs 5000"))
    state.record_human_decision(False)
    assert state.human_approval is False
    assert state.stage is WorkflowStage.PLANNING
    assert state.status is WorkflowStatus.RUNNING
    assert not state.ranking_results
