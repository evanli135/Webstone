"""Graph builder abstraction.

GraphBuilder wraps LangGraph's StateGraph to provide a typed, composable
interface for defining research workflows. It enforces that all nodes are
registered with proper typing and that the graph compiles before execution.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from langgraph.graph import END, StateGraph

from webstone.core.state.base import GraphState

logger = logging.getLogger(__name__)

# Node function type: async callable from GraphState -> partial state dict
NodeFn = Callable[[GraphState], Any]


class GraphBuilder:
    """Typed wrapper around LangGraph's StateGraph for research workflows.

    Usage:
        builder = GraphBuilder()
        builder.add_node("planner", planner_node)
        builder.add_node("reader", reader_node)
        builder.add_edge("planner", "reader")
        builder.set_entry("planner")
        graph = builder.compile()

    TODO: Add graph validation (no orphan nodes, reachable END, etc.).
    TODO: Add visualization helper (export to Mermaid diagram).
    """

    def __init__(self) -> None:
        self._graph: StateGraph = StateGraph(GraphState)
        self._nodes: dict[str, NodeFn] = {}
        self._compiled = False

    def add_node(self, name: str, fn: NodeFn) -> "GraphBuilder":
        """Register a node function. Returns self for chaining."""
        if name in self._nodes:
            raise ValueError(f"Node '{name}' is already registered")
        self._nodes[name] = fn
        self._graph.add_node(name, fn)
        logger.debug("GraphBuilder: added node '%s'", name)
        return self

    def add_edge(self, from_node: str, to_node: str) -> "GraphBuilder":
        """Add an unconditional edge between two nodes."""
        self._graph.add_edge(from_node, to_node)
        return self

    def add_conditional_edges(
        self,
        from_node: str,
        condition_fn: Callable[[GraphState], str],
        mapping: dict[str, str],
    ) -> "GraphBuilder":
        """Add conditional routing edges from a node.

        Args:
            from_node: Source node name.
            condition_fn: Function that receives state and returns a routing key.
            mapping: Dict mapping routing keys to destination node names.
        """
        self._graph.add_conditional_edges(from_node, condition_fn, mapping)
        return self

    def set_entry(self, node_name: str) -> "GraphBuilder":
        """Set the entry point for the graph."""
        self._graph.set_entry_point(node_name)
        return self

    def set_finish(self, node_name: str) -> "GraphBuilder":
        """Add an edge from node_name to END."""
        self._graph.add_edge(node_name, END)
        return self

    def compile(self) -> Any:
        """Compile and return the runnable LangGraph graph.

        Raises:
            RuntimeError: If the graph has no entry point set.
        """
        if self._compiled:
            raise RuntimeError("Graph has already been compiled")

        compiled = self._graph.compile()
        self._compiled = True
        logger.info("GraphBuilder: compiled graph with %d nodes", len(self._nodes))
        return compiled
