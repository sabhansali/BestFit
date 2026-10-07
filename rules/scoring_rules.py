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

    def as_dict(self) -> dict[str, float]:
        return {
            "style_compatibility": self.style_compatibility,
            "color_compatibility": self.color_compatibility,
            "occasion_compatibility": self.occasion_compatibility,
            "category_coordination": self.category_coordination,
            "formality_compatibility": self.formality_compatibility,
            "season_compatibility": self.season_compatibility,
            "constraint_satisfaction": self.constraint_satisfaction,
            "overall_score": self.overall_score,
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
    weights: RankingWeights | None = None,
) -> ScoreBreakdown:
    """Score an outfit using only deterministic product and requirement data."""

    if not products:
        return ScoreBreakdown(0, 0, 0, 0, 0, 0, 0, 0)
    weights = weights or RankingWeights()
    categories = {str(product.get("category", "")).lower() for product in products}
    required = {category.lower() for category in required_categories}
    total_price = sum(float(product.get("price_inr", 0)) for product in products)
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
    constraint_score = 100.0 if (budget_inr is None or total_price <= budget_inr) else 0.0
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
    if not products_compatible(products):
        constraint_score = min(constraint_score, 0.0)
    weighted = (
        style * weights.style
        + color * weights.color
        + occasion_score * weights.occasion
        + category_score * weights.category
        + formality_score * weights.formality
        + season_score * weights.season
        + constraint_score * weights.constraints
    ) / weights.total
    return ScoreBreakdown(
        style,
        color,
        occasion_score,
        category_score,
        formality_score,
        season_score,
        constraint_score,
        round(weighted, 2),
    )
