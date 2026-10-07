"""Outfit construction tool."""

from itertools import product as cartesian_product
from typing import Any, Iterable, Sequence

from rules.compatibility_rules import products_compatible


def build_outfits(
    products_by_category: dict[str, Sequence[dict[str, Any]]],
    required_categories: Iterable[str],
    limit: int = 100,
    budget_inr: float | None = None,
) -> list[list[dict[str, Any]]]:
    categories = tuple(required_categories)
    if not categories:
        return []
    candidates = []
    for combination in cartesian_product(*(products_by_category.get(category, ()) for category in categories)):
        total_price = sum(float(item["price_inr"]) for item in combination)
        if (
            (budget_inr is None or total_price <= budget_inr)
            and len({item["product_id"] for item in combination}) == len(combination)
            and products_compatible(combination)
        ):
            candidates.append(list(combination))
            if len(candidates) >= limit:
                break
    return candidates
