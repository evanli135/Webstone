"""Shared pytest fixtures.

Fixtures here are available to all tests. Use `scope="session"` for
expensive setup (LLM clients, DBs); use the default function scope for
anything that must be isolated between tests.
"""

from __future__ import annotations

import pytest

from webstone.core.state.base import (
    BranchContext,
    ExecutionStatus,
    GraphState,
    ResearchQuery,
    SearchBranch,
)
from webstone.core.models.base import AgentConfig, RetryPolicy
from webstone.memory.graph_store.store import InMemoryGraphStore
from webstone.memory.vector_store.store import InMemoryVectorStore
from webstone.memory.retrieval.retriever import MemoryRetriever
from webstone.runtime.checkpoints.store import InMemoryCheckpointStore
from webstone.observability.events.bus import InMemoryEventBus


# ── State fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def research_query() -> ResearchQuery:
    return ResearchQuery(
        query="What are the key architectural patterns for LLM agents?",
        max_branches=4,
        max_depth=2,
    )


@pytest.fixture
def empty_state(research_query: ResearchQuery) -> GraphState:
    """A fresh GraphState with a query but no branches or findings."""
    return GraphState(
        query=research_query,
        status=ExecutionStatus.RUNNING,
        messages=[],
        branches=[],
        errors=[],
    )


@pytest.fixture
def state_with_branches(empty_state: GraphState) -> GraphState:
    """A GraphState with two pending branches."""
    branches = [
        SearchBranch(
            context=BranchContext(depth=0),
            sub_query="What is the ReAct pattern?",
            status=ExecutionStatus.PENDING,
        ),
        SearchBranch(
            context=BranchContext(depth=0),
            sub_query="What is the Plan-and-Execute pattern?",
            status=ExecutionStatus.PENDING,
        ),
    ]
    return empty_state.model_copy(update={"branches": branches})


@pytest.fixture
def state_with_completed_branches(state_with_branches: GraphState) -> GraphState:
    """A GraphState where all branches have findings."""
    updated = [
        b.model_copy(update={
            "findings": [f"Findings for: {b.sub_query}"],
            "status": ExecutionStatus.COMPLETED,
        })
        for b in state_with_branches.branches
    ]
    return state_with_branches.model_copy(update={"branches": updated})


# ── Infrastructure fixtures ───────────────────────────────────────────────────

@pytest.fixture
def graph_store() -> InMemoryGraphStore:
    return InMemoryGraphStore()


@pytest.fixture
def vector_store() -> InMemoryVectorStore:
    return InMemoryVectorStore()


@pytest.fixture
def memory_retriever(
    graph_store: InMemoryGraphStore, vector_store: InMemoryVectorStore
) -> MemoryRetriever:
    return MemoryRetriever(graph_store=graph_store, vector_store=vector_store)


@pytest.fixture
def checkpoint_store() -> InMemoryCheckpointStore:
    return InMemoryCheckpointStore()


@pytest.fixture
def event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@pytest.fixture
def agent_config() -> AgentConfig:
    return AgentConfig(
        model_name="claude-haiku-4-5-20251001",
        temperature=0.0,
        retry_policy=RetryPolicy(max_attempts=1),  # no retries in tests
    )
