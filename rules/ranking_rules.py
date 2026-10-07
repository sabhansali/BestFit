"""Deterministic ranking helpers."""

from __future__ import annotations

from typing import Iterable, Sequence

from rules.scoring_rules import ScoreBreakdown, score_products


def rank_outfits(
    outfits: Iterable[Sequence[dict[str, object]]],
    required_categories: Sequence[str],
    **requirements: object,
) -> list[tuple[Sequence[dict[str, object]], ScoreBreakdown]]:
    """Return outfits ordered by score, with stable product-id tie breaking."""

    scored = [
        (outfit, score_products(outfit, required_categories, **requirements))
        for outfit in outfits
    ]
    return sorted(
        scored,
        key=lambda item: (
            item[1].eligibility_status != "ELIGIBLE",
            -item[1].overall_score,
            tuple(str(product.get("product_id", "")) for product in item[0]),
        ),
    )
