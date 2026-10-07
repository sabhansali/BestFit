"""Stable teacher-facing dashboard renderer independent of components.py."""

from pathlib import Path
from typing import Any

from security.evaluation import run_security_evaluation
from tools.default_registry import create_default_registry
from evaluation.experiments import run_all_experiments


def _metrics(streamlit: Any, state: Any) -> None:
    values = {
        "Execution (ms)": state.metrics.get("total_execution_time_ms", 0),
        "Agents": state.agent_execution_count,
        "Tools": state.tool_execution_count,
        "Retries": state.retry_count,
        "Cost units": state.metrics.get("experimental_cost_units", 0),
    }
    columns = streamlit.columns(len(values))
    for column, (label, value) in zip(columns, values.items()):
        column.metric(label, value)


def _timeline(streamlit: Any, state: Any) -> None:
    streamlit.subheader("Workflow timeline")
    rows = []
    for event in state.trace:
        if event.get("event") in {"agent_completed", "agent_failed", "tool_call"}:
            rows.append(
                {
                    "event": event.get("event"),
                    "agent": event.get("agent"),
                    "tool": event.get("tool"),
                    "duration_ms": event.get("duration_ms", 0),
                    "status": event.get("status", "completed"),
                }
            )
    streamlit.dataframe(rows, use_container_width=True)


def render_system_dashboard(streamlit: Any, state: Any) -> None:
    tabs = streamlit.tabs(
        ["Overview", "Workflow", "Agents", "Tools", "Security",
         "Performance", "Optimization", "Evaluation", "Trace"]
    )
    with tabs[0]:
        streamlit.subheader("System overview")
        streamlit.write(f"Workflow: **{state.status.value.upper()}**")
        streamlit.write(
            f"Validation: **{(state.validation_result or {}).get('status', 'NOT RUN')}**"
        )
        _metrics(streamlit, state)
        streamlit.subheader("Gemini planner usage")
        streamlit.json(getattr(state, "planner_usage", {}))
    with tabs[1]:
        _timeline(streamlit, state)
        streamlit.json(state.routing_plan.__dict__ if state.routing_plan else {})
    with tabs[2]:
        _timeline(streamlit, state)
    with tabs[3]:
        registry = create_default_registry()
        streamlit.dataframe(
            [
                {
                    "tool": item.name,
                    "description": item.description,
                    "allowed_agents": ", ".join(sorted(item.allowed_agents)),
                }
                for item in registry.discover()
            ],
            use_container_width=True,
        )
        streamlit.json(state.tool_calls)
    with tabs[4]:
        report = run_security_evaluation()
        streamlit.metric("Security pass rate", report["extended_security_pass_rate"])
        streamlit.dataframe(report["security_cases"], use_container_width=True)
        if state.security_events:
            streamlit.json(state.security_events)
        rejected = getattr(state, "rejected_candidates", [])
        with streamlit.expander("Rejected candidates"):
            streamlit.write(f"{len(rejected)} rejected candidate(s)")
            streamlit.json(rejected)
    with tabs[5]:
        _metrics(streamlit, state)
        streamlit.write(
            {
                "search_time_ms": state.metrics.get("search_execution_time_ms", 0),
                "cache_hits": state.metrics.get("cache_hits", 0),
                "cache_misses": state.metrics.get("cache_misses", 0),
            }
        )
    with tabs[6]:
        if streamlit.button("Run measured optimization experiments"):
            streamlit.session_state["optimization_report"] = run_all_experiments(
                Path(__file__).parents[1] / "data" / "products.csv"
            )
        streamlit.json(streamlit.session_state.get("optimization_report", {}))
    with tabs[7]:
        streamlit.info("Evaluation uses measured workflow and experiment outputs.")
        streamlit.json(streamlit.session_state.get("optimization_report", {}))
    with tabs[8]:
        streamlit.json(state.trace)
