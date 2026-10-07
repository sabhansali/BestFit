"""Stable client-facing recommendation renderer."""

from pathlib import Path
from typing import Any

from ui.images import load_image_mapping, product_image


def _why_this_look(score: dict[str, Any]) -> str:
    parts = []
    for label, key in (
        ("style", "style_compatibility"),
        ("color", "color_compatibility"),
        ("occasion", "occasion_compatibility"),
        ("season", "season_compatibility"),
        ("coherence", "outfit_coherence"),
    ):
        if float(score.get(key, 0)) >= 80:
            parts.append(f"strong {label} compatibility")
    if score.get("constraint_satisfaction") == 100:
        parts.append("all hard constraints satisfied")
    return ", ".join(parts).capitalize() + "." if parts else (
        "Validated using deterministic compatibility rules."
    )


def render_recommendations(streamlit: Any, state: Any) -> None:
    streamlit.subheader("Recommended looks")
    eligible_results = [
        result for result in state.ranking_results
        if result.get("eligibility_status", result["score_breakdown"].get("eligibility_status"))
        == "ELIGIBLE"
    ]
    if not eligible_results:
        streamlit.info("No validated outfit candidates are available.")
        return
    root = Path(__file__).parents[1]
    mapping = load_image_mapping(root / "data" / "product_images.json")
    columns = streamlit.columns(min(2, len(eligible_results[:5])))
    for index, result in enumerate(eligible_results[:5]):
        score = result["score_breakdown"]
        with columns[index % len(columns)].container(border=True):
            status = result.get("eligibility_status", score.get("eligibility_status"))
            streamlit.markdown(f"### Look #{result['rank']}")
            streamlit.metric("Quality score", f"{score['overall_score']:.1f}/100")
            streamlit.caption("Validated" if status == "ELIGIBLE" else "Not eligible")
            products = result["outfit"]
            total = sum(float(item["price_inr"]) for item in products)
            streamlit.write(f"Total price: ₹{total:,.0f}")
            for item in products:
                image, caption = product_image(item, mapping, root)
                if image:
                    streamlit.image(image, caption=caption, use_container_width=True)
                else:
                    streamlit.caption(caption)
                streamlit.markdown(f"**{item['name']}** · {item['category']}")
                streamlit.write(f"Price: ₹{float(item['price_inr']):,.0f}")
            streamlit.success("Validated outfit")
            streamlit.caption("Why this look? " + _why_this_look(score))
            with streamlit.expander("Score breakdown"):
                streamlit.json(score)
