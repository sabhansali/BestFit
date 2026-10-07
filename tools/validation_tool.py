"""Basic recommendation validation tool."""

from typing import Any

from rules.eligibility_rules import validate_outfit


def validate_recommendation(
    outfit: list[dict[str, Any]] | None = None,
    budget_inr: float | None = None,
    required_categories: tuple[str, ...] = (),
    occasion: str | None = None,
    gender: str | None = None,
    season: str | None = None,
    preferred_colors: tuple[str, ...] = (),
    hard_color_constraint: bool = False,
    outfits: list[list[dict[str, Any]]] | None = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    if outfits is not None:
        return [
            validate_recommendation(
                candidate,
                budget_inr,
                required_categories,
                occasion,
                gender,
                season,
                preferred_colors,
                hard_color_constraint,
            )
            for candidate in outfits
        ]
    if outfit is None:
        raise ValueError("outfit is required")
    eligibility = validate_outfit(
        outfit, required_categories, budget_inr, occasion, gender, season,
        preferred_colors, hard_color_constraint
    )
    return {
        "status": "PASSED" if eligibility["eligibility_status"] == "ELIGIBLE" else "FAILED",
        "errors": eligibility["validation_errors"],
        "warnings": eligibility["validation_warnings"],
        "checks": eligibility["checks"],
        "eligibility_status": eligibility["eligibility_status"],
    }


def validate_recommendations(
    outfits: list[list[dict[str, Any]]],
    budget_inr: float | None,
    required_categories: tuple[str, ...],
    occasion: str | None = None,
    gender: str | None = None,
    season: str | None = None,
    preferred_colors: tuple[str, ...] = (),
    hard_color_constraint: bool = False,
) -> list[dict[str, Any]]:
    """Validate a checkpoint batch without one registry call per candidate."""

    return [
        validate_recommendation(
            outfit,
            budget_inr,
            required_categories,
            occasion,
            gender,
            season,
            preferred_colors,
            hard_color_constraint,
        )
        for outfit in outfits
    ]
