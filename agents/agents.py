"""Phase 3 specialized agents with explicit shared-state contracts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from agents.base import Agent
from config import DEFAULT_CONFIG
from security.guardrails import validate_user_query
from security.state_validation import validate_state_update
from tools.registry import ToolRegistry
from services.gemini_advisor import extract_query_entities, gemini_configured
from workflow.state import (
    Plan,
    Requirements,
    RoutingPlan,
    WorkflowStage,
    WorkflowState,
    WorkflowStatus,
)


def _first_match(patterns: tuple[str, ...], query: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _extract_budget(query: str) -> float | None:
    match = re.search(
        r"(?:under|below|within|budget(?:\s+of)?|cost(?:ing)?|price)\s*"
        r"(?:is|of|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",
        query,
        re.IGNORECASE,
    )
    return float(match.group(1).replace(",", "")) if match else None


def _normalize_intent(query: str) -> str:
    """Normalize common misspellings and natural-language intent phrases."""

    normalized = query.casefold()
    replacements = {
        "summery": "summer",
        "sumer": "summer",
        "hot weather": "summer",
        "summertime": "summer",
        "warm weather": "summer",
        "sunny weather": "summer",
        "cold weather": "winter",
        "chilly weather": "winter",
        "rainy weather": "monsoon",
        "rainy season": "monsoon",
        "rainy weather": "monsoon",
        "cold season": "winter",
        "male": "men",
        "female": "women",
        "everyday dress": "casual dress",
        "campus wear": "college",
        "campus outfit": "college outfit",
        "workwear": "office",
        "work wear": "office",
        "evening party": "party",
        "night party": "party",
        "business casual": "smart casual",
    }
    for source, replacement in replacements.items():
        normalized = normalized.replace(source, replacement)
    return normalized


class PlannerAgent(Agent):
    name = "planner_agent"
    role = "planner_agent"

    def run(self, state: WorkflowState) -> None:
        allowed, findings = validate_user_query(state.user_query)
        if not allowed:
            state.security_events.extend({"event": "blocked_input", "finding": item} for item in findings)
            state.transition(WorkflowStage.SECURITY, WorkflowStatus.FAILED)
            raise ValueError("User query blocked by input guardrails")
        query = _normalize_intent(state.user_query)
        llm_entities: dict[str, Any] = {}
        if gemini_configured():
            extraction = extract_query_entities(state.user_query, timeout_seconds=2.0)
            state.planner_usage = {
                "provider": "Gemini",
                "configured_model": extraction.get("model")
                or "GEMINI_MODEL/default",
                "configured": True,
                "call_attempted": extraction.get("call_attempted", True),
                "call_succeeded": extraction.get("call_succeeded", False),
                "call_status": extraction.get("status", "UNAVAILABLE"),
                "fallback_used": extraction.get("status") != "AVAILABLE",
                "latency_ms": extraction.get("latency_ms"),
                "failure_type": extraction.get("failure_type"),
                "failure_message": extraction.get("failure_message"),
            }
            if extraction.get("status") == "AVAILABLE":
                llm_entities = extraction
            state.llm_advice.append(
                {"type": "entity_extraction", "status": extraction.get("status")}
            )
        else:
            state.planner_usage = {
                "provider": "Gemini",
                "configured_model": None,
                "configured": False,
                "call_attempted": False,
                "call_succeeded": False,
                "call_status": "NOT_CONFIGURED",
                "fallback_used": True,
                "latency_ms": 0.0,
                "failure_type": "configuration",
                "failure_message": "GEMINI_API_KEY is not configured",
            }
        budget = _extract_budget(query)
        category_aliases = {
            "top": "Top", "shirt": "Top", "blouse": "Top", "t-shirt": "Top",
            "bottom": "Bottom", "trouser": "Bottom", "trousers": "Bottom",
            "pants": "Bottom", "jeans": "Bottom",             "footwear": "Footwear", "shoe": "Footwear", "shoes": "Footwear",
            "accessory": "Accessory",
            "accessories": "Accessory", "dress": "Dress", "dresses": "Dress",
            "outerwear": "Outerwear",
            "jacket": "Outerwear",
        }
        categories = tuple(
            category for alias, category in category_aliases.items()
            if re.search(rf"\b{re.escape(alias)}\b", query, re.IGNORECASE)
        )
        llm_categories = {
            str(value).strip().title()
            for value in (llm_entities.get("categories") or [])
            if str(value).strip().title()
            in {"Top", "Bottom", "Footwear", "Accessory", "Dress", "Outerwear"}
        }
        categories = tuple(dict.fromkeys(categories or tuple(llm_categories))) or (
            "Top", "Bottom", "Footwear"
        )
        occasion = next(
            (
                value
                for value in ("college", "farewell", "party", "office", "wedding")
                if re.search(rf"\b{value}\b", query, re.IGNORECASE)
            ),
            str(llm_entities.get("occasion")).casefold()
            if llm_entities.get("occasion")
            else None,
        )
        valid_occasions = {
            "college", "farewell", "party", "office", "wedding"
        }
        if occasion and occasion.casefold() not in valid_occasions:
            occasion = None
        colors = tuple(
            dict.fromkeys(
                re.findall(
                    r"\b(black|white|navy|blue|grey|gray|beige|brown|red|maroon|olive|pink|green|cream)\b",
                    query,
                    flags=re.IGNORECASE,
                )
            )
        )
        requirements = Requirements(
            budget_inr=budget,
            occasion=occasion.title() if occasion else None,
            required_categories=categories,
            style=(
                _first_match((r"\b(smart casual|casual|formal|party|sporty)\b",), query)
                or (
                    str(llm_entities.get("style")).title()
                    if llm_entities.get("style") else None
                )
            ),
            preferred_color=colors[0].lower() if colors else None,
            preferred_colors=tuple(color.lower() for color in colors),
            hard_color_constraint=bool(
                re.search(r"\b(must|only|exactly|required)\b", query, re.IGNORECASE)
            ),
            gender=(
                _first_match((r"\b(men|'?s men|women|'?s women|unisex)\b",), query)
                or (str(llm_entities.get("gender")).title() if llm_entities.get("gender") else None)
            ),
            season=(
                _first_match((r"\b(summer|winter|monsoon|spring|autumn)\b",), query)
                or (
                    _normalize_intent(str(llm_entities.get("season"))).lower()
                    if llm_entities.get("season") else None
                )
            ),
        )
        if requirements.gender:
            normalized_gender = requirements.gender.casefold().replace("'s ", " ")
            if normalized_gender in {"men", "women", "unisex"}:
                requirements = Requirements(
                    budget_inr=requirements.budget_inr,
                    occasion=requirements.occasion,
                    required_categories=requirements.required_categories,
                    style=requirements.style,
                    preferred_color=requirements.preferred_color,
                    preferred_colors=requirements.preferred_colors,
                    hard_color_constraint=requirements.hard_color_constraint,
                    gender=normalized_gender.title(),
                    season=requirements.season,
                    formality=requirements.formality,
                )
        valid, errors = validate_state_update(state, requirements)
        if not valid:
            state.security_events.append({"event": "invalid_state_update", "errors": errors})
            raise ValueError("; ".join(errors))
        if state.requirements is not None and state.requirements != requirements:
            state.security_events.append(
                {"event": "conflict_resolved", "winner": "trusted_requirements"}
            )
            raise ValueError("Trusted requirements cannot be overwritten")
        state.requirements = requirements
        state.plan = Plan(requirements, rationale="Deterministic fallback planner")
        state.transition(WorkflowStage.PLANNING, WorkflowStatus.RUNNING)


class RouterAgent(Agent):
    name = "router_agent"
    role = "planner_agent"

    def run(self, state: WorkflowState) -> None:
        if state.plan is None:
            raise ValueError("Router requires a completed plan")
        state.routing_plan = RoutingPlan(state.plan.requirements.required_categories)
        state.transition(WorkflowStage.ROUTING, WorkflowStatus.RUNNING)


class SearchAgent(Agent):
    name = "search_agent"
    role = "search_agent"

    def __init__(self, registry: ToolRegistry, catalog_path: str | Path) -> None:
        super().__init__(registry)
        self.catalog_path = catalog_path

    def run(self, state: WorkflowState) -> None:
        if state.routing_plan is None or state.requirements is None:
            raise ValueError("Search requires routing and requirements")
        state.transition(WorkflowStage.SEARCHING, WorkflowStatus.RUNNING)
        for category in state.routing_plan.search_categories:
            state.search_results[category] = self.search_category(state, category)

    def search_category(self, state: WorkflowState, category: str) -> list[dict[str, Any]]:
        """Search one independent category branch for the orchestrator."""

        if state.requirements is None:
            raise ValueError("Search requires requirements")
        return self.call_tool(
            state,
            "search_products",
            catalog_path=self.catalog_path,
            category=category,
            limit=DEFAULT_CONFIG.max_candidates_per_category,
            gender=state.requirements.gender,
        )


class FilterAgent(Agent):
    name = "filter_agent"
    role = "filter_agent"

    def run(self, state: WorkflowState) -> None:
        if state.requirements is None:
            raise ValueError("Filter requires requirements")
        state.transition(WorkflowStage.FILTERING, WorkflowStatus.RUNNING)
        for category, products in state.search_results.items():
            state.filtered_results[category] = self.call_tool(
                state, "filter_products", products=products,
                budget_inr=state.requirements.budget_inr,
                occasion=state.requirements.occasion,
                season=state.requirements.season,
                gender=state.requirements.gender,
                preferred_color=(
                    state.requirements.preferred_color
                    if state.requirements.hard_color_constraint
                    else None
                ),
                preferred_colors=(
                    state.requirements.preferred_colors
                    if state.requirements.hard_color_constraint
                    else ()
                ),
            )


class OutfitBuilderAgent(Agent):
    name = "outfit_builder_agent"
    role = "outfit_builder_agent"

    def run(self, state: WorkflowState) -> None:
        if state.requirements is None:
            raise ValueError("Outfit builder requires requirements")
        state.transition(WorkflowStage.BUILDING, WorkflowStatus.RUNNING)
        state.outfit_candidates = self.call_tool(
            state, "build_outfits",
            products_by_category=state.filtered_results,
            required_categories=state.requirements.required_categories,
            limit=DEFAULT_CONFIG.max_outfit_candidates,
            budget_inr=state.requirements.budget_inr,
            occasion=state.requirements.occasion,
            gender=state.requirements.gender,
            season=state.requirements.season,
            preferred_colors=state.requirements.preferred_colors,
            hard_color_constraint=state.requirements.hard_color_constraint,
            metrics=state.metrics,
            rejected_candidates=state.rejected_candidates,
        )


class ComparisonAgent(Agent):
    name = "comparison_agent"
    role = "comparison_agent"

    def run(self, state: WorkflowState) -> None:
        state.transition(WorkflowStage.COMPARING, WorkflowStatus.RUNNING)
        state.comparison_results = self.call_tool(
            state, "compare_outfits", outfits=state.outfit_candidates
        )


class RankingAgent(Agent):
    name = "ranking_agent"
    role = "ranking_agent"

    def run(self, state: WorkflowState) -> None:
        if state.requirements is None:
            raise ValueError("Ranking requires requirements")
        state.transition(WorkflowStage.RANKING, WorkflowStatus.RUNNING)
        ranked = self.call_tool(
            state, "rank_outfits", outfits=state.outfit_candidates,
            required_categories=state.requirements.required_categories,
            budget_inr=state.requirements.budget_inr,
            preferred_color=state.requirements.preferred_color,
            preferred_colors=state.requirements.preferred_colors,
            preferred_style=state.requirements.style,
            occasion=state.requirements.occasion,
            season=state.requirements.season,
            gender=state.requirements.gender,
            hard_color_constraint=state.requirements.hard_color_constraint,
        )
        ranked_results = [
            {
                "outfit": outfit,
                "score_breakdown": score.as_dict(),
                "eligibility_status": score.eligibility_status,
                "validation_errors": list(score.validation_errors),
                "validation_warnings": list(score.validation_warnings),
                "quality_score": score.product_quality,
                "preference_match": score.preference_match,
                "outfit_coherence": score.outfit_coherence,
                "rank": index,
            }
            for index, (outfit, score) in enumerate(ranked, start=1)
        ]
        state.rejected_candidates.extend([
            result for result in ranked_results
            if result["eligibility_status"] != "ELIGIBLE"
        ])
        state.ranking_results = [
            result for result in ranked_results
            if result["eligibility_status"] == "ELIGIBLE"
        ]


class ValidatorAgent(Agent):
    name = "validator_agent"
    role = "validator_agent"

    def run(self, state: WorkflowState) -> None:
        if state.requirements is None:
            raise ValueError("Validation requires requirements")
        state.transition(WorkflowStage.VALIDATING, WorkflowStatus.RUNNING)
        if not state.ranking_results:
            state.validation_result = {
                "status": "FAILED", "errors": ["No ranked outfit candidates"],
                "warnings": [], "checks": {},
            }
        else:
            checkpoint_results = state.ranking_results[:5]
            checks = self.call_tool(
                state, "validate_recommendation",
                outfits=[result["outfit"] for result in checkpoint_results],
                budget_inr=state.requirements.budget_inr,
                required_categories=state.requirements.required_categories,
                occasion=state.requirements.occasion,
                gender=state.requirements.gender,
                season=state.requirements.season,
                preferred_colors=state.requirements.preferred_colors,
                hard_color_constraint=state.requirements.hard_color_constraint,
            )
            errors = [error for result in checks for error in result["errors"]]
            state.validation_result = {
                "status": "PASSED" if not errors else "FAILED",
                "errors": sorted(set(errors)),
                "warnings": [],
                "checks": {
                    "candidates_checked": len(checks),
                    "checkpoint": "top_5_ranked_recommendations",
                },
            }
        state.validation_checkpoints.append("ranking")


class SupervisorAgent(Agent):
    name = "supervisor_agent"
    role = "supervisor_agent"

    def run(self, state: WorkflowState) -> None:
        if state.validation_result is None:
            raise ValueError("Supervisor requires validation")
        passed = state.validation_result["status"] == "PASSED"
        state.add_trace({
            "agent": self.name,
            "event": "supervision_decision",
            "decision": "continue_to_approval" if passed else "recover_or_fail",
        })
        state.status = WorkflowStatus.WAITING_FOR_APPROVAL if passed else WorkflowStatus.FAILED
        state.stage = WorkflowStage.HUMAN_APPROVAL if passed else WorkflowStage.FAILED
