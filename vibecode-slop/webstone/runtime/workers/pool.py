"""Worker pool implementation.

Workers consume tasks from the queue, execute the graph, and write results
to the checkpoint store. The pool manages worker lifecycle and graceful shutdown.

Satisfies: WorkerPoolProtocol

TODO: Implement multiprocessing-based pool for CPU parallelism in v0.3.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from webstone.runtime.queues.queue import InMemoryQueue

logger = logging.getLogger(__name__)


class WorkerPool:
    """Pool of asyncio tasks that consume from a shared queue.

    Each worker is a long-running asyncio coroutine. Workers are started
    once and run until stop() is called.

    Args:
        queue: The task queue to consume from.
        handler: Async function called with (task_id, payload) for each task.
        num_workers: Number of concurrent worker coroutines.
    """

    def __init__(
        self,
        queue: InMemoryQueue,
        handler: Any,  # AsyncCallable[[str, dict], None]
        num_workers: int = 4,
    ) -> None:
        self._queue = queue
        self._handler = handler
        self._num_workers = num_workers
        self._tasks: list[asyncio.Task[None]] = []
        self._active_count = 0
        self._running = False

    @property
    def active_count(self) -> int:
        """Number of workers currently processing a task."""
        return self._active_count

    async def start(self) -> None:
        """Spawn all worker coroutines."""
        if self._running:
            raise RuntimeError("WorkerPool is already running")
        self._running = True
        self._tasks = [
            asyncio.create_task(self._worker_loop(i), name=f"worker-{i}")
            for i in range(self._num_workers)
        ]
        logger.info("WorkerPool: started %d workers", self._num_workers)

    async def stop(self) -> None:
        """Gracefully stop all workers after they finish current tasks."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("WorkerPool: all workers stopped")

    async def _worker_loop(self, worker_id: int) -> None:
        """Main loop for a single worker."""
        logger.debug("WorkerPool: worker %d started", worker_id)
        while self._running:
            try:
                task_id, payload = await self._queue.dequeue()
                self._active_count += 1
                try:
                    await self._handler(task_id, payload)
                    await self._queue.ack(task_id)
                except Exception as exc:
                    logger.error("Worker %d: task=%s failed: %s", worker_id, task_id, exc)
                    await self._queue.nack(task_id, str(exc))
                finally:
                    self._active_count -= 1
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Worker %d: unexpected error: %s", worker_id, exc)
        logger.debug("WorkerPool: worker %d stopped", worker_id)
