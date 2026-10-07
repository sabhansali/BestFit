from ui.workflow_view import execute_query


def test_occasion_is_not_invented_when_query_only_specifies_summer_dresses() -> None:
    state = execute_query("summer dresses under Rs 5000", "parallel")

    assert state.requirements is not None
    assert state.requirements.occasion is None
    assert state.requirements.season == "summer"
    assert state.requirements.required_categories == ("Dress",)
    assert state.status.value in {"waiting_for_approval", "failed"}
