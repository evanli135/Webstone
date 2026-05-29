"""Unit tests for the research router (deterministic — no LLM calls)."""

from __future__ import annotations

import pytest

from webstone.agents.router.router import ResearchRouter, RouterDecision
from webstone.core.state.base import (
    BranchContext,
    ExecutionStatus,
    GraphState,
    ResearchQuery,
    SearchBranch,
)


def make_branch(score: float | None, status: ExecutionStatus, depth: int = 0) -> SearchBranch:
    return SearchBranch(
        context=BranchContext(depth=depth),
        sub_query="test sub-query",
        score=score,
        status=status,
    )


class TestResearchRouter:
    def test_terminates_on_failed_state(self) -> None:
        router = ResearchRouter()
        state = GraphState(status=ExecutionStatus.FAILED)
        assert router.route(state) == RouterDecision.TERMINATE

    def test_terminates_when_no_passing_branches(self) -> None:
        router = ResearchRouter()
        state = GraphState(
            query=ResearchQuery(query="test"),
            branches=[make_branch(score=0.1, status=ExecutionStatus.PRUNED)],
        )
        assert router.route(state) == RouterDecision.TERMINATE

    def test_merges_when_passing_branches_exist(self) -> None:
        router = ResearchRouter(max_depth=3)
        state = GraphState(
            query=ResearchQuery(query="test"),
            branches=[
                make_branch(score=0.8, status=ExecutionStatus.COMPLETED, depth=1),
            ],
        )
        assert router.route(state) == RouterDecision.MERGE

    def test_terminates_when_no_branches(self) -> None:
        router = ResearchRouter()
        state = GraphState(query=ResearchQuery(query="test"), branches=[])
        assert router.route(state) == RouterDecision.TERMINATE
