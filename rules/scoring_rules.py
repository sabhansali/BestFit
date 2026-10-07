"""Explainable score components for requirements and product/outfit candidates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from config import RankingWeights
from rules.compatibility_rules import (
    colors_compatible,
    products_compatible,
    styles_compatible,
)
from rules.eligibility_rules import validate_outfit


@dataclass(frozen=True)
class ScoreBreakdown:
    style_compatibility: float
    color_compatibility: float
    occasion_compatibility: float
    category_coordination: float
    formality_compatibility: float
    season_compatibility: float
    constraint_satisfaction: float
    overall_score: float
    product_quality: float = 0.0
    preference_match: float = 0.0
    outfit_coherence: float = 0.0
    eligibility_status: str = "ELIGIBLE"
    validation_errors: tuple[str, ...] = ()
    validation_warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "style_compatibility": self.style_compatibility,
            "color_compatibility": self.color_compatibility,
            "occasion_compatibility": self.occasion_compatibility,
            "category_coordination": self.category_coordination,
            "formality_compatibility": self.formality_compatibility,
            "season_compatibility": self.season_compatibility,
            "constraint_satisfaction": self.constraint_satisfaction,
            "overall_score": self.overall_score,
            "product_quality": self.product_quality,
            "preference_match": self.preference_match,
            "outfit_coherence": self.outfit_coherence,
            "eligibility_status": self.eligibility_status,
            "validation_errors": list(self.validation_errors),
            "validation_warnings": list(self.validation_warnings),
        }


def _percentage(matches: int, total: int) -> float:
    return 100.0 if total == 0 else round(100.0 * matches / total, 2)


def score_products(
    products: Sequence[Mapping[str, object]],
    required_categories: Sequence[str],
    budget_inr: float | None = None,
    preferred_color: str | None = None,
    preferred_colors: Sequence[str] = (),
    preferred_style: str | None = None,
    occasion: str | None = None,
    season: str | None = None,
    gender: str | None = None,
    hard_color_constraint: bool = False,
    weights: RankingWeights | None = None,
) -> ScoreBreakdown:
    """Score an outfit using only deterministic product and requirement data."""

    if not products:
        return ScoreBreakdown(0, 0, 0, 0, 0, 0, 0, 0, eligibility_status="INELIGIBLE")
    weights = weights or RankingWeights()
    eligibility = validate_outfit(
        products, required_categories, budget_inr, occasion, gender, season,
        preferred_colors, hard_color_constraint
    )
    categories = {str(product.get("category", "")).lower() for product in products}
    required = {category.lower() for category in required_categories}
    style = _percentage(
        sum(
            styles_compatible(str(products[0].get("style", "")), str(product.get("style", "")))
            for product in products[1:]
        ),
        max(len(products) - 1, 1),
    )
    color = _percentage(
        sum(
            colors_compatible(str(products[0].get("color", "")), str(product.get("color", "")))
            for product in products[1:]
        ),
        max(len(products) - 1, 1),
    )
    occasion_score = _percentage(
        sum(
            str(product.get("occasion", "")).lower() == str(occasion).lower()
            for product in products
        )
        if occasion
        else len(products),
        len(products),
    )
    season_score = _percentage(
        sum(
            str(product.get("season", "")).lower() in {str(season).lower(), "all season"}
            for product in products
        )
        if season
        else len(products),
        len(products),
    )
    formality_values = [int(product.get("formality", 0)) for product in products]
    formality_score = _percentage(
        sum(abs(value - formality_values[0]) <= 1 for value in formality_values[1:]),
        max(len(formality_values) - 1, 1),
    )
    category_score = _percentage(len(categories.intersection(required)), len(required))
    constraint_score = 100.0 if eligibility["eligibility_status"] == "ELIGIBLE" else 0.0
    color_preferences = {color.lower() for color in preferred_colors}
    if preferred_color:
        color_preferences.add(preferred_color.lower())
    if color_preferences:
        color = round((color + _percentage(
            sum(str(product.get("color", "")).lower() in color_preferences for product in products),
            len(products),
        )) / 2, 2)
    if preferred_style:
        style = round((style + _percentage(
            sum(str(product.get("style", "")).lower() == preferred_style.lower() for product in products),
            len(products),
        )) / 2, 2)
    quality = round(
        sum(min(max(float(product.get("rating", 0)), 0), 5) for product in products)
        / max(len(products), 1)
        * 20,
        2,
    )
    preference = _percentage(
        sum(
            (not preferred_style or str(product.get("style", "")).lower() == preferred_style.lower())
            and (
                not color_preferences
                or str(product.get("color", "")).lower() in color_preferences
            )
            for product in products
        ),
        len(products),
    )
    coherence = _percentage(
        sum(products_compatible(products) for _ in [0]),
        1,
    )
    weighted = (
        style * weights.style
        + color * weights.color
        + occasion_score * weights.occasion
        + category_score * weights.category
        + formality_score * weights.formality
        + season_score * weights.season
        + constraint_score * weights.constraints
        + quality * weights.product_quality
        + preference * weights.preference_match
        + coherence * weights.outfit_coherence
    ) / weights.total
    return ScoreBreakdown(
        style,
        color,
        occasion_score,
        category_score,
        formality_score,
        season_score,
        constraint_score,
        round(weighted if eligibility["eligibility_status"] == "ELIGIBLE" else 0.0, 2),
        quality,
        preference,
        coherence,
        eligibility["eligibility_status"],
        tuple(eligibility["validation_errors"]),
        tuple(eligibility["validation_warnings"]),
    )
