"""Research router — graph edge routing logic.

The router is called after the evaluator and decides what happens next:
  - RECURSE: spawn sub-branches for high-scoring branches that warrant deeper exploration
  - MERGE: all branches explored sufficiently, proceed to answer synthesis
  - TERMINATE: fatal error or max depth reached

In LangGraph, the router is used as a conditional edge function.
"""

from __future__ import annotations

import logging
from enum import StrEnum

from webstone.core.state.base import ExecutionStatus, GraphState

logger = logging.getLogger(__name__)


class RouterDecision(StrEnum):
    RECURSE = "recurse"
    MERGE = "merge"
    TERMINATE = "terminate"


class ResearchRouter:
    """Stateless routing logic for the research graph.

    This class is not an agent — it does not invoke an LLM. It applies
    deterministic rules over the current graph state to decide the next step.

    To use as a LangGraph conditional edge:
        graph.add_conditional_edges("evaluator", router.route, {
            RouterDecision.RECURSE: "planner",
            RouterDecision.MERGE: "synthesizer",
            RouterDecision.TERMINATE: END,
        })
    """

    def __init__(self, max_depth: int = 3, min_passing_branches: int = 1) -> None:
        self.max_depth = max_depth
        self.min_passing_branches = min_passing_branches

    def route(self, state: GraphState) -> RouterDecision:
        """Determine the next step based on current state.

        Args:
            state: Current graph state after evaluator has run.

        Returns:
            RouterDecision string used by LangGraph conditional edges.
        """
        if state.status == ExecutionStatus.FAILED:
            logger.warning("Router: state is FAILED, terminating")
            return RouterDecision.TERMINATE

        passing = [b for b in state.branches if b.score is not None and b.score >= 0.5]
        max_depth_reached = all(
            b.context.depth >= self.max_depth for b in state.branches if passing
        )

        if not passing:
            logger.info("Router: no passing branches, terminating")
            return RouterDecision.TERMINATE

        if max_depth_reached:
            logger.info("Router: max depth reached, merging")
            return RouterDecision.MERGE

        # TODO: implement smarter recursion heuristic — e.g., only recurse
        #       branches with score >= some threshold AND where findings
        #       indicate significant unexplored sub-topics.
        logger.info("Router: merging %d passing branches", len(passing))
        return RouterDecision.MERGE
