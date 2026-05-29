"""In-process task scheduler.

The current implementation runs graph executions directly in the calling
event loop using asyncio tasks. Future implementation will hand off work
to a distributed worker pool via the queue layer.

Satisfies: SchedulerProtocol
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from webstone.core.state.base import ExecutionStatus, GraphState

logger = logging.getLogger(__name__)


class InProcessScheduler:
    """Simple asyncio-based scheduler for development and single-node deployments.

    Limitations:
    - No persistence: job status is lost on restart
    - No horizontal scaling
    - Bounded concurrency via asyncio semaphore

    TODO: Replace with a Redis-backed distributed scheduler in v0.3.
    """

    def __init__(self, max_concurrent: int = 8) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._jobs: dict[str, asyncio.Task[Any]] = {}
        self._results: dict[str, GraphState] = {}
        self._statuses: dict[str, ExecutionStatus] = {}

    async def submit(self, graph: Any, initial_state: dict[str, Any]) -> str:
        """Submit a graph execution job.

        Args:
            graph: A compiled LangGraph graph.
            initial_state: Initial state dict for the execution.

        Returns:
            A job ID for status tracking.
        """
        job_id = str(uuid.uuid4())
        self._statuses[job_id] = ExecutionStatus.PENDING

        task = asyncio.create_task(
            self._run(job_id, graph, initial_state),
            name=f"job-{job_id[:8]}",
        )
        self._jobs[job_id] = task
        logger.info("Scheduler: submitted job=%s", job_id)
        return job_id

    async def cancel(self, job_id: str) -> None:
        """Cancel a running or pending job."""
        task = self._jobs.get(job_id)
        if task and not task.done():
            task.cancel()
            self._statuses[job_id] = ExecutionStatus.CANCELLED
            logger.info("Scheduler: cancelled job=%s", job_id)

    async def status(self, job_id: str) -> str:
        """Return the current status string for a job."""
        return self._statuses.get(job_id, "not_found")

    async def result(self, job_id: str) -> GraphState | None:
        """Block until the job completes and return the final state.

        Returns None if the job is not found or was cancelled.
        """
        task = self._jobs.get(job_id)
        if task is None:
            return None
        await asyncio.wait_for(asyncio.shield(task), timeout=None)
        return self._results.get(job_id)

    async def _run(self, job_id: str, graph: Any, initial_state: dict[str, Any]) -> None:
        """Internal coroutine that executes the graph under the semaphore."""
        async with self._semaphore:
            self._statuses[job_id] = ExecutionStatus.RUNNING
            try:
                raw = await graph.ainvoke(initial_state)
                result = GraphState.model_validate(raw)
                self._results[job_id] = result
                self._statuses[job_id] = ExecutionStatus.COMPLETED
                logger.info("Scheduler: completed job=%s", job_id)
            except asyncio.CancelledError:
                self._statuses[job_id] = ExecutionStatus.CANCELLED
                raise
            except Exception as exc:
                logger.exception("Scheduler: job=%s failed: %s", job_id, exc)
                self._statuses[job_id] = ExecutionStatus.FAILED
