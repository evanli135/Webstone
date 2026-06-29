"""The core research workflow graph.

Wires together: planner → reader → memory → evaluator → (router) → synthesizer

         ┌─────────┐
         │ planner │
         └────┬────┘
              │
         ┌────▼────┐
         │ reader  │
         └────┬────┘
              │
         ┌────▼────┐
         │ memory  │   (persists findings)
         └────┬────┘
              │
         ┌────▼────────┐
         │  evaluator  │
         └────┬────────┘
              │ (conditional)
       ┌──────┼──────────┐
  recurse   merge    terminate
       │      │          │
  [planner] [synth]    [END]
              │
         ┌────▼──────────┐
         │  synthesizer  │
         └───────────────┘
                │
              [END]

This module also provides a `__main__` entry point for local testing.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from langgraph.graph import END

from webstone.agents.router.router import RouterDecision
from webstone.graphs.builder import GraphBuilder
from webstone.graphs.edges.base import route_after_evaluator
from webstone.graphs.nodes.base import (
    evaluator_node,
    memory_node,
    planner_node,
    reader_node,
    synthesizer_node,
)
from webstone.core.state.base import ExecutionStatus, GraphState, ResearchQuery

logger = logging.getLogger(__name__)


def build_research_graph() -> Any:
    """Build and compile the standard research workflow graph.

    Returns a compiled LangGraph runnable. Invoke it with a dict
    matching GraphState fields:
        graph.invoke({"query": ResearchQuery(query="..."), "run_id": "..."})

    Returns:
        A compiled LangGraph CompiledStateGraph.
    """
    builder = GraphBuilder()

    # Register nodes
    builder.add_node("planner", planner_node)
    builder.add_node("reader", reader_node)
    builder.add_node("memory", memory_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("synthesizer", synthesizer_node)

    # Set entry point
    builder.set_entry("planner")

    # Linear edges: planner → reader → memory → evaluator
    builder.add_edge("planner", "reader")
    builder.add_edge("reader", "memory")
    builder.add_edge("memory", "evaluator")

    # Conditional routing after evaluator
    builder.add_conditional_edges(
        "evaluator",
        route_after_evaluator,
        {
            RouterDecision.RECURSE: "planner",   # recurse deeper
            RouterDecision.MERGE: "synthesizer",  # done, synthesize
            RouterDecision.TERMINATE: END,         # no useful results
        },
    )

    # Synthesizer → END
    builder.set_finish("synthesizer")

    return builder.compile()


async def run_example() -> None:
    """Local test harness — run the research graph on a sample query."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Building research graph...")
    graph = build_research_graph()

    initial_state = {
        "query": ResearchQuery(
            query="What are the main architectural patterns for building large language model agents?",
            max_branches=3,
            max_depth=2,
        ),
        "status": ExecutionStatus.RUNNING,
        "messages": [],
        "branches": [],
        "errors": [],
        "metadata": {},
    }

    logger.info("Starting research run...")
    result = await graph.ainvoke(initial_state)
    final_state = GraphState.model_validate(result)

    print("\n" + "=" * 60)
    print("RESEARCH COMPLETE")
    print("=" * 60)
    print(f"Status: {final_state.status}")
    print(f"Branches: {len(final_state.branches)}")
    print(f"\nFinal Answer:\n{final_state.final_answer}")


if __name__ == "__main__":
    asyncio.run(run_example())
