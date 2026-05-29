"""Unit tests for the in-memory graph store."""

from __future__ import annotations

import pytest

from webstone.memory.graph_store.store import GraphEdge, GraphNode, InMemoryGraphStore


@pytest.mark.asyncio
class TestInMemoryGraphStore:
    async def test_upsert_and_get_node(self) -> None:
        store = InMemoryGraphStore()
        node = GraphNode(id="n1", entity_type="concept", properties={"name": "ReAct"})
        await store.upsert_node(node)
        result = await store.get_node("n1")
        assert result is not None
        assert result.entity_type == "concept"

    async def test_get_missing_node_returns_none(self) -> None:
        store = InMemoryGraphStore()
        result = await store.get_node("nonexistent")
        assert result is None

    async def test_upsert_merges_properties(self) -> None:
        store = InMemoryGraphStore()
        await store.upsert_node(GraphNode(id="n1", entity_type="x", properties={"a": 1}))
        await store.upsert_node(GraphNode(id="n1", entity_type="x", properties={"b": 2}))
        result = await store.get_node("n1")
        assert result is not None
        assert result.properties == {"a": 1, "b": 2}

    async def test_get_neighbors(self) -> None:
        store = InMemoryGraphStore()
        await store.upsert_node(GraphNode(id="a", entity_type="org"))
        await store.upsert_node(GraphNode(id="b", entity_type="model"))
        await store.upsert_edge(
            GraphEdge(id="e1", source_id="a", relation="publishes", target_id="b")
        )
        neighbors = await store.get_neighbors("a")
        assert len(neighbors) == 1
        assert neighbors[0].id == "b"

    async def test_get_neighbors_filtered_by_relation(self) -> None:
        store = InMemoryGraphStore()
        await store.upsert_node(GraphNode(id="a", entity_type="x"))
        await store.upsert_node(GraphNode(id="b", entity_type="y"))
        await store.upsert_node(GraphNode(id="c", entity_type="z"))
        await store.upsert_edge(GraphEdge(id="e1", source_id="a", relation="foo", target_id="b"))
        await store.upsert_edge(GraphEdge(id="e2", source_id="a", relation="bar", target_id="c"))

        foo_neighbors = await store.get_neighbors("a", relation="foo")
        assert len(foo_neighbors) == 1
        assert foo_neighbors[0].id == "b"

    async def test_search_by_type(self) -> None:
        store = InMemoryGraphStore()
        await store.upsert_node(GraphNode(id="a", entity_type="person"))
        await store.upsert_node(GraphNode(id="b", entity_type="person"))
        await store.upsert_node(GraphNode(id="c", entity_type="org"))

        persons = await store.search_by_type("person")
        assert len(persons) == 2
