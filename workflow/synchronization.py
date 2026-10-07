"""Synchronization and integrity checks for parallel search branches."""

from __future__ import annotations

from typing import Any

from workflow.state import WorkflowState


def synchronize_search_results(
    state: WorkflowState,
    expected_categories: tuple[str, ...],
    branches: dict[str, list[dict[str, Any]]],
) -> None:
    """Validate and merge independent search branches into shared state."""

    errors: list[str] = []
    missing = [category for category in expected_categories if category not in branches]
    if missing:
        errors.append(f"Missing search branches: {', '.join(missing)}")
    for category, products in branches.items():
        if not isinstance(products, list):
            errors.append(f"Malformed result for category: {category}")
            continue
        product_ids = [product.get("product_id") for product in products]
        if any(not product_id for product_id in product_ids):
            errors.append(f"Missing product ID in category: {category}")
        if len(product_ids) != len(set(product_ids)):
            errors.append(f"Duplicate product result in category: {category}")
    if errors:
        state.errors.extend({"stage": "synchronization", "error": error} for error in errors)
        state.add_trace({"event": "synchronization_failed", "errors": errors})
        raise ValueError("; ".join(errors))
    state.search_results = dict(branches)
    state.add_trace(
        {
            "event": "synchronization_completed",
            "categories": list(expected_categories),
            "result_counts": {category: len(branches[category]) for category in expected_categories},
        }
    )
