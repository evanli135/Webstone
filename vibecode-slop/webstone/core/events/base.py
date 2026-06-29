"""Domain event models.

All events inherit from DomainEvent which provides a stable envelope with
run_id, timestamp, and topic routing. Events are serializable to JSON for
streaming over WebSocket and writing to the event log.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EventType(StrEnum):
    GRAPH_STARTED = "graph.started"
    GRAPH_COMPLETED = "graph.completed"
    GRAPH_FAILED = "graph.failed"
    NODE_STARTED = "node.started"
    NODE_COMPLETED = "node.completed"
    NODE_FAILED = "node.failed"
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    BRANCH_CREATED = "branch.created"
    BRANCH_PRUNED = "branch.pruned"
    MEMORY_READ = "memory.read"
    MEMORY_WRITTEN = "memory.written"
    CHECKPOINT_SAVED = "checkpoint.saved"
    CHECKPOINT_LOADED = "checkpoint.loaded"


class DomainEvent(BaseModel):
    """Base class for all domain events.

    Every event carries the run_id so consumers can correlate events across
    a single research execution. The `data` field holds event-specific payload.
    """

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    run_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    topic: str  # routing key for event bus subscriptions
    data: dict[str, Any] = Field(default_factory=dict)

    def model_dump_json_safe(self) -> dict[str, Any]:
        """Return a JSON-serializable dict (datetimes as ISO strings)."""
        d = self.model_dump()
        d["occurred_at"] = self.occurred_at.isoformat()
        return d


class GraphStartedEvent(DomainEvent):
    event_type: EventType = EventType.GRAPH_STARTED
    topic: str = "graph"


class GraphCompletedEvent(DomainEvent):
    event_type: EventType = EventType.GRAPH_COMPLETED
    topic: str = "graph"


class NodeStartedEvent(DomainEvent):
    event_type: EventType = EventType.NODE_STARTED
    topic: str = "node"


class NodeCompletedEvent(DomainEvent):
    event_type: EventType = EventType.NODE_COMPLETED
    topic: str = "node"


class AgentStartedEvent(DomainEvent):
    event_type: EventType = EventType.AGENT_STARTED
    topic: str = "agent"


class AgentCompletedEvent(DomainEvent):
    event_type: EventType = EventType.AGENT_COMPLETED
    topic: str = "agent"


class BranchPrunedEvent(DomainEvent):
    event_type: EventType = EventType.BRANCH_PRUNED
    topic: str = "branch"
