from pathlib import Path

from agents.agents import _normalize_intent
from ui.images import load_image_mapping, product_image


ROOT = Path(__file__).parents[1]


def test_common_intent_misspelling_is_normalized() -> None:
    assert "summer dresses" in _normalize_intent("summery dresses")


def test_missing_product_image_returns_safe_placeholder() -> None:
    item = {"product_id": "missing", "category": "Top"}
    image, caption = product_image(item, load_image_mapping(ROOT / "data" / "product_images.json"), ROOT)
    assert image is not None
    assert "illustrative placeholder" in caption
