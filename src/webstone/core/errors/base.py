"""Webstone exception hierarchy.

All exceptions inherit from WebstoneError so callers can catch the base
class when they want broad error handling, or specific subclasses when they
need to handle specific failure modes differently.
"""

from __future__ import annotations


class WebstoneError(Exception):
    """Root exception for all Webstone errors."""

    def __init__(self, message: str, run_id: str | None = None) -> None:
        super().__init__(message)
        self.run_id = run_id


class ConfigurationError(WebstoneError):
    """Raised when the system is misconfigured at startup."""


class GraphExecutionError(WebstoneError):
    """Raised when a graph execution fails unrecoverably."""

    def __init__(self, message: str, run_id: str | None = None, node: str | None = None) -> None:
        super().__init__(message, run_id)
        self.node = node


class AgentError(WebstoneError):
    """Raised when an agent invocation fails."""

    def __init__(
        self, message: str, run_id: str | None = None, agent_role: str | None = None
    ) -> None:
        super().__init__(message, run_id)
        self.agent_role = agent_role


class BranchError(WebstoneError):
    """Raised when a search branch fails."""

    def __init__(
        self, message: str, run_id: str | None = None, branch_id: str | None = None
    ) -> None:
        super().__init__(message, run_id)
        self.branch_id = branch_id


class MemoryError(WebstoneError):  # noqa: A001 — shadows builtin intentionally in this namespace
    """Raised on graph or vector store failures."""


class QueueError(WebstoneError):
    """Raised on task queue failures (enqueue, dequeue, ack)."""


class CheckpointError(WebstoneError):
    """Raised on checkpoint read/write failures."""
