"""Node function implementations.

Each function here is a LangGraph node: it takes GraphState and returns a
partial state update dict. Nodes are intentionally thin — they instantiate
the agent, delegate, and return.

In a production system, agents would be injected (not instantiated here)
via a dependency injection container or factory, allowing test doubles.

TODO: Replace direct instantiation with injected agent factories.
TODO: Add span creation for each node for distributed tracing.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from webstone.agents.evaluator.agent import EvaluatorAgent
from webstone.agents.memory.agent import MemoryAgent
from webstone.agents.planner.agent import PlannerAgent
from webstone.agents.reader.agent import ReaderAgent
from webstone.core.state.base import ExecutionStatus, GraphState

logger = logging.getLogger(__name__)


async def planner_node(state: GraphState) -> dict[str, Any]:
    """Decompose the research query into parallel search branches."""
    logger.info("NODE planner | run=%s", state.run_id)
    agent = PlannerAgent()
    return await agent.invoke(state)


async def reader_node(state: GraphState) -> dict[str, Any]:
    """Investigate all pending branches and populate findings."""
    logger.info("NODE reader | run=%s branches=%d", state.run_id, len(state.branches))
    agent = ReaderAgent()
    return await agent.invoke(state)


async def evaluator_node(state: GraphState) -> dict[str, Any]:
    """Score completed branches and prune low-quality ones."""
    logger.info("NODE evaluator | run=%s", state.run_id)
    agent = EvaluatorAgent()
    return await agent.invoke(state)


async def memory_node(state: GraphState) -> dict[str, Any]:
    """Persist branch findings to the memory stores."""
    logger.info("NODE memory | run=%s", state.run_id)
    agent = MemoryAgent()
    return await agent.invoke(state)


async def synthesizer_node(state: GraphState) -> dict[str, Any]:
    """Synthesize all passing branch findings into a final answer.

    TODO: Implement LLM-based synthesis. Currently returns a placeholder.
    """
    logger.info("NODE synthesizer | run=%s", state.run_id)

    passing = [b for b in state.branches if b.status == ExecutionStatus.COMPLETED]
    if not passing:
        return {
            "final_answer": "No sufficient findings were gathered.",
            "status": ExecutionStatus.COMPLETED,
        }

    # Stub: concatenate findings until real synthesis is implemented
    # TODO: Invoke LLM with all findings to produce a coherent final answer.
    combined = "\n\n---\n\n".join(
        f"**{b.sub_query}**\n{chr(10).join(b.findings)}" for b in passing
    )
    return {
        "final_answer": combined,
        "status": ExecutionStatus.COMPLETED,
    }
