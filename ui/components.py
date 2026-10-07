"""Small reusable Streamlit rendering components."""

from typing import Any
from pathlib import Path

from ui.images import load_image_mapping, product_image


def render_requirements(st, state: Any) -> None:
    requirements = state.requirements
    if requirements is None:
        return
    colors = getattr(requirements, "preferred_colors", ())
    st.subheader("Your requirements")
    columns = st.columns(4)
    columns[0].metric("Budget", f"₹{requirements.budget_inr:,.0f}")
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


def _why_this_look(score: dict[str, Any]) -> str:
    parts = []
    for label, key in (
        ("style", "style_compatibility"),
        ("color", "color_compatibility"),
        ("occasion", "occasion_compatibility"),
        ("season", "season_compatibility"),
        ("coherence", "outfit_coherence"),
    ):
        value = float(score.get(key, 0))
        if value >= 80:
            parts.append(f"strong {label} compatibility")
    if score.get("constraint_satisfaction") == 100:
        parts.append("all hard constraints satisfied")
    return ", ".join(parts).capitalize() + "." if parts else "Validated using the deterministic compatibility rules."


def render_workflow_progress(st, state: Any) -> None:
    stages = (
        "security", "planning", "routing", "searching", "filtering",
        "building", "comparing", "ranking", "validating", "human_approval",
    )
    current = state.stage.value
    st.subheader("Workflow progress")
    for stage in stages:
        if stage == current:
            marker = "→"
        elif stage in {item["checkpoint"] for item in state.trace if item.get("event") == "checkpoint_validation"}:
            marker = "✓"
        else:
            marker = "•"
        st.write(f"{marker} {stage.replace('_', ' ').title()}")


def render_recommendations(st, state: Any) -> None:
    st.subheader("Recommended looks")
    if not state.ranking_results:
        st.info("No validated outfit candidates are available.")
        return
    columns = st.columns(min(2, len(state.ranking_results[:5])))
    for index, result in enumerate(state.ranking_results[:5]):
        score = result["score_breakdown"]
        with columns[index % len(columns)].container(border=True):
            status = result.get("eligibility_status", score.get("eligibility_status"))
            st.markdown(f"### Look #{result['rank']}")
            st.metric("Quality score", f"{score['overall_score']:.1f}/100")
            st.caption("✓ Validated" if status == "ELIGIBLE" else "Not eligible")
            products = result["outfit"]
            st.write(f"Total price: ₹{sum(float(item['price_inr']) for item in products):,.0f}")
            image_mapping = load_image_mapping(
                Path(__file__).parents[1] / "data" / "product_images.json"
            )
            for item in products:
                image, image_caption = product_image(
                    item, image_mapping, Path(__file__).parents[1]
                )
                if image:
                    st.image(image, caption=image_caption, use_container_width=True)
                else:
                    st.caption(image_caption)
                st.markdown(f"**{item['name']}** · {item['category']}")
                st.write(
                    f"Price: ₹{float(item['price_inr']):,.0f}"
                )
            st.success("Validated outfit" if status == "ELIGIBLE" else "Validation failed")
            st.caption("Why this look? " + _why_this_look(score))
            with st.expander("Score breakdown"):
                st.json(score)


def render_system_dashboard(st, state: Any) -> None:
    """Teacher-facing observability view over the same WorkflowState."""

    tabs = st.tabs(
        ["Overview", "Workflow", "Agents", "Tools", "Security", "Performance", "Optimization", "Evaluation", "Trace"]
    )
    with tabs[0]:
        st.subheader("System overview")
        st.write(f"Workflow: **{state.status.value.upper()}**")
        validation = state.validation_result or {}
        st.write(f"Validation: **{validation.get('status', 'NOT RUN')}**")
        render_metrics(st, state)
    with tabs[1]:
        render_workflow_progress(st, state)
        st.dataframe(
            [
                {
                    "event": item.get("event"),
                    "agent": item.get("agent"),
                    "duration_ms": item.get("duration_ms"),
                    "status": item.get("status", "completed"),
                    "tool": item.get("tool"),
                }
                for item in state.trace
                if item.get("event") in {"agent_completed", "tool_call", "checkpoint_validation"}
            ],
            use_container_width=True,
        )
    with tabs[2]:
        st.dataframe(
            [
                {
                    "agent": item.get("agent"),
                    "status": item.get("event"),
                    "duration_ms": item.get("duration_ms", 0),
                }
                for item in state.trace
                if item.get("event") in {"agent_completed", "agent_failed"}
            ],
            use_container_width=True,
        )
    with tabs[3]:
        from tools.default_registry import create_default_registry
        registry = create_default_registry()
        st.dataframe(
            [
                {
                    "tool": metadata.name,
                    "description": metadata.description,
                    "allowed_agents": ", ".join(sorted(metadata.allowed_agents)),
                    "registered": True,
                }
                for metadata in registry.discover()
            ],
            use_container_width=True,
        )
        st.json(state.tool_calls)
    with tabs[4]:
        from security.evaluation import run_security_evaluation
        report = run_security_evaluation()
        st.metric("Extended security pass rate", report["extended_security_pass_rate"])
        st.dataframe(report["security_cases"], use_container_width=True)
        render_security(st, state)
    with tabs[5]:
        render_metrics(st, state)
        st.write(
            {
                "search_time_ms": state.metrics.get("search_execution_time_ms", 0),
                "cache_hits": state.metrics.get("cache_hits", 0),
                "cache_misses": state.metrics.get("cache_misses", 0),
            }
        )
    with tabs[6]:
        if st.button("Run measured optimization experiments"):
            from evaluation.experiments import run_all_experiments
            report = run_all_experiments(Path(__file__).parents[1] / "data" / "products.csv")
            st.session_state["optimization_report"] = report
        if st.session_state.get("optimization_report"):
            st.json(st.session_state["optimization_report"])
        else:
            st.info("Run the experiments to display measured baseline/optimized results.")
    with tabs[7]:
        st.info("Evaluation results are generated from the measured workflow and experiments.")
        if st.session_state.get("optimization_report"):
            st.json(st.session_state["optimization_report"])
    with tabs[8]:
        render_trace(st, state)


def render_metrics(st, state: Any) -> None:
    st.subheader("Execution metrics")
    values = {
        "Execution time (ms)": state.metrics.get("total_execution_time_ms", 0),
        "Agent executions": state.agent_execution_count,
        "Tool calls": state.tool_execution_count,
        "Retries": state.retry_count,
        "Experimental cost units": state.metrics.get("experimental_cost_units", 0),
    }
    columns = st.columns(len(values))
    for column, (label, value) in zip(columns, values.items()):
        column.metric(label, value)


def render_security(st, state: Any) -> None:
    st.subheader("Security status")
    if state.security_events:
        st.warning(f"{len(state.security_events)} security event(s)")
        st.json(state.security_events)
    else:
        st.success("No security violations recorded")


def render_trace(st, state: Any) -> None:
    st.subheader("Workflow trace")
    st.dataframe(state.trace, use_container_width=True)
