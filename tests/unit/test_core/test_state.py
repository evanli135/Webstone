"""Unit tests for core state models."""

from __future__ import annotations

import pytest

from webstone.core.state.base import (
    BranchContext,
    ExecutionStatus,
    GraphState,
    ResearchQuery,
    SearchBranch,
)


class TestResearchQuery:
    def test_defaults(self) -> None:
        q = ResearchQuery(query="test question")
        assert q.max_depth == 3
        assert q.max_branches == 16
        assert q.id  # auto-generated UUID

    def test_id_is_unique(self) -> None:
        q1 = ResearchQuery(query="a")
        q2 = ResearchQuery(query="b")
        assert q1.id != q2.id


class TestBranchContext:
    def test_root_context(self) -> None:
        ctx = BranchContext(depth=0)
        assert ctx.is_root
        assert ctx.parent_id is None

    def test_child_context(self) -> None:
        ctx = BranchContext(depth=1, parent_id="parent-id")
        assert not ctx.is_root

    def test_path_tracking(self) -> None:
        ctx = BranchContext(depth=2, path=["root-id", "mid-id"])
        assert len(ctx.path) == 2


class TestSearchBranch:
    def test_defaults(self) -> None:
        branch = SearchBranch(
            context=BranchContext(),
            sub_query="What is X?",
        )
        assert branch.status == ExecutionStatus.PENDING
        assert branch.score is None
        assert branch.findings == []

    def test_model_copy_preserves_id(self) -> None:
        branch = SearchBranch(context=BranchContext(), sub_query="Q?")
        updated = branch.model_copy(update={"status": ExecutionStatus.COMPLETED})
        assert updated.id == branch.id
        assert updated.status == ExecutionStatus.COMPLETED


class TestGraphState:
    def test_empty_state(self) -> None:
        state = GraphState()
        assert state.status == ExecutionStatus.PENDING
        assert state.branches == []
        assert state.errors == []
        assert state.final_answer is None

    def test_arbitrary_types_allowed(self, empty_state: GraphState) -> None:
        # GraphState allows BaseMessage in messages — just verify instantiation
        assert isinstance(empty_state, GraphState)

    def test_run_id_is_unique(self) -> None:
        s1 = GraphState()
        s2 = GraphState()
        assert s1.run_id != s2.run_id
