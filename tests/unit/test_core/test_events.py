"""Unit tests for domain event models."""

from __future__ import annotations

from webstone.core.events.base import (
    AgentStartedEvent,
    EventType,
    GraphStartedEvent,
)


class TestDomainEvents:
    def test_event_id_is_unique(self) -> None:
        e1 = GraphStartedEvent(run_id="run-1", data={})
        e2 = GraphStartedEvent(run_id="run-1", data={})
        assert e1.event_id != e2.event_id

    def test_event_type(self) -> None:
        e = GraphStartedEvent(run_id="run-1", data={})
        assert e.event_type == EventType.GRAPH_STARTED
        assert e.topic == "graph"

    def test_json_safe_dump(self) -> None:
        e = AgentStartedEvent(run_id="run-1", data={"role": "planner"})
        d = e.model_dump_json_safe()
        assert isinstance(d["occurred_at"], str)  # ISO format, not datetime object
        assert "T" in d["occurred_at"]
