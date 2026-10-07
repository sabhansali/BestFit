"""Streamlit entry point for the e-commerce outfit recommendation system."""

import streamlit as st

from ui.recommendation_view import render_approval_controls
from ui.requirements_view import render_requirements
from ui.recommendations_view import render_recommendations
from ui.dashboard_view import render_system_dashboard
from ui.workflow_view import execute_query


st.set_page_config(
    page_title="E-Commerce Outfit Recommendation Agent",
    page_icon="👔",
    layout="wide",
)

st.markdown(
    """
    <style>
    .hero { padding: 1.5rem 0 0.75rem; }
    .hero h1 { margin-bottom: 0.25rem; }
    .hero p { color: #64748b; font-size: 1.05rem; }
    </style>
    <div class="hero">
      <h1>Outfit Recommendation Agent</h1>
      <p>Find a complete look based on your style, occasion, and budget.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Query panel")
    view = st.radio("View", ("Client", "System Dashboard"), index=0)
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
        with st.spinner("Finding compatible looks..."):
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
    if view == "Client":
        render_requirements(st, state)
        render_recommendations(st, state)
        decision = render_approval_controls(st, state)
        if decision == "approved":
            st.success("Recommendation approved.")
            st.rerun()
        if decision == "rejected":
            st.warning("Targeted re-analysis was recorded.")
            st.rerun()
    else:
        render_system_dashboard(st, state)
