"""Hard-constraint filtering tool."""

from typing import Any, Iterable


def filter_products(
    products: Iterable[dict[str, Any]],
    budget_inr: float | None,
    occasion: str | None = None,
    season: str | None = None,
    gender: str | None = None,
    preferred_color: str | None = None,
    preferred_colors: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    results = []
    occasion_aliases = {
        "casual": "casual outing",
        "casual outing": "casual outing",
    }
    normalized_occasion = occasion_aliases.get(occasion.lower(), occasion.lower()) if occasion else None
    for product in products:
        if budget_inr is not None and float(product["price_inr"]) > budget_inr:
            continue
        if occasion and product["occasion"].lower() != normalized_occasion:
            continue
        if season and product["season"].lower() not in {season.lower(), "all season"}:
            continue
        if gender and product["gender"].lower() not in {gender.lower(), "unisex"}:
            continue
        allowed_colors = {color.lower() for color in preferred_colors}
        if preferred_color:
            allowed_colors.add(preferred_color.lower())
        if allowed_colors and product["color"].lower() not in allowed_colors:
            continue
        results.append(product)
    return results
