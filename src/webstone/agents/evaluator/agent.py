"""Evaluator agent implementation.

The evaluator acts as a critic: it scores each completed branch based on
relevance, quality, and novelty relative to the research question. Low-scoring
branches are marked for pruning; high-scoring branches may trigger deeper
recursion via the router.

Design notes:
- Scores are in [0.0, 1.0]. Branches below `prune_threshold` are pruned.
- The evaluator is deterministic (temperature=0) to ensure stable pruning.
- Feedback from the evaluator can optionally be fed back to the planner
  in recursive executions.

TODO: Implement multi-criteria scoring (relevance, quality, novelty separately).
TODO: Add LLM-based pairwise comparison for better relative scoring.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from webstone.agents.base import BaseAgent
from webstone.agents.evaluator.prompts import EVALUATOR_SYSTEM_PROMPT
from webstone.core.models.base import AgentConfig
from webstone.core.state.base import AgentRole, ExecutionStatus, GraphState, SearchBranch

logger = logging.getLogger(__name__)

DEFAULT_PRUNE_THRESHOLD = 0.3


class EvaluatorAgent(BaseAgent):
    """Scores completed branches and marks low-quality ones for pruning.

    The evaluator runs after all reader branches complete. It produces a
    score for each branch and updates their status (completed → pruned if
    below threshold).
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        prune_threshold: float = DEFAULT_PRUNE_THRESHOLD,
    ) -> None:
        super().__init__(config)
        self.prune_threshold = prune_threshold

    @property
    def role(self) -> AgentRole:
        return AgentRole.EVALUATOR

    async def invoke(self, state: GraphState, **kwargs: Any) -> dict[str, Any]:
        """Score all completed branches and prune those below threshold."""
        completed = [b for b in state.branches if b.status == ExecutionStatus.COMPLETED]
        if not completed:
            logger.debug("EvaluatorAgent: no completed branches to evaluate")
            return {}

        scores = await self.score(state)
        updated_branches = list(state.branches)
        pruned_count = 0

        for branch, score in zip(completed, scores):
            idx = next(i for i, b in enumerate(updated_branches) if b.id == branch.id)
            status = ExecutionStatus.PRUNED if score < self.prune_threshold else branch.status

            if status == ExecutionStatus.PRUNED:
                pruned_count += 1
                logger.info("EvaluatorAgent: pruning branch=%s score=%.2f", branch.id, score)

            updated_branches[idx] = branch.model_copy(update={"score": score, "status": status})

        return {"branches": updated_branches}

    async def score(self, state: GraphState) -> list[float]:
        """Score each completed branch. Returns scores in [0.0, 1.0].

        TODO: Replace stub with actual LLM scoring.
              Each branch should be scored against the original query for:
              - Relevance (does it address the question?)
              - Quality (is the content well-supported?)
              - Novelty (does it add new information?)
        """
        completed = [b for b in state.branches if b.status == ExecutionStatus.COMPLETED]

        # Stub: return 1.0 for all branches until LLM scoring is implemented
        # TODO: invoke LLM with EVALUATOR_SYSTEM_PROMPT to produce real scores
        _ = EVALUATOR_SYSTEM_PROMPT  # reference to avoid unused import warnings
        return [1.0] * len(completed)

    async def should_prune(self, score: float) -> bool:
        """Return True if a branch with the given score should be pruned."""
        return score < self.prune_threshold

    def _build_scoring_prompt(self, state: GraphState, branch: SearchBranch) -> str:
        """Build a prompt for scoring a single branch.

        TODO: Call this in `score()` once LLM scoring is implemented.
        """
        original_query = state.query.query if state.query else "unknown"
        findings_text = "\n".join(branch.findings) if branch.findings else "(no findings)"
        return (
            f"Original research question: {original_query}\n\n"
            f"Sub-question: {branch.sub_query}\n\n"
            f"Findings:\n{findings_text}\n\n"
            "Score the findings from 0.0 (completely irrelevant/wrong) to "
            "1.0 (highly relevant, accurate, and complete). "
            "Reply with ONLY a number between 0.0 and 1.0."
        )
