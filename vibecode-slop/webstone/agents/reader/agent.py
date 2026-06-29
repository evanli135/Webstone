"""Reader agent implementation.

The reader receives a SearchBranch (a focused sub-question) and:
  1. Queries the memory layer for relevant context.
  2. Optionally uses tools (web search, document retrieval) to gather new info.
  3. Synthesizes findings into a structured summary.

Readers are the primary workhorses — the system runs many of them in parallel.
They should be stateless with respect to each other.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from webstone.agents.base import BaseAgent
from webstone.agents.reader.prompts import READER_SYSTEM_PROMPT
from webstone.core.state.base import AgentRole, ExecutionStatus, GraphState, SearchBranch

logger = logging.getLogger(__name__)


class ReaderAgent(BaseAgent):
    """Investigates a single SearchBranch and populates its findings.

    Each ReaderAgent instance handles one branch. In a distributed deployment,
    multiple ReaderAgent instances run in parallel worker processes.

    TODO: Integrate memory retrieval (graph + vector) before LLM call.
    TODO: Add tool use for web search and document retrieval.
    TODO: Implement streaming output for long-running research.
    """

    @property
    def role(self) -> AgentRole:
        return AgentRole.READER

    async def invoke(self, state: GraphState, **kwargs: Any) -> dict[str, Any]:
        """Process pending branches and populate their findings.

        The reader iterates over all PENDING branches in the state and
        investigates them. In the full implementation, branches are
        dispatched to separate worker tasks and run concurrently.

        TODO: Replace serial loop with parallel asyncio.gather dispatch.
        """
        pending = [b for b in state.branches if b.status == ExecutionStatus.PENDING]
        if not pending:
            logger.debug("ReaderAgent: no pending branches to process")
            return {}

        updated_branches = list(state.branches)

        for branch in pending:
            updated_branch = await self._research_branch(state, branch)
            idx = next(i for i, b in enumerate(updated_branches) if b.id == branch.id)
            updated_branches[idx] = updated_branch

        return {"branches": updated_branches}

    async def _research_branch(self, state: GraphState, branch: SearchBranch) -> SearchBranch:
        """Investigate a single branch and return an updated copy."""
        logger.info("ReaderAgent: researching branch=%s query=%r", branch.id, branch.sub_query)

        llm = self.get_llm()
        messages = [
            SystemMessage(content=READER_SYSTEM_PROMPT),
            HumanMessage(content=self._build_prompt(state, branch)),
        ]

        try:
            # TODO: Inject memory context before invoking the LLM.
            response = await llm.ainvoke(messages)

            return branch.model_copy(
                update={
                    "findings": [str(response.content)],
                    "status": ExecutionStatus.COMPLETED,
                }
            )
        except Exception as exc:
            logger.error("ReaderAgent: branch %s failed: %s", branch.id, exc)
            return branch.model_copy(
                update={
                    "status": ExecutionStatus.FAILED,
                    "metadata": {**branch.metadata, "error": str(exc)},
                }
            )

    def _build_prompt(self, state: GraphState, branch: SearchBranch) -> str:
        """Construct the research prompt for a branch."""
        original_query = state.query.query if state.query else "unknown"
        return (
            f"Original research question: {original_query}\n\n"
            f"Your specific sub-question: {branch.sub_query}\n\n"
            "Provide a thorough, factual answer. Cite sources if known. "
            "Be concise but complete."
        )
