"""Catalog search tool."""

import csv
from pathlib import Path
from typing import Any


def search_products(
    catalog_path: str | Path,
    category: str,
    limit: int = 30,
    gender: str | None = None,
) -> list[dict[str, Any]]:
    if limit <= 0:
        raise ValueError("Search limit must be positive")
    with Path(catalog_path).open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file)
        results = [
            row for row in rows
            if row["category"].strip().lower() == category.strip().lower()
            and (gender is None or row["gender"].strip().lower() == gender.strip().lower())
        ]
    return results[:limit]
