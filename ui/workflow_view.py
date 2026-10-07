"""Workflow execution view."""

from pathlib import Path

from tools.default_registry import create_default_registry
from workflow.orchestrator import WorkflowOrchestrator
from workflow.state import WorkflowState


def execute_query(query: str, mode: str) -> WorkflowState:
    orchestrator = WorkflowOrchestrator(
        create_default_registry(),
        Path(__file__).parents[1] / "data" / "products.csv",
    )
    return orchestrator.run(WorkflowState(query), mode=mode)
