"""Validation for state updates that affect trusted requirements."""

from workflow.state import Requirements, WorkflowState


def validate_requirements(requirements: Requirements) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if requirements.budget_inr <= 0:
        errors.append("Budget must be positive")
    if not requirements.required_categories:
        errors.append("At least one category is required")
    return not errors, errors


def validate_state_update(state: WorkflowState, requirements: Requirements) -> tuple[bool, list[str]]:
    if state.requirements is not None and requirements != state.requirements:
        return False, ["Trusted requirements cannot be overwritten after planning"]
    return validate_requirements(requirements)
