"""Small reusable Streamlit rendering components."""

from typing import Any


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
    st.subheader("Ranked outfit recommendations")
    if not state.ranking_results:
        st.info("No validated outfit candidates are available.")
        return
    for result in state.ranking_results[:5]:
        score = result["score_breakdown"]
        with st.container(border=True):
            st.markdown(f"### Outfit #{result['rank']} — {score['overall_score']:.2f}/100")
            products = result["outfit"]
            st.write(f"Total price: ₹{sum(float(item['price_inr']) for item in products):,.0f}")
            st.markdown("#### Recommended products")
            for item in products:
                st.markdown(f"**{item['name']}**")
                st.write(
                    f"Product ID: `{item['product_id']}`  |  "
                    f"Category: {item['category']} / {item['subcategory']}  |  "
                    f"Price: ₹{float(item['price_inr']):,.0f}"
                )
                st.write(
                    f"Color: {item['color']} | Style: {item['style']} | "
                    f"Occasion: {item['occasion']} | Season: {item['season']} | "
                    f"Gender: {item['gender']}"
                )
                st.caption(
                    f"Brand: {item['brand']} | Material: {item['material']} | "
                    f"Rating: {item['rating']} ({item['review_count']} reviews)"
                )
                st.divider()
            st.json(score)


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
