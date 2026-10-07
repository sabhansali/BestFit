from pathlib import Path

from tools.default_registry import create_default_registry
from workflow.orchestrator import WorkflowOrchestrator
from workflow.state import WorkflowStage, WorkflowState, WorkflowStatus
from workflow.synchronization import synchronize_search_results


ROOT = Path(__file__).parents[1]


def test_sequential_and_parallel_modes_share_contract() -> None:
    orchestrator = WorkflowOrchestrator(
        create_default_registry(), ROOT / "data" / "products.csv"
    )
    sequential = orchestrator.run(
        WorkflowState("college outfit under Rs 5000"), mode="sequential"
    )
    parallel = orchestrator.run(
        WorkflowState("college outfit under Rs 5000"), mode="parallel"
    )
    for state in (sequential, parallel):
        assert state.status is WorkflowStatus.WAITING_FOR_APPROVAL
        assert state.stage is WorkflowStage.HUMAN_APPROVAL
        assert state.outfit_candidates
        assert state.metrics["total_execution_time_ms"] >= 0
        assert any(event["event"] == "synchronization_completed" for event in state.trace)


def test_synchronization_rejects_missing_and_duplicate_branches() -> None:
    state = WorkflowState("query")
    try:
        synchronize_search_results(
            state,
            ("Top", "Bottom"),
            {"Top": [{"product_id": "P1"}], "Bottom": [{"product_id": "P1"}, {"product_id": "P1"}]},
        )
        raise AssertionError("Expected synchronization failure")
    except ValueError as error:
        assert "Duplicate" in str(error)
    assert state.errors
