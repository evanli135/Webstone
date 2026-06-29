"""Planner agent implementation.

The planner receives a ResearchQuery and produces:
  1. A high-level research plan (string)
  2. A list of SearchBranches (sub-queries to explore in parallel)

Design:
  - The planner is called once at the root of each graph execution.
  - It may be called recursively for deeper branches if the router decides
    further decomposition is needed.
  - It should NOT do any retrieval — that is the reader's job.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from webstone.agents.base import BaseAgent
from webstone.agents.planner.prompts import PLANNER_SYSTEM_PROMPT
from webstone.core.state.base import AgentRole, BranchContext, GraphState, SearchBranch

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """Decomposes a top-level research query into parallel search branches.

    Each branch represents an independent sub-question that can be explored
    by reader agents concurrently. The number of branches is bounded by
    state.query.max_branches.

    TODO: Implement structured output parsing to extract SearchBranch list.
    TODO: Add few-shot examples to improve plan quality.
    TODO: Support chain-of-thought reasoning traces.
    """

    @property
    def role(self) -> AgentRole:
        return AgentRole.PLANNER

    async def invoke(self, state: GraphState, **kwargs: Any) -> dict[str, Any]:
        """Generate a research plan and decompose into search branches.

        Args:
            state: Must have `state.query` populated.

        Returns:
            Partial state update with `plan` and `branches`.
        """
        if state.query is None:
            logger.error("PlannerAgent invoked with no query in state")
            return {"errors": [*state.errors, "Planner: no query provided"]}

        logger.info("PlannerAgent: planning for query=%r", state.query.query)

        llm = self.get_llm()

        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=self._build_prompt(state)),
        ]

        # TODO: Use structured output (llm.with_structured_output) to parse
        #       a proper PlannerOutput model with plan + sub_queries list.
        response = await llm.ainvoke(messages)

        # Placeholder: create stub branches from the raw response
        # In a real implementation, parse the LLM output into SearchBranch list
        plan_text = str(response.content)
        branches = self._parse_branches(state, plan_text)

        logger.info("PlannerAgent: created %d branches", len(branches))
        return {
            "plan": plan_text,
            "branches": branches,
            "messages": [*state.messages, *messages, response],
        }

    def _build_prompt(self, state: GraphState) -> str:
        """Build the user prompt for the planner."""
        assert state.query is not None
        return (
            f"Research question: {state.query.query}\n\n"
            f"Maximum branches: {state.query.max_branches}\n"
            f"Maximum depth: {state.query.max_depth}\n\n"
            "Decompose this into parallel sub-questions. "
            "Return a numbered list of sub-questions, one per line."
        )

    def _parse_branches(self, state: GraphState, plan_text: str) -> list[SearchBranch]:
        """Parse planner output into SearchBranch objects.

        TODO: Replace this stub with robust structured output parsing.
              The LLM should return JSON with a well-defined schema.
        """
        assert state.query is not None
        lines = [line.strip() for line in plan_text.splitlines() if line.strip()]
        sub_queries = lines[: state.query.max_branches] or ["Explore the main topic directly"]

        return [
            SearchBranch(
                context=BranchContext(depth=0),
                sub_query=sq,
            )
            for sq in sub_queries
        ]
