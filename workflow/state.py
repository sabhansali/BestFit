"""Typed shared state for the multi-agent recommendation workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class WorkflowStage(str, Enum):
    CREATED = "created"
    SECURITY = "security"
    PLANNING = "planning"
    ROUTING = "routing"
    SEARCHING = "searching"
    FILTERING = "filtering"
    BUILDING = "building"
    COMPARING = "comparing"
    RANKING = "ranking"
    VALIDATING = "validating"
    HUMAN_APPROVAL = "human_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Requirements:
    budget_inr: float
    occasion: str
    required_categories: tuple[str, ...]
    style: str | None = None
    preferred_color: str | None = None
    preferred_colors: tuple[str, ...] = ()
    hard_color_constraint: bool = False
    gender: str | None = None
    season: str | None = None
    formality: int | None = None

    def __post_init__(self) -> None:
        if self.budget_inr <= 0:
            raise ValueError("Budget must be positive")
        if not self.occasion.strip():
            raise ValueError("Occasion is required")
        if not self.required_categories:
            raise ValueError("At least one product category is required")
        if len(set(category.lower() for category in self.required_categories)) != len(
            self.required_categories
        ):
            raise ValueError("Required categories must be unique")


@dataclass(frozen=True)
class Plan:
    requirements: Requirements
    rationale: str = ""


@dataclass(frozen=True)
class RoutingPlan:
    search_categories: tuple[str, ...]


@dataclass
class WorkflowState:
    user_query: str
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    requirements: Requirements | None = None
    plan: Plan | None = None
    routing_plan: RoutingPlan | None = None
    search_results: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    filtered_results: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    outfit_candidates: list[list[dict[str, Any]]] = field(default_factory=list)
    comparison_results: list[dict[str, Any]] = field(default_factory=list)
    ranking_results: list[dict[str, Any]] = field(default_factory=list)
    validation_result: dict[str, Any] | None = None
    human_approval: bool | None = None
    messages: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    trace: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    security_events: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    stage: WorkflowStage = WorkflowStage.CREATED
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    agent_execution_count: int = 0
    tool_execution_count: int = 0
    validation_checkpoints: list[str] = field(default_factory=list)
    retry_history: list[dict[str, Any]] = field(default_factory=list)
    checkpoint_results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def transition(self, stage: WorkflowStage, status: WorkflowStatus) -> None:
        if self.status in {WorkflowStatus.COMPLETED, WorkflowStatus.FAILED}:
            raise ValueError("A terminal workflow cannot transition")
        self.stage = stage
        self.status = status
        self.updated_at = datetime.now(timezone.utc)

    def add_trace(self, event: dict[str, Any]) -> None:
        self.trace.append({"workflow_id": self.workflow_id, **event})
        self.updated_at = datetime.now(timezone.utc)

    def record_agent_execution(self) -> None:
        self.agent_execution_count += 1

    def record_tool_execution(self) -> None:
        self.tool_execution_count += 1

    def record_human_decision(self, approved: bool) -> None:
        """Commit an approval or reopen the workflow for supervised re-analysis."""

        if not (
            self.stage is WorkflowStage.HUMAN_APPROVAL
            and self.status is WorkflowStatus.WAITING_FOR_APPROVAL
        ):
            raise ValueError("Human decision requires a workflow waiting for approval")
        self.human_approval = approved
        if approved:
            self.transition(WorkflowStage.COMPLETED, WorkflowStatus.COMPLETED)
            self.add_trace({"event": "human_approval", "decision": "approved"})
            return
        self.outfit_candidates.clear()
        self.comparison_results.clear()
        self.ranking_results.clear()
        self.validation_result = None
        self.checkpoint_results.clear()
        self.validation_checkpoints.clear()
        self.transition(WorkflowStage.PLANNING, WorkflowStatus.RUNNING)
        self.add_trace({"event": "human_approval", "decision": "rejected", "action": "reanalyze"})

    def record_retry(self, stage: str, error: str) -> None:
        self.retry_count += 1
        self.retry_history.append({"stage": stage, "retry_number": self.retry_count, "error": error})
        self.add_trace(
            {
                "event": "retry_scheduled",
                "stage": stage,
                "retry_number": self.retry_count,
                "error": error,
            }
        )
