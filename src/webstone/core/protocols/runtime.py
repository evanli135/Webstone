"""Runtime layer protocols.

These define the execution infrastructure contracts. The current Python
implementation satisfies these protocols. The future Go sidecar will also
satisfy them via gRPC-backed Python stubs — no changes to cognitive code needed.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, runtime_checkable

from webstone.core.events.base import DomainEvent
from webstone.core.state.base import GraphState


@runtime_checkable
class QueueProtocol(Protocol):
    """FIFO task queue abstraction.

    Current backend: asyncio.Queue (in-memory)
    Future backends: Redis Streams, SQS, Pub/Sub
    """

    async def enqueue(self, task_id: str, payload: dict[str, Any]) -> None:
        """Add a task to the queue."""
        ...

    async def dequeue(self) -> tuple[str, dict[str, Any]]:
        """Remove and return the next task. Blocks until one is available."""
        ...

    async def ack(self, task_id: str) -> None:
        """Acknowledge successful processing of a task."""
        ...

    async def nack(self, task_id: str, reason: str) -> None:
        """Mark a task as failed and return it for retry."""
        ...


@runtime_checkable
class SchedulerProtocol(Protocol):
    """Task scheduler for distributing work across workers."""

    async def submit(self, state: GraphState) -> str:
        """Submit a graph execution job. Returns a job ID."""
        ...

    async def cancel(self, job_id: str) -> None:
        """Cancel a running or pending job."""
        ...

    async def status(self, job_id: str) -> str:
        """Return the current status of a job."""
        ...


@runtime_checkable
class WorkerPoolProtocol(Protocol):
    """Pool of workers that consume tasks from the queue."""

    async def start(self) -> None:
        """Start all workers."""
        ...

    async def stop(self) -> None:
        """Gracefully stop all workers, draining in-flight work."""
        ...

    @property
    def active_count(self) -> int:
        """Number of currently active (non-idle) workers."""
        ...


@runtime_checkable
class CheckpointStoreProtocol(Protocol):
    """Durable checkpoint store for graph execution state.

    Enables resuming interrupted runs without restarting from scratch.
    """

    async def save(self, run_id: str, state: GraphState) -> None:
        """Persist a state snapshot for the given run."""
        ...

    async def load(self, run_id: str) -> GraphState | None:
        """Load the most recent checkpoint for a run. None if not found."""
        ...

    async def delete(self, run_id: str) -> None:
        """Delete all checkpoints for a run (cleanup after completion)."""
        ...


@runtime_checkable
class EventBusProtocol(Protocol):
    """Async event bus for domain event streaming.

    Consumers (WebSocket handlers, metrics collectors) subscribe to receive
    events. Producers (graph nodes, agents) publish without knowing who listens.
    """

    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to all subscribers."""
        ...

    def subscribe(self, topic: str) -> AsyncIterator[DomainEvent]:
        """Subscribe to events on the given topic. Returns an async generator."""
        ...
