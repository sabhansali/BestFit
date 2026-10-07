from ui.workflow_view import execute_query
from workflow.state import WorkflowStage, WorkflowStatus


def test_budget_constrained_query_never_returns_over_budget_outfits() -> None:
    state = execute_query("college outfit under Rs 3000", "parallel")
    assert state.requirements is not None
    assert state.requirements.budget_inr == 3000
    for result in state.ranking_results:
        total = sum(float(item["price_inr"]) for item in result["outfit"])
        assert total <= 3000
    assert state.status in {WorkflowStatus.WAITING_FOR_APPROVAL, WorkflowStatus.FAILED}


def test_color_and_occasion_query_preserves_structured_requirements() -> None:
    state = execute_query(
        "Give me a black smart casual farewell outfit under Rs 5000", "parallel"
    )
    assert state.requirements is not None
    assert state.requirements.preferred_color == "black"
    assert state.requirements.preferred_colors == ("black",)
    assert state.requirements.occasion == "Farewell"
    assert state.status in {WorkflowStatus.WAITING_FOR_APPROVAL, WorkflowStatus.FAILED}


def test_multiple_requested_colors_are_preserved_and_used() -> None:
    state = execute_query(
        "black and white smart casual college outfit under Rs 5000", "parallel"
    )
    assert state.requirements is not None
    assert state.requirements.preferred_colors == ("black", "white")
    assert state.requirements.hard_color_constraint is False


def test_three_category_and_four_category_workflows_are_supported() -> None:
    three_category = execute_query("college Top Bottom Footwear under Rs 5000", "parallel")
    four_category = execute_query(
        "college Top Bottom Footwear Accessory under Rs 5000", "parallel"
    )
    assert three_category.requirements is not None
    assert four_category.requirements is not None
    assert len(three_category.requirements.required_categories) == 3
    assert len(four_category.requirements.required_categories) == 4
    assert three_category.status in {WorkflowStatus.WAITING_FOR_APPROVAL, WorkflowStatus.FAILED}
    assert four_category.status in {WorkflowStatus.WAITING_FOR_APPROVAL, WorkflowStatus.FAILED}


def test_approval_and_rejection_paths_are_end_to_end() -> None:
    approved = execute_query("college outfit under Rs 5000", "parallel")
    approved.record_human_decision(True)
    assert approved.status is WorkflowStatus.COMPLETED

    rejected = execute_query("college outfit under Rs 5000", "parallel")
    rejected.record_human_decision(False)
    assert rejected.status is WorkflowStatus.RUNNING
    assert rejected.stage is WorkflowStage.PLANNING
    assert not rejected.ranking_results
