from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ErrorEvent:
    agent_id: str
    error: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FetchEvent:
    source: str  # "semantic_scholar" | "arxiv"
    query: str
    duration_ms: float
    result_count: int
    success: bool
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentEvent:
    agent_id: str
    action: str
    duration_ms: float
    success: bool
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ToolEvent:
    agent_id: str  # who invoked it
    tool: str  # e.g. "fetch_arxiv", "search_memory"
    args: dict
    duration_ms: float
    success: bool
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentActionEvent:
    source_agent_id: str  # who triggered the action
    target_agent_id: str  # who received it (same as source for self-actions)
    action: str  # e.g. "fork", "evaluate", "interrupt", "delegate"
    result: str | None = None  # e.g. spawned agent id for a fork
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BaseTelemetry(ABC):
    @abstractmethod
    def record_agent(self, event: AgentEvent) -> None:
        """Record a general agent lifecycle event."""

    @abstractmethod
    def record_fetch(self, event: FetchEvent) -> None:
        """Record a paper/data fetch from an external source."""

    @abstractmethod
    def record_error(self, event: ErrorEvent) -> None:
        """Record an agent error."""

    @abstractmethod
    def record_tool(self, event: ToolEvent) -> None:
        """Record a tool invocation by an agent."""

    @abstractmethod
    def record_agent_action(self, event: AgentActionEvent) -> None:
        """Record an agent acting on itself or another agent (fork, delegate, etc.)."""
