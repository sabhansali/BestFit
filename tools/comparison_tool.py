"""Deterministic comparison tool for candidate outfits."""

from typing import Any


def compare_outfits(outfits: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": index,
            "product_ids": [item["product_id"] for item in outfit],
            "total_price_inr": sum(float(item["price_inr"]) for item in outfit),
        }
        for index, outfit in enumerate(outfits, start=1)
    ]
