"""Memory agent — bridges the cognitive layer and the memory layer.

The memory agent is responsible for:
  1. Writing branch findings to the graph/vector stores after reader completion.
  2. Providing relevant context to reader agents before they start.

It is intentionally thin — all store logic lives in `webstone.memory`.
"""

from __future__ import annotations

import logging
from typing import Any

from webstone.agents.base import BaseAgent
from webstone.core.state.base import AgentRole, ExecutionStatus, GraphState

logger = logging.getLogger(__name__)


class MemoryAgent(BaseAgent):
    """Persists branch findings to the memory layer and retrieves context.

    TODO: Inject MemoryRetriever and GraphStore dependencies via constructor.
    TODO: Implement graph extraction from findings (entity/relation parsing).
    TODO: Implement vector indexing of findings for semantic retrieval.
    """

    @property
    def role(self) -> AgentRole:
        return AgentRole.MEMORY

    async def invoke(self, state: GraphState, **kwargs: Any) -> dict[str, Any]:
        """Write completed branch findings to memory stores.

        This node runs after the reader phase. It persists all findings
        so they are available to future reader invocations (recursive branches)
        and to the final synthesizer.
        """
        completed = [b for b in state.branches if b.status == ExecutionStatus.COMPLETED]

        for branch in completed:
            await self._persist_branch(branch, state.run_id)

        logger.info("MemoryAgent: persisted %d branches to memory", len(completed))
        return {}  # No state update — memory is a side effect

    async def _persist_branch(self, branch: Any, run_id: str) -> None:
        """Persist a branch's findings to the graph and vector stores.

        TODO: Implement actual persistence:
          1. Extract entities and relations from findings using an LLM.
          2. Write to graph store.
          3. Embed findings and write to vector store.
        """
        logger.debug("MemoryAgent: persisting branch=%s run=%s", branch.id, run_id)
        # TODO: graph_store.upsert_nodes(entities)
        # TODO: vector_store.upsert(chunks, embeddings)
