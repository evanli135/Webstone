"""State schemas for graph execution.

All agent nodes read from and write to GraphState. No raw dicts allowed
across node boundaries — everything must be a typed Pydantic model.
"""

from webstone.core.state.base import (
    AgentRole,
    BranchContext,
    ExecutionStatus,
    GraphState,
    ResearchQuery,
    SearchBranch,
)

__all__ = [
    "AgentRole",
    "BranchContext",
    "ExecutionStatus",
    "GraphState",
    "ResearchQuery",
    "SearchBranch",
]
