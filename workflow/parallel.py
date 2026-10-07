"""Parallel execution strategy."""

from workflow.state import WorkflowState


def run_parallel(orchestrator: object, state: WorkflowState) -> WorkflowState:
    """Run the shared pipeline with independent category searches concurrent."""

    return orchestrator._run_pipeline(state, parallel=True)
