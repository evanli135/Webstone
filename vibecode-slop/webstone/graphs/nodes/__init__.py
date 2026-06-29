"""Node functions — thin wrappers that delegate to agents.

Nodes are the LangGraph integration points. They receive GraphState, create
or reuse an agent, call `agent.invoke(state)`, and return the state update.
"""

from webstone.graphs.nodes.base import (
    evaluator_node,
    memory_node,
    planner_node,
    reader_node,
    synthesizer_node,
)

__all__ = [
    "evaluator_node",
    "memory_node",
    "planner_node",
    "reader_node",
    "synthesizer_node",
]
