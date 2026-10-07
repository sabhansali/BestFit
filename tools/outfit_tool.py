"""Outfit construction tool."""

from itertools import product as cartesian_product
from typing import Any, Iterable, Sequence

from rules.eligibility_rules import validate_outfit


def build_outfits(
    products_by_category: dict[str, Sequence[dict[str, Any]]],
    required_categories: Iterable[str],
    limit: int = 100,
    budget_inr: float | None = None,
    occasion: str | None = None,
    gender: str | None = None,
    season: str | None = None,
    preferred_colors: Iterable[str] = (),
    hard_color_constraint: bool = False,
    metrics: dict[str, float] | None = None,
    rejected_candidates: list[dict[str, Any]] | None = None,
) -> list[list[dict[str, Any]]]:
    categories = tuple(required_categories)
    if not categories:
        return []
    candidates = []
    allowed_gender_cohorts = (
        ({gender.lower(), "unisex"},)
        if gender
        else ({"men", "unisex"}, {"women", "unisex"}, {"unisex"})
    )
    for combination in cartesian_product(*(products_by_category.get(category, ()) for category in categories)):
        if metrics is not None:
            metrics["deterministic_candidate_validations"] = (
                metrics.get("deterministic_candidate_validations", 0) + 1
            )
        genders = {
            str(item.get("gender", "")).strip().lower()
            for item in combination
            if item.get("gender")
        }
        if not any(genders.issubset(cohort) for cohort in allowed_gender_cohorts):
            continue
        eligibility = validate_outfit(
            combination,
            categories,
            budget_inr=budget_inr,
            occasion=occasion,
            gender=gender,
            season=season,
            preferred_colors=preferred_colors,
            hard_color_constraint=hard_color_constraint,
        )
        if eligibility["eligibility_status"] == "ELIGIBLE":
            candidates.append(list(combination))
            if len(candidates) >= limit:
                break
        else:
            if metrics is not None:
                metrics["rejected_candidate_count"] = (
                    metrics.get("rejected_candidate_count", 0) + 1
                )
            if rejected_candidates is not None and len(rejected_candidates) < 100:
                rejected_candidates.append(
                    {
                        "outfit": list(combination),
                        "eligibility_status": "INELIGIBLE",
                        "validation_errors": eligibility["validation_errors"],
                        "validation_warnings": eligibility["validation_warnings"],
                    }
                )
    return candidates
