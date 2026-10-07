"""Explicit, deterministic compatibility rules for fashion products."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable, Mapping


COLOR_COMPATIBILITY: Mapping[str, frozenset[str]] = {
    "black": frozenset({"black", "white", "grey", "gray", "navy", "beige", "red"}),
    "white": frozenset({"black", "white", "navy", "blue", "grey", "gray", "beige", "brown"}),
    "navy": frozenset({"black", "white", "beige", "brown", "grey", "gray", "blue"}),
    "blue": frozenset({"white", "navy", "beige", "brown", "grey", "gray"}),
    "grey": frozenset({"black", "white", "navy", "blue", "red", "maroon", "beige"}),
    "gray": frozenset({"black", "white", "navy", "blue", "red", "maroon", "beige"}),
    "beige": frozenset({"black", "white", "navy", "blue", "brown", "maroon", "olive"}),
    "brown": frozenset({"white", "navy", "blue", "beige", "cream", "olive"}),
    "cream": frozenset({"brown", "navy", "black", "olive", "maroon"}),
    "red": frozenset({"black", "white", "grey", "gray", "navy", "beige"}),
    "maroon": frozenset({"black", "white", "grey", "gray", "beige", "cream"}),
    "olive": frozenset({"black", "white", "beige", "brown", "cream", "navy"}),
    "pink": frozenset({"white", "black", "grey", "gray", "navy", "beige"}),
    "yellow": frozenset({"black", "white", "navy", "brown", "beige"}),
    "orange": frozenset({"black", "white", "navy", "brown", "beige"}),
    "purple": frozenset({"black", "white", "grey", "gray", "beige"}),
}

STYLE_COMPATIBILITY: Mapping[str, frozenset[str]] = {
    "casual": frozenset({"casual", "smart casual", "sporty"}),
    "smart casual": frozenset({"casual", "smart casual", "formal"}),
    "formal": frozenset({"smart casual", "formal", "party"}),
    "party": frozenset({"formal", "party", "smart casual"}),
    "sporty": frozenset({"casual", "sporty"}),
}

OCCASION_COMPATIBILITY: Mapping[str, frozenset[str]] = {
    "college": frozenset({"college", "casual", "farewell"}),
    "farewell": frozenset({"farewell", "college", "party"}),
    "party": frozenset({"party", "farewell"}),
    "office": frozenset({"office", "formal"}),
    "wedding": frozenset({"wedding", "party", "formal"}),
    "casual": frozenset({"casual", "college"}),
}

FORMALITY_COMPATIBILITY: Mapping[int, frozenset[int]] = {
    1: frozenset({1, 2}),
    2: frozenset({1, 2, 3}),
    3: frozenset({2, 3, 4}),
    4: frozenset({3, 4, 5}),
    5: frozenset({4, 5}),
}

SEASON_COMPATIBILITY: Mapping[str, frozenset[str]] = {
    "summer": frozenset({"summer", "all season"}),
    "winter": frozenset({"winter", "all season"}),
    "monsoon": frozenset({"monsoon", "all season"}),
    "spring": frozenset({"spring", "summer", "all season"}),
    "autumn": frozenset({"autumn", "winter", "all season"}),
    "all season": frozenset({"all season", "summer", "winter", "monsoon", "spring", "autumn"}),
}


def _normalize(value: object) -> str:
    return str(value).strip().lower()


def _pair_compatible(
    first: str,
    second: str,
    table: Mapping[str, frozenset[str]],
) -> bool:
    first_normalized = _normalize(first)
    second_normalized = _normalize(second)
    return (
        first_normalized == second_normalized
        or second_normalized in table.get(first_normalized, frozenset())
        or first_normalized in table.get(second_normalized, frozenset())
    )


def colors_compatible(first: str, second: str) -> bool:
    return _pair_compatible(first, second, COLOR_COMPATIBILITY)


def styles_compatible(first: str, second: str) -> bool:
    return _pair_compatible(first, second, STYLE_COMPATIBILITY)


def occasions_compatible(first: str, second: str) -> bool:
    return _pair_compatible(first, second, OCCASION_COMPATIBILITY)


def formality_compatible(first: int, second: int) -> bool:
    return abs(int(first) - int(second)) <= 1


def seasons_compatible(first: str, second: str) -> bool:
    return _pair_compatible(first, second, SEASON_COMPATIBILITY)


def products_compatible(products: Iterable[Mapping[str, object]]) -> bool:
    """Return whether every product pair coordinates on all shared dimensions."""

    product_list = list(products)
    for first, second in combinations(product_list, 2):
        if not colors_compatible(first.get("color", ""), second.get("color", "")):
            return False
        if not styles_compatible(first.get("style", ""), second.get("style", "")):
            return False
        if not occasions_compatible(first.get("occasion", ""), second.get("occasion", "")):
            return False
        if not formality_compatible(
            int(first.get("formality", 0)),
            int(second.get("formality", 0)),
        ):
            return False
        if not seasons_compatible(first.get("season", ""), second.get("season", "")):
            return False
    return True
