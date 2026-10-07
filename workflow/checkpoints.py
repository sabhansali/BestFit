"""Checkpoint validation for trusted workflow contracts."""

from workflow.state import WorkflowState


def validate_checkpoint(state: WorkflowState, checkpoint: str) -> None:
    errors: list[str] = []
    if checkpoint == "plan":
        if state.requirements is None or state.plan is None:
            errors.append("Plan and requirements are required")
        elif state.plan.requirements != state.requirements:
            errors.append("Plan requirements do not match trusted requirements")
    elif checkpoint == "filter":
        if state.routing_plan is None:
            errors.append("Routing plan is required")
        else:
            missing = set(state.routing_plan.search_categories) - set(state.filtered_results)
            if missing:
                errors.append(f"Missing filtered categories: {', '.join(sorted(missing))}")
    elif checkpoint == "ranking":
        if state.ranking_results and any(
            result["score_breakdown"]["overall_score"] < 0
            or result["score_breakdown"]["overall_score"] > 100
            for result in state.ranking_results
        ):
            errors.append("Ranking score is outside 0-100")
    else:
        raise ValueError(f"Unknown checkpoint: {checkpoint}")
    result = {"status": "PASSED" if not errors else "FAILED", "errors": errors}
    state.checkpoint_results[checkpoint] = result
    state.validation_checkpoints.append(checkpoint)
    state.add_trace({"event": "checkpoint_validation", "checkpoint": checkpoint, **result})
    if errors:
        state.errors.extend({"stage": checkpoint, "error": error} for error in errors)
        raise ValueError("; ".join(errors))
