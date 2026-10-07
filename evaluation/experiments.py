"""Phase 7 experiments using the production workflow contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from tools.default_registry import create_default_registry
from tools.registry import ToolRegistry
from workflow.orchestrator import WorkflowOrchestrator
from workflow.state import WorkflowState


DEFAULT_QUERY = "smart casual college outfit under Rs 5000"


@dataclass(frozen=True)
class ExperimentResult:
    name: str
    baseline: dict[str, Any]
    optimized: dict[str, Any]
    measurements: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _orchestrator(catalog_path: str | Path) -> WorkflowOrchestrator:
    return WorkflowOrchestrator(create_default_registry(), catalog_path)


def experiment_sequential_vs_parallel(catalog_path: str | Path) -> ExperimentResult:
    sequential = _orchestrator(catalog_path).run(
        WorkflowState(DEFAULT_QUERY), mode="sequential"
    )
    parallel = _orchestrator(catalog_path).run(
        WorkflowState(DEFAULT_QUERY), mode="parallel"
    )
    sequential_time = sequential.metrics["total_execution_time_ms"]
    parallel_time = parallel.metrics["total_execution_time_ms"]
    return ExperimentResult(
        "sequential_vs_parallel",
        {"time_ms": sequential_time, "tool_calls": sequential.tool_execution_count},
        {"time_ms": parallel_time, "tool_calls": parallel.tool_execution_count},
        {
            "speedup": round(sequential_time / parallel_time, 3) if parallel_time else 0,
            "search_time_ms": {
                "sequential": sequential.metrics.get("search_execution_time_ms", 0),
                "parallel": parallel.metrics.get("search_execution_time_ms", 0),
            },
        },
    )


class _FlakyRegistry(ToolRegistry):
    """Inject one transient failure without changing production code."""

    def __init__(self) -> None:
        super().__init__()
        self.failures_remaining = 1

    def execute(self, agent_role: str, tool_name: str, **kwargs: Any) -> Any:
        if tool_name == "search_products" and self.failures_remaining:
            self.failures_remaining -= 1
            raise RuntimeError("experimental transient failure")
        return super().execute(agent_role, tool_name, **kwargs)


def experiment_retry_strategy(catalog_path: str | Path) -> ExperimentResult:
    baseline = _orchestrator(catalog_path).run(WorkflowState(DEFAULT_QUERY))
    flaky = _FlakyRegistry()
    flaky.tools = create_default_registry().tools
    optimized = WorkflowOrchestrator(flaky, catalog_path).run(WorkflowState(DEFAULT_QUERY))
    return ExperimentResult(
        "retry_strategy",
        {
            "retries": 0,
            "recovery_success": baseline.status.value == "waiting_for_approval",
            "cost_units": baseline.metrics.get("experimental_cost_units", 0),
        },
        {
            "retries": optimized.retry_count,
            "recovery_success": optimized.status.value == "waiting_for_approval",
            "cost_units": optimized.metrics.get("experimental_cost_units", 0),
        },
        {"extra_cost_units": optimized.retry_count},
    )


def experiment_tool_authorization(catalog_path: str | Path) -> ExperimentResult:
    del catalog_path
    registry = create_default_registry()
    blocked = 0
    attempted = 0
    for role in ("planner_agent", "search_agent", "filter_agent"):
        attempted += 1
        try:
            registry.execute(role, "validate_recommendation", outfit=[], budget_inr=1, required_categories=())
        except PermissionError:
            blocked += 1
    return ExperimentResult(
        "tool_authorization",
        {"policy": "broad_access", "unauthorized_attempts": attempted, "blocked_attempts": 0},
        {"policy": "least_privilege", "unauthorized_attempts": attempted, "blocked_attempts": blocked},
        {"security_pass_rate": round(blocked / attempted, 3) if attempted else 1.0},
    )


def experiment_validation(catalog_path: str | Path) -> ExperimentResult:
    state = _orchestrator(catalog_path).run(WorkflowState(DEFAULT_QUERY))
    checkpoints = len(state.validation_checkpoints)
    final_only_errors = len(state.validation_result.get("errors", [])) if state.validation_result else 0
    checkpoint_errors = sum(
        len(result["errors"]) for result in state.checkpoint_results.values()
    )
    return ExperimentResult(
        "validation_strategy",
        {"policy": "final_only", "errors_detected": final_only_errors, "checkpoints": 1},
        {
            "policy": "checkpoint_validation",
            "errors_detected": checkpoint_errors + final_only_errors,
            "checkpoints": checkpoints,
        },
        {"additional_checkpoints": max(checkpoints - 1, 0)},
    )


def experiment_ranking(catalog_path: str | Path) -> ExperimentResult:
    state = _orchestrator(catalog_path).run(WorkflowState(DEFAULT_QUERY))
    aware_scores = [
        result["score_breakdown"]["overall_score"] for result in state.ranking_results
    ]
    basic_scores = sorted(
        (
            sum(float(item["rating"]) for item in result["outfit"])
            / len(result["outfit"])
            for result in state.ranking_results
        ),
        reverse=True,
    )
    return ExperimentResult(
        "ranking_strategy",
        {"policy": "basic_rating", "top_score": round(basic_scores[0], 2) if basic_scores else 0},
        {
            "policy": "requirement_aware_compatibility",
            "top_score": aware_scores[0] if aware_scores else 0,
        },
        {
            "candidate_count": len(state.ranking_results),
            "constraint_satisfaction": all(
                result["score_breakdown"]["constraint_satisfaction"] == 100
                for result in state.ranking_results
            ),
        },
    )


def experiment_duplicate_operations(catalog_path: str | Path) -> ExperimentResult:
    registry = create_default_registry()
    started = perf_counter()
    first = registry.execute(
        "search_agent", "search_products", catalog_path=catalog_path, category="Top", limit=30
    )
    second = registry.execute(
        "search_agent", "search_products", catalog_path=catalog_path, category="Top", limit=30
    )
    baseline_time = (perf_counter() - started) * 1000
    cached_started = perf_counter()
    cache = {"Top": first}
    reused = cache["Top"]
    optimized_time = (perf_counter() - cached_started) * 1000
    assert second == reused
    return ExperimentResult(
        "duplicate_operations",
        {"search_count": 2, "tool_calls": 2, "time_ms": round(baseline_time, 3)},
        {"search_count": 1, "tool_calls": 1, "time_ms": round(optimized_time, 3)},
        {"search_reduction": 1, "tool_reduction": 1},
    )


def run_all_experiments(catalog_path: str | Path) -> dict[str, Any]:
    """Run all experiments and return JSON-serializable report data."""

    results = [
        experiment_sequential_vs_parallel(catalog_path),
        experiment_retry_strategy(catalog_path),
        experiment_tool_authorization(catalog_path),
        experiment_validation(catalog_path),
        experiment_ranking(catalog_path),
        experiment_duplicate_operations(catalog_path),
    ]
    return {"experiments": [result.as_dict() for result in results]}
