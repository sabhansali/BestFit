"""Client-facing rendering for interpreted user requirements."""

from __future__ import annotations

from typing import Any


def render_requirements(st: Any, state: Any) -> None:
    requirements = state.requirements
    if requirements is None:
        return
    colors = getattr(requirements, "preferred_colors", ())
    st.subheader("Your requirements")
    columns = st.columns(4)
    columns[0].metric(
        "Budget",
        f"₹{requirements.budget_inr:,.0f}"
        if requirements.budget_inr is not None
        else "Not specified",
    )
    columns[1].metric("Occasion", requirements.occasion or "Not specified")
    columns[2].metric("Style", requirements.style or "Not specified")
    columns[3].metric("Colors", " + ".join(colors) if colors else "Not specified")
    st.caption(
        f"Gender: {requirements.gender or 'Not specified'}  ·  "
        f"Season: {requirements.season or 'Not specified'}"
    )
    st.write("Required categories")
    st.write("  ".join(f"✓ {category}" for category in requirements.required_categories))
    with st.expander("View structured requirements"):
        st.json(
            {
                "budget_inr": requirements.budget_inr,
                "occasion": requirements.occasion,
                "style": requirements.style,
                "preferred_colors": colors,
                "gender": requirements.gender,
                "season": requirements.season,
                "required_categories": requirements.required_categories,
            }
        )
