"""Graph-structured memory store.

Stores entities (nodes) and relationships (edges) discovered during research.
Supports graph traversal queries for context retrieval.

Current backend: in-memory adjacency list (for dev/testing).
Future backends: Neo4j, Kuzu, FalkorDB — swappable via Protocol interface.

Node model:
    Entity(id="anthropic", type="organization", properties={...})

Edge model:
    Relation(source="anthropic", relation="publishes", target="claude")

TODO: Implement graph traversal (BFS/DFS) for neighborhood queries.
TODO: Add full-text search over node properties.
TODO: Implement Neo4jGraphStore backed by the Neo4j async driver.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GraphNode(BaseModel):
    """A knowledge graph entity."""

    id: str
    entity_type: str
    properties: dict[str, Any] = Field(default_factory=dict)
    source_run_ids: list[str] = Field(default_factory=list)


class GraphEdge(BaseModel):
    """A directed relationship between two graph nodes."""

    id: str
    source_id: str
    relation: str
    target_id: str
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)
    source_run_ids: list[str] = Field(default_factory=list)


class InMemoryGraphStore:
    """In-memory adjacency list implementation of a knowledge graph store.

    Not suitable for large graphs or multi-process deployments.
    All data is lost on restart.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        # adjacency: node_id -> list of outgoing edge ids
        self._adjacency: dict[str, list[str]] = defaultdict(list)

    async def upsert_node(self, node: GraphNode) -> None:
        """Insert or update a node."""
        if node.id in self._nodes:
            existing = self._nodes[node.id]
            merged_props = {**existing.properties, **node.properties}
            self._nodes[node.id] = node.model_copy(update={"properties": merged_props})
        else:
            self._nodes[node.id] = node
        logger.debug("GraphStore: upserted node=%s type=%s", node.id, node.entity_type)

    async def upsert_edge(self, edge: GraphEdge) -> None:
        """Insert or update an edge."""
        self._edges[edge.id] = edge
        if edge.id not in self._adjacency[edge.source_id]:
            self._adjacency[edge.source_id].append(edge.id)

    async def get_node(self, node_id: str) -> GraphNode | None:
        """Retrieve a node by ID."""
        return self._nodes.get(node_id)

    async def get_neighbors(self, node_id: str, relation: str | None = None) -> list[GraphNode]:
        """Return all nodes reachable from node_id via outgoing edges.

        Args:
            node_id: Source node ID.
            relation: If given, filter by edge relation type.
        """
        edge_ids = self._adjacency.get(node_id, [])
        neighbors: list[GraphNode] = []

        for eid in edge_ids:
            edge = self._edges.get(eid)
            if edge is None:
                continue
            if relation is not None and edge.relation != relation:
                continue
            target = self._nodes.get(edge.target_id)
            if target:
                neighbors.append(target)

        return neighbors

    async def search_by_type(self, entity_type: str) -> list[GraphNode]:
        """Return all nodes of the given entity type."""
        return [n for n in self._nodes.values() if n.entity_type == entity_type]

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)
