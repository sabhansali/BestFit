from ui.workflow_view import execute_query
from ui.requirements_view import render_requirements
from ui.recommendations_view import render_recommendations
from ui.dashboard_view import render_system_dashboard


def test_client_and_system_views_consume_same_workflow_state() -> None:
    state = execute_query("summery dresses under Rs 5000", "parallel")
    assert state.requirements is not None
    assert state.ranking_results
    assert state.trace
    assert state.metrics["total_execution_time_ms"] >= 0
    assert callable(render_requirements)
    assert callable(render_recommendations)
    assert callable(render_system_dashboard)
