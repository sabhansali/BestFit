from rules.compatibility_rules import colors_compatible, products_compatible
from rules.ranking_rules import rank_outfits
from rules.scoring_rules import score_products
from workflow.state import (
    Requirements,
    WorkflowStage,
    WorkflowState,
    WorkflowStatus,
)


def product(product_id: str, category: str, color: str, style: str = "Smart Casual") -> dict:
    return {
        "product_id": product_id,
        "category": category,
        "color": color,
        "style": style,
        "occasion": "College",
        "season": "All Season",
        "formality": 2,
        "price_inr": 1000,
    }


def test_color_and_product_compatibility_are_deterministic() -> None:
    assert colors_compatible("Black", "White")
    assert not colors_compatible("Pink", "Orange")
    assert products_compatible([product("1", "Top", "Black"), product("2", "Bottom", "White")])


def test_scoring_exposes_constraints_and_overall_score() -> None:
    outfit = [product("1", "Top", "Black"), product("2", "Bottom", "White")]
    result = score_products(outfit, ("Top", "Bottom"), budget_inr=2500, occasion="College")
    assert result.constraint_satisfaction == 100
    assert 0 <= result.overall_score <= 100
    assert "color_compatibility" in result.as_dict()


def test_ranking_is_stable_and_descending() -> None:
    first = [product("1", "Top", "Black"), product("2", "Bottom", "White")]
    second = [product("3", "Top", "Pink", style="Casual"), product("4", "Bottom", "Orange", style="Casual")]
    ranked = rank_outfits([second, first], ("Top", "Bottom"), budget_inr=3000, occasion="College")
    assert ranked[0][1].overall_score >= ranked[1][1].overall_score


def test_workflow_state_has_safe_transition_and_audit_metadata() -> None:
    state = WorkflowState("black and white college outfit")
    state.transition(WorkflowStage.PLANNING, WorkflowStatus.RUNNING)
    state.record_agent_execution()
    state.add_trace({"event": "planning_started"})
    assert state.stage is WorkflowStage.PLANNING
    assert state.agent_execution_count == 1
    assert state.trace[0]["workflow_id"] == state.workflow_id


def test_requirements_reject_invalid_budget_and_empty_categories() -> None:
    try:
        Requirements(0, "College", ("Top",))
        raise AssertionError("Expected invalid budget to be rejected")
    except ValueError:
        pass
    try:
        Requirements(1000, "College", ())
        raise AssertionError("Expected empty categories to be rejected")
    except ValueError:
        pass
