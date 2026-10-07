"""Basic recommendation validation tool."""

from typing import Any


def validate_recommendation(
    outfit: list[dict[str, Any]],
    budget_inr: float,
    required_categories: tuple[str, ...],
) -> dict[str, Any]:
    categories = {item["category"] for item in outfit}
    ids = [item["product_id"] for item in outfit]
    checks = {
        "budget": sum(float(item["price_inr"]) for item in outfit) <= budget_inr,
        "required_categories": set(required_categories).issubset(categories),
        "product_existence": all(bool(item.get("product_id")) for item in outfit),
        "duplicate_products": len(ids) == len(set(ids)),
    }
    errors = [name for name, passed in checks.items() if not passed]
    return {"status": "PASSED" if not errors else "FAILED", "errors": errors, "warnings": [], "checks": checks}
