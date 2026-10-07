"""Hard eligibility checks for complete outfits."""

from __future__ import annotations

from typing import Any, Iterable

from rules.compatibility_rules import (
    occasions_compatible,
    products_compatible,
    seasons_compatible,
    styles_compatible,
)


def validate_outfit(
    outfit: Iterable[dict[str, Any]],
    required_categories: Iterable[str],
    budget_inr: float | None = None,
    occasion: str | None = None,
    gender: str | None = None,
    season: str | None = None,
    preferred_colors: Iterable[str] = (),
    hard_color_constraint: bool = False,
) -> dict[str, Any]:
    """Return an explainable, deterministic hard-eligibility result."""

    products = list(outfit)
    errors: list[str] = []
    warnings: list[str] = []
    categories = {str(item.get("category", "")).strip().lower() for item in products}
    required = {str(category).strip().lower() for category in required_categories}
    ids = [item.get("product_id") for item in products]
    genders = {
        str(item.get("gender", "")).strip().lower()
        for item in products
        if item.get("gender")
    }
    try:
        total_price = sum(float(item.get("price_inr", 0)) for item in products)
    except (TypeError, ValueError):
        total_price = 0.0
        errors.append("invalid_price")

    if not products:
        errors.append("empty_outfit")
    if not required.issubset(categories):
        errors.append("missing_required_category")
    if budget_inr is not None and total_price > budget_inr:
        errors.append("budget")
    if any(not item.get("product_id") for item in products):
        errors.append("product_existence")
    if len(ids) != len(set(ids)):
        errors.append("duplicate_products")
    if gender and any(
        product_gender not in {gender.lower(), "unisex"} for product_gender in genders
    ):
        errors.append("gender")
    if len(genders - {"unisex"}) > 1:
        errors.append("gender_coherence")
    if not products_compatible(products):
        errors.append("pairwise_compatibility")

    for first_index, first in enumerate(products):
        for second in products[first_index + 1:]:
            if not styles_compatible(first.get("style", ""), second.get("style", "")):
                errors.append("style_coherence")
            if not occasions_compatible(first.get("occasion", ""), second.get("occasion", "")):
                errors.append("occasion_coherence")
            if not seasons_compatible(first.get("season", ""), second.get("season", "")):
                errors.append("season_coherence")
            try:
                if abs(int(first.get("formality", 0)) - int(second.get("formality", 0))) > 1:
                    errors.append("formality_coherence")
            except (TypeError, ValueError):
                errors.append("formality_coherence")
    if occasion and any(
        not occasions_compatible(item.get("occasion", ""), occasion) for item in products
    ):
        errors.append("occasion")
    if season and any(
        str(item.get("season", "")).lower() not in {season.lower(), "all season"}
        for item in products
    ):
        errors.append("season")
    requested_colors = {str(color).strip().lower() for color in preferred_colors if color}
    if hard_color_constraint and requested_colors and any(
        str(item.get("color", "")).strip().lower() not in requested_colors
        for item in products
    ):
        errors.append("hard_color_constraint")

    unique_errors = sorted(set(errors))
    return {
        "eligibility_status": "ELIGIBLE" if not unique_errors else "INELIGIBLE",
        "validation_errors": unique_errors,
        "validation_warnings": sorted(set(warnings)),
        "total_price_inr": total_price,
        "checks": {
            "category_completeness": required.issubset(categories),
            "gender_coherence": len(genders - {"unisex"}) <= 1,
            "style_coherence": "style_coherence" not in unique_errors,
            "occasion_coherence": "occasion_coherence" not in unique_errors,
            "season_coherence": "season_coherence" not in unique_errors,
            "formality_coherence": "formality_coherence" not in unique_errors,
            "color_compatibility": "pairwise_compatibility" not in unique_errors,
            "duplicate_products": len(ids) == len(set(ids)),
            "budget_compliance": "budget" not in unique_errors,
            "required_categories": required.issubset(categories),
            "hard_color_constraint": "hard_color_constraint" not in unique_errors,
        },
    }
