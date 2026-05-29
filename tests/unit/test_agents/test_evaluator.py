"""Unit tests for the evaluator agent (mocked LLM)."""

from __future__ import annotations

import pytest

from webstone.agents.evaluator.agent import EvaluatorAgent
from webstone.core.state.base import ExecutionStatus


@pytest.mark.asyncio
class TestEvaluatorAgent:
    async def test_scores_completed_branches(self, state_with_completed_branches) -> None:
        evaluator = EvaluatorAgent(prune_threshold=0.3)
        result = await evaluator.invoke(state_with_completed_branches)

        updated_branches = result["branches"]
        for b in updated_branches:
            if b.status == ExecutionStatus.COMPLETED:
                assert b.score is not None

    async def test_no_op_when_no_completed_branches(self, state_with_branches) -> None:
        evaluator = EvaluatorAgent()
        result = await evaluator.invoke(state_with_branches)
        assert result == {}  # nothing to evaluate

    async def test_prune_threshold(self, state_with_completed_branches) -> None:
        # With threshold = 2.0 (impossible to exceed), all branches should be pruned
        evaluator = EvaluatorAgent(prune_threshold=2.0)
        result = await evaluator.invoke(state_with_completed_branches)
        pruned = [b for b in result["branches"] if b.status == ExecutionStatus.PRUNED]
        assert len(pruned) == len(state_with_completed_branches.branches)

    async def test_should_prune_logic(self) -> None:
        evaluator = EvaluatorAgent(prune_threshold=0.5)
        assert await evaluator.should_prune(0.3) is True
        assert await evaluator.should_prune(0.7) is False
