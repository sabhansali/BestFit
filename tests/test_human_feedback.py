from pathlib import Path

from tools.default_registry import create_default_registry
from workflow.orchestrator import WorkflowOrchestrator
from workflow.state import WorkflowStage, WorkflowState


ROOT = Path(__file__).parents[1]


def test_wrong_color_rejection_keeps_search_and_targets_ranking() -> None:
    state = WorkflowOrchestrator(
        create_default_registry(), ROOT / "data" / "products.csv"
    ).run(WorkflowState("college outfit under Rs 5000"))

    state.record_human_decision(False, "wrong_color", "Prefer black and white")

    assert state.human_feedback == {
        "reason": "wrong_color",
        "text": "Prefer black and white",
    }
    assert state.reanalysis is not None
    assert state.reanalysis["rerun_from"] == "ranking"
    assert "searching" in state.reanalysis["skipped_stages"]
    assert state.stage is WorkflowStage.RANKING


def test_poor_combination_rejection_targets_reconstruction() -> None:
    state = WorkflowOrchestrator(
        create_default_registry(), ROOT / "data" / "products.csv"
    ).run(WorkflowState("college outfit under Rs 5000"))

    state.record_human_decision(False, "poor_combination")

    assert state.reanalysis is not None
    assert state.reanalysis["rerun_from"] == "building"
    assert state.stage is WorkflowStage.BUILDING
    assert not state.outfit_candidates
