"""Conditional edge functions for LangGraph.

Edge functions receive GraphState and return a string key that LangGraph
uses to look up the next node in the conditional mapping.
"""

from __future__ import annotations

from webstone.agents.router.router import ResearchRouter, RouterDecision
from webstone.core.state.base import GraphState

_router = ResearchRouter()


def route_after_evaluator(state: GraphState) -> str:
    """Routing logic applied after the evaluator node.

    Returns one of: "recurse", "merge", "terminate"
    LangGraph maps these strings to the next node via add_conditional_edges.
    """
    return _router.route(state)
