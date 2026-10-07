"""Sequential execution strategy."""

from workflow.state import WorkflowState


def run_sequential(orchestrator: object, state: WorkflowState) -> WorkflowState:
    """Run the shared pipeline with category searches performed in order."""

    return orchestrator._run_pipeline(state, parallel=False)
