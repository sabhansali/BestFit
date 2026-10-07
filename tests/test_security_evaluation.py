from pathlib import Path

from security.evaluation import run_security_evaluation
from tools.default_registry import create_default_registry
from workflow.orchestrator import WorkflowOrchestrator
from workflow.state import WorkflowStage, WorkflowState, WorkflowStatus


ROOT = Path(__file__).parents[1]


def test_required_security_scenarios_are_blocked() -> None:
    report = run_security_evaluation(ROOT / "data" / "products.csv")
    assert report["total_scenarios"] == 5
    assert report["blocked_scenarios"] == 5
    assert report["security_pass_rate"] == 1.0


def test_human_decision_cannot_bypass_approval_stage() -> None:
    state = WorkflowState("college outfit")
    try:
        state.record_human_decision(True)
        raise AssertionError("Approval bypass was accepted")
    except ValueError as error:
        assert "waiting for approval" in str(error)


def test_terminal_workflow_cannot_be_reopened_by_human_decision() -> None:
    state = WorkflowOrchestrator(
        create_default_registry(), ROOT / "data" / "products.csv"
    ).run(WorkflowState("college outfit under Rs 5000"))
    state.record_human_decision(True)
    assert state.status is WorkflowStatus.COMPLETED
    assert state.stage is WorkflowStage.COMPLETED
    try:
        state.record_human_decision(False)
        raise AssertionError("Terminal workflow was reopened")
    except ValueError as error:
        assert "waiting for approval" in str(error)
