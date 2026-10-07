"""Phase 4 workflow orchestration for sequential and parallel execution."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter

from agents import (
    ComparisonAgent,
    FilterAgent,
    OutfitBuilderAgent,
    PlannerAgent,
    RankingAgent,
    RouterAgent,
    SearchAgent,
    SupervisorAgent,
    ValidatorAgent,
)
from tools.registry import ToolRegistry
from config import DEFAULT_CONFIG
from workflow.checkpoints import validate_checkpoint
from workflow.synchronization import synchronize_search_results
from workflow.state import WorkflowStage, WorkflowState, WorkflowStatus
from services.gemini_advisor import review_outfit


class WorkflowOrchestrator:
    """Coordinates agents without embedding business logic in the UI."""

    def __init__(
        self,
        registry: ToolRegistry,
        catalog_path: str | Path,
        use_gemini: bool = False,
    ) -> None:
        self.registry = registry
        self.catalog_path = catalog_path
        self.use_gemini = use_gemini

    def run(self, state: WorkflowState, mode: str = "parallel") -> WorkflowState:
        if mode not in {"sequential", "parallel"}:
            raise ValueError("mode must be 'sequential' or 'parallel'")
        started = perf_counter()
        try:
            result = self._run_pipeline(state, parallel=mode == "parallel")
        except Exception as error:
            state.status = WorkflowStatus.FAILED
            state.stage = WorkflowStage.FAILED
            state.errors.append({"stage": state.stage.value, "error": str(error)})
            state.add_trace({"event": "workflow_failed", "error": str(error)})
            return state
        result.metrics["total_execution_time_ms"] = round((perf_counter() - started) * 1000, 3)
        result.metrics["execution_mode"] = mode
        result.add_trace({"event": "workflow_completed", "mode": mode})
        return result

    def _run_pipeline(self, state: WorkflowState, parallel: bool) -> WorkflowState:
        PlannerAgent(self.registry).execute(state)
        validate_checkpoint(state, "plan")
        RouterAgent(self.registry).execute(state)
        if state.routing_plan is None:
            raise ValueError("Router did not produce a routing plan")
        state.transition(WorkflowStage.SEARCHING, WorkflowStatus.RUNNING)
        search_agent = SearchAgent(self.registry, self.catalog_path)
        categories = state.routing_plan.search_categories
        search_started = perf_counter()
        if parallel:
            with ThreadPoolExecutor(max_workers=len(categories)) as executor:
                futures = {
                    category: executor.submit(self._search_with_retry, search_agent, state, category)
                    for category in categories
                }
                branches = {category: future.result() for category, future in futures.items()}
        else:
            branches = {
                category: self._search_with_retry(search_agent, state, category)
                for category in categories
            }
        state.metrics["search_execution_time_ms"] = round(
            (perf_counter() - search_started) * 1000, 3
        )
        synchronize_search_results(state, categories, branches)
        FilterAgent(self.registry).execute(state)
        validate_checkpoint(state, "filter")
        OutfitBuilderAgent(self.registry).execute(state)
        ComparisonAgent(self.registry).execute(state)
        RankingAgent(self.registry).execute(state)
        validate_checkpoint(state, "ranking")
        self._add_advisory_reviews(state)
        ValidatorAgent(self.registry).execute(state)
        SupervisorAgent(self.registry).execute(state)
        state.metrics["experimental_cost_units"] = (
            state.agent_execution_count * DEFAULT_CONFIG.agent_cost_units
            + state.tool_execution_count * DEFAULT_CONFIG.tool_cost_units
            + state.retry_count * DEFAULT_CONFIG.retry_cost_units
        )
        return state

    def _add_advisory_reviews(self, state: WorkflowState) -> None:
        """Ask Gemini for bounded explanations without changing deterministic results."""

        if not self.use_gemini or state.requirements is None:
            return
        requirements = {
            "budget_inr": state.requirements.budget_inr,
            "occasion": state.requirements.occasion,
            "categories": state.requirements.required_categories,
            "style": state.requirements.style,
            "colors": state.requirements.preferred_colors,
            "season": state.requirements.season,
        }
        for result in state.ranking_results[:3]:
            if result.get("eligibility_status") != "ELIGIBLE":
                continue
            advice = review_outfit(result["outfit"], requirements)
            result["gemini_advice"] = advice
            state.llm_advice.append(
                {"rank": result["rank"], "status": advice.get("status", "UNAVAILABLE")}
            )
        state.add_trace(
            {
                "event": "advisory_review_completed",
                "provider": "gemini",
                "reviewed": len(state.llm_advice),
            }
        )

    def _search_with_retry(
        self, search_agent: SearchAgent, state: WorkflowState, category: str
    ) -> list[dict[str, object]]:
        for attempt in range(DEFAULT_CONFIG.max_retries + 1):
            try:
                return search_agent.search_category(state, category)
            except Exception as error:
                if attempt >= DEFAULT_CONFIG.max_retries:
                    raise
                state.record_retry(f"search:{category}", str(error))
                state.add_trace(
                    {"event": "retry_started", "stage": f"search:{category}", "attempt": attempt + 1}
                )
        raise RuntimeError("Unreachable retry state")
