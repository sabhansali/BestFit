"""Central configuration for the outfit recommendation workflow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RankingWeights:
    """Weights used by deterministic outfit scoring."""

    style: float = 0.20
    color: float = 0.20
    occasion: float = 0.15
    category: float = 0.15
    formality: float = 0.10
    season: float = 0.10
    constraints: float = 0.10

    def __post_init__(self) -> None:
        values = (
            self.style,
            self.color,
            self.occasion,
            self.category,
            self.formality,
            self.season,
            self.constraints,
        )
        if any(value < 0 for value in values):
            raise ValueError("Ranking weights cannot be negative")
        if sum(values) == 0:
            raise ValueError("At least one ranking weight must be positive")

    @property
    def total(self) -> float:
        return sum(
            (
                self.style,
                self.color,
                self.occasion,
                self.category,
                self.formality,
                self.season,
                self.constraints,
            )
        )


@dataclass(frozen=True)
class WorkflowConfig:
    """Tunable limits shared by future agents and orchestration."""

    max_candidates_per_category: int = 60
    max_outfit_candidates: int = 100
    max_retries: int = 2
    default_budget_inr: float = 5000.0
    ranking_weights: RankingWeights = RankingWeights()
    agent_cost_units: float = 1.0
    tool_cost_units: float = 1.0
    retry_cost_units: float = 1.0

    def __post_init__(self) -> None:
        if self.max_candidates_per_category <= 0:
            raise ValueError("Candidate limit must be positive")
        if self.max_outfit_candidates <= 0:
            raise ValueError("Outfit limit must be positive")
        if self.max_retries < 0:
            raise ValueError("Retry limit cannot be negative")
        if self.default_budget_inr <= 0:
            raise ValueError("Default budget must be positive")
        if any(
            value < 0
            for value in (self.agent_cost_units, self.tool_cost_units, self.retry_cost_units)
        ):
            raise ValueError("Cost units cannot be negative")


DEFAULT_CONFIG = WorkflowConfig()
