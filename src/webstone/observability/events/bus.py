"""In-process async event bus.

Producers publish DomainEvents; consumers subscribe to a topic and receive
them via async generators. The WebSocket handler subscribes to broadcast
events to connected clients.

This is the pub/sub backbone for streaming observability.

Satisfies: EventBusProtocol

TODO: Replace with Redis Pub/Sub for multi-process deployments.
TODO: Add durable event log (append-only) for replay.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict

from webstone.core.events.base import DomainEvent

logger = logging.getLogger(__name__)


class InMemoryEventBus:
    """Asyncio-based in-process pub/sub event bus.

    Subscribers receive all events published to their subscribed topic.
    Slow consumers are detected and warned when their queue fills up.

    Args:
        max_queue_size: Maximum events buffered per subscriber before warning.
    """

    def __init__(self, max_queue_size: int = 1000) -> None:
        self._max_queue_size = max_queue_size
        # topic -> list of subscriber queues
        self._subscribers: dict[str, list[asyncio.Queue[DomainEvent]]] = defaultdict(list)
        self._published_count = 0

    async def publish(self, event: DomainEvent) -> None:
        """Broadcast an event to all subscribers of event.topic."""
        queues = self._subscribers.get(event.topic, [])
        for q in queues:
            if q.full():
                logger.warning("EventBus: subscriber queue full for topic=%s", event.topic)
            else:
                await q.put(event)
        self._published_count += 1
        logger.debug("EventBus: published %s to %d subscribers", event.event_type, len(queues))

    async def subscribe(self, topic: str):  # noqa: ANN201
        """Subscribe to events on a topic. Yields events as an async generator.

        Usage:
            async for event in bus.subscribe("agent"):
                handle(event)
        """
        queue: asyncio.Queue[DomainEvent] = asyncio.Queue(maxsize=self._max_queue_size)
        self._subscribers[topic].append(queue)
        logger.debug("EventBus: new subscriber for topic=%s", topic)

        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self._subscribers[topic].remove(queue)
            logger.debug("EventBus: subscriber disconnected from topic=%s", topic)

    def subscriber_count(self, topic: str) -> int:
        """Number of active subscribers for a topic."""
        return len(self._subscribers.get(topic, []))
