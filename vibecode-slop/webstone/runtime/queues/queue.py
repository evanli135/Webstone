"""Queue implementations.

Satisfies: QueueProtocol

Current: In-memory asyncio.Queue for development.
Future: Redis Streams backend for distributed deployments.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class InMemoryQueue:
    """Thin wrapper around asyncio.Queue satisfying QueueProtocol.

    Not suitable for multi-process or distributed deployments.
    Tasks are lost on restart.

    TODO: Implement RedisStreamQueue backed by redis-py Streams for v0.3.
    """

    def __init__(self, maxsize: int = 0) -> None:
        self._queue: asyncio.Queue[tuple[str, dict[str, Any]]] = asyncio.Queue(maxsize=maxsize)
        self._processing: dict[str, dict[str, Any]] = {}

    async def enqueue(self, task_id: str, payload: dict[str, Any]) -> None:
        """Add a task to the queue."""
        await self._queue.put((task_id, payload))
        logger.debug("Queue: enqueued task=%s", task_id)

    async def dequeue(self) -> tuple[str, dict[str, Any]]:
        """Remove and return the next task. Blocks until one is available."""
        task_id, payload = await self._queue.get()
        self._processing[task_id] = payload
        return task_id, payload

    async def ack(self, task_id: str) -> None:
        """Acknowledge successful processing."""
        self._processing.pop(task_id, None)
        self._queue.task_done()
        logger.debug("Queue: acked task=%s", task_id)

    async def nack(self, task_id: str, reason: str) -> None:
        """Mark a task as failed. Re-enqueues it for retry.

        TODO: Add max-retry counter; dead-letter queue for exhausted tasks.
        """
        payload = self._processing.pop(task_id, None)
        if payload is not None:
            logger.warning("Queue: nacked task=%s reason=%s, re-enqueuing", task_id, reason)
            await self._queue.put((task_id, payload))
        self._queue.task_done()

    @property
    def size(self) -> int:
        """Current number of tasks waiting in the queue."""
        return self._queue.qsize()
