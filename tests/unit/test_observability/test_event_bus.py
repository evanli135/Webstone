"""Unit tests for the in-memory event bus."""

from __future__ import annotations

import asyncio

import pytest

from webstone.core.events.base import GraphStartedEvent
from webstone.observability.events.bus import InMemoryEventBus


@pytest.mark.asyncio
class TestInMemoryEventBus:
    async def test_publish_and_receive(self) -> None:
        bus = InMemoryEventBus()
        received: list[GraphStartedEvent] = []

        async def consumer() -> None:
            async for event in bus.subscribe("graph"):
                received.append(event)  # type: ignore[arg-type]
                break  # receive one event and stop

        consumer_task = asyncio.create_task(consumer())

        # Give consumer time to subscribe
        await asyncio.sleep(0)

        event = GraphStartedEvent(run_id="test-run", data={})
        await bus.publish(event)

        await consumer_task
        assert len(received) == 1
        assert received[0].run_id == "test-run"

    async def test_subscriber_count(self) -> None:
        bus = InMemoryEventBus()
        assert bus.subscriber_count("graph") == 0

    async def test_no_subscribers_no_error(self) -> None:
        bus = InMemoryEventBus()
        event = GraphStartedEvent(run_id="test-run", data={})
        # Should not raise even with no subscribers
        await bus.publish(event)
