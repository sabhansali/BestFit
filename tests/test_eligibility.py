from rules.eligibility_rules import validate_outfit
from tools.validation_tool import validate_recommendation


def item(product_id: str, category: str, gender: str = "Women") -> dict:
    return {
        "product_id": product_id,
        "category": category,
        "color": "Black",
        "style": "Formal",
        "occasion": "Office",
        "season": "Winter",
        "formality": 4,
        "gender": gender,
        "price_inr": 1000,
    }


def test_eligibility_checks_gender_coherence_and_context() -> None:
    result = validate_outfit(
        [item("1", "Top", "Women"), item("2", "Bottom", "Men")],
        ("Top", "Bottom"),
        budget_inr=3000,
        occasion="Office",
        season="Winter",
    )
    assert result["eligibility_status"] == "INELIGIBLE"
    assert "gender_coherence" in result["validation_errors"]


def test_validator_returns_structured_eligibility_fields() -> None:
    result = validate_recommendation(
        [item("1", "Top"), item("2", "Bottom")],
        3000,
        ("Top", "Bottom"),
        occasion="Office",
        season="Winter",
    )
    assert result["status"] == "PASSED"
    assert result["eligibility_status"] == "ELIGIBLE"
    assert "category_completeness" in result["checks"]
