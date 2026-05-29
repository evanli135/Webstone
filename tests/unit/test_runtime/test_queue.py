"""Unit tests for the in-memory queue."""

from __future__ import annotations

import pytest

from webstone.runtime.queues.queue import InMemoryQueue


@pytest.mark.asyncio
class TestInMemoryQueue:
    async def test_enqueue_dequeue(self) -> None:
        q = InMemoryQueue()
        await q.enqueue("task-1", {"payload": "hello"})
        task_id, payload = await q.dequeue()
        assert task_id == "task-1"
        assert payload == {"payload": "hello"}

    async def test_ack_removes_from_processing(self) -> None:
        q = InMemoryQueue()
        await q.enqueue("task-1", {})
        task_id, _ = await q.dequeue()
        await q.ack(task_id)
        assert q.size == 0

    async def test_nack_requeues(self) -> None:
        q = InMemoryQueue()
        await q.enqueue("task-1", {"data": 42})
        task_id, _ = await q.dequeue()
        await q.nack(task_id, "transient error")
        assert q.size == 1  # re-enqueued

    async def test_size(self) -> None:
        q = InMemoryQueue()
        assert q.size == 0
        await q.enqueue("a", {})
        await q.enqueue("b", {})
        assert q.size == 2
