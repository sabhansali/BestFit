"""Presentation-only product image lookup with safe category placeholders."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_image_mapping(path: str | Path) -> dict[str, str]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def product_image(
    product: dict[str, Any],
    mapping: dict[str, str],
    root: str | Path,
) -> tuple[str | None, str]:
    """Return an existing image path or an explanatory placeholder label."""

    relative = mapping.get(str(product.get("product_id", "")))
    if relative:
        candidate = Path(root) / relative
        if candidate.is_file():
            return str(candidate), "Illustrative product preview"
    gender = str(product.get("gender", "unisex")).strip().casefold()
    image_root = Path(root) / "assets" / "products"
    folders = [gender, "unisex"] if gender != "unisex" else ["unisex"]
    searchable = " ".join(
        str(product.get(key, ""))
        for key in ("name", "category", "subcategory", "color")
    ).casefold()
    searchable = re.sub(r"[^a-z0-9]+", " ", searchable).strip()
    words = set(searchable.split())
    image_candidates: list[Path] = []
    for folder in folders:
        directory = image_root / folder
        if directory.is_dir():
            image_candidates.extend(sorted(directory.glob("*.png")))
            image_candidates.extend(sorted(directory.glob("*.jpg")))
            image_candidates.extend(sorted(directory.glob("*.jpeg")))
    for candidate in image_candidates:
        stem_words = set(re.sub(r"[^a-z0-9]+", " ", candidate.stem.casefold()).split())
        if stem_words and stem_words.issubset(words):
            return str(candidate), "Product image"
    category = str(product.get("category", "Product"))
    placeholder = Path(root) / "assets" / "placeholders" / f"{category.casefold()}.svg"
    if placeholder.is_file():
        return str(placeholder), f"{category} illustrative placeholder"
    return None, f"{category} preview unavailable — illustrative placeholder"
