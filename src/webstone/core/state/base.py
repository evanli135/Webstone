"""Core graph state models.

GraphState is the single source of truth passed through every node in a
LangGraph execution. Nodes receive the current state, compute updates,
and return a new (partial) state dict — they never mutate in place.

Design notes:
- All fields are Optional with defaults so partial updates work cleanly.
- BranchContext tracks lineage for recursive search trees.
- Messages use LangChain's BaseMessage for LLM compatibility.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PRUNED = "pruned"  # Branch was pruned by the evaluator


class AgentRole(StrEnum):
    PLANNER = "planner"
    READER = "reader"
    EVALUATOR = "evaluator"
    ROUTER = "router"
    MEMORY = "memory"


class ResearchQuery(BaseModel):
    """The top-level research question driving an execution run."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    max_depth: int = Field(default=3, ge=1, le=10)
    max_branches: int = Field(default=16, ge=1, le=1024)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class BranchContext(BaseModel):
    """Tracks lineage for a single branch in the recursive search tree.

    Each parallel execution path carries its own BranchContext. This allows
    the evaluator to score and prune branches independently, and allows
    checkpointing to resume specific branches after failure.
    """

    branch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str | None = None
    depth: int = 0
    path: list[str] = Field(default_factory=list)  # ordered branch_ids from root

    @property
    def is_root(self) -> bool:
        return self.parent_id is None


class SearchBranch(BaseModel):
    """A single branch in the recursive search tree.

    Produced by the planner and consumed by reader agents.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    context: BranchContext
    sub_query: str
    hypothesis: str | None = None
    score: float | None = None  # Filled in by the evaluator
    status: ExecutionStatus = ExecutionStatus.PENDING
    findings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphState(BaseModel):
    """Shared state schema for the research graph.

    Every node in the LangGraph workflow reads from and writes to this model.
    LangGraph merges partial updates via its reducer logic — only return the
    fields you actually changed from a node.

    Lifecycle:
        1. Initialized with a ResearchQuery by the entry point.
        2. Planner populates `plan` and `branches`.
        3. Reader nodes populate `branches[*].findings`.
        4. Evaluator scores `branches` and sets `branches[*].score`.
        5. Router decides whether to branch further, merge, or terminate.
        6. Final answer is assembled into `final_answer`.
    """

    # Execution identity
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: ExecutionStatus = ExecutionStatus.PENDING

    # Research query
    query: ResearchQuery | None = None

    # Planning outputs
    plan: str | None = None
    branches: list[SearchBranch] = Field(default_factory=list)

    # Message history for LLM context
    messages: Annotated[list[BaseMessage], Field(default_factory=list)]

    # Final assembled answer
    final_answer: str | None = None
    confidence_score: float | None = None

    # Error tracking
    errors: list[str] = Field(default_factory=list)

    # Arbitrary metadata (timestamps, agent notes, debug info)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True  # needed for BaseMessage
