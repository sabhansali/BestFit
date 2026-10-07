"""Streamlit entry point for the e-commerce outfit recommendation system."""

import streamlit as st

from ui.components import (
    render_metrics,
    render_recommendations,
    render_security,
    render_trace,
    render_workflow_progress,
)
from ui.recommendation_view import render_approval_controls
from ui.workflow_view import execute_query


st.set_page_config(
    page_title="E-Commerce Outfit Recommendation Agent",
    page_icon="👔",
    layout="wide",
)

st.title("E-Commerce Outfit Recommendation Agent")
st.caption("Multi-Agent AI | Workflow Orchestration | Deterministic Compatibility")

with st.sidebar:
    st.header("Query panel")
    query = st.text_area(
        "Describe your outfit request",
        value="Give me a smart casual college outfit under Rs 5000.",
        height=120,
    )
    mode = st.radio("Execution mode", ("parallel", "sequential"), index=0)
    generate = st.button("Generate outfit", type="primary", use_container_width=True)

if generate:
    if not query.strip():
        st.error("Please enter a fashion request.")
    else:
        with st.spinner("Running the multi-agent workflow..."):
            st.session_state["workflow_state"] = execute_query(query, mode)

state = st.session_state.get("workflow_state")
if state is None:
    st.info("Enter a request and select Generate outfit to start.")
else:
    if state.status.value == "failed":
        st.error("The workflow could not produce a valid recommendation.")
        if state.security_events:
            st.warning("The request was blocked by the security guardrail.")
        if state.errors:
            st.write("Reason:", state.errors[-1].get("error", "Unknown workflow error"))
    else:
        st.success(f"Workflow status: {state.status.value.replace('_', ' ').title()}")
    left, right = st.columns((1, 2))
    with left:
        st.subheader("Structured requirements")
        if state.requirements:
            st.json({
                "budget_inr": state.requirements.budget_inr,
                "occasion": state.requirements.occasion,
                "categories": state.requirements.required_categories,
                "style": state.requirements.style,
                "preferred_color": state.requirements.preferred_color,
                # Defaults keep an already-running Streamlit session compatible
                # with states created before the multi-color fields were added.
                "preferred_colors": getattr(
                    state.requirements,
                    "preferred_colors",
                    (state.requirements.preferred_color,)
                    if state.requirements.preferred_color
                    else (),
                ),
                "hard_color_constraint": getattr(
                    state.requirements, "hard_color_constraint", False
                ),
                "gender": state.requirements.gender,
                "season": state.requirements.season,
            })
        render_workflow_progress(st, state)
        render_security(st, state)
    with right:
        render_recommendations(st, state)
        if state.validation_result:
            st.subheader("Validation")
            st.json(state.validation_result)
        decision = render_approval_controls(st, state)
        if decision == "approved":
            st.success("Recommendation approved.")
            st.rerun()
        if decision == "rejected":
            st.warning("Recommendation rejected. Re-analysis is ready.")
            st.rerun()
    render_metrics(st, state)
    render_trace(st, state)
