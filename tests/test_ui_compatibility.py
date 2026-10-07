from types import SimpleNamespace


def test_ui_requirement_fallback_supports_legacy_state_objects() -> None:
    legacy = SimpleNamespace(preferred_color="black")
    preferred_colors = getattr(
        legacy,
        "preferred_colors",
        (legacy.preferred_color,) if legacy.preferred_color else (),
    )
    hard_color_constraint = getattr(legacy, "hard_color_constraint", False)
    assert preferred_colors == ("black",)
    assert hard_color_constraint is False
