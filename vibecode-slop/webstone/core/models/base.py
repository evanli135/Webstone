"""Shared data models used across multiple layers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from webstone.core.state.base import ExecutionStatus, GraphState


class RetryPolicy(BaseModel):
    """Configuration for retry behavior on transient failures."""

    max_attempts: int = Field(default=3, ge=1, le=10)
    base_delay_seconds: float = Field(default=1.0, ge=0.1)
    max_delay_seconds: float = Field(default=60.0)
    exponential_base: float = Field(default=2.0)
    jitter: bool = True

    def delay_for_attempt(self, attempt: int) -> float:
        """Compute the delay (in seconds) for the given attempt number (1-indexed).

        Uses exponential backoff with optional jitter.
        """
        # TODO: implement jitter calculation
        import math

        delay = self.base_delay_seconds * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay_seconds)


class AgentConfig(BaseModel):
    """Per-agent configuration."""

    model_name: str = "claude-sonnet-4-6"
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    timeout_seconds: float = Field(default=120.0, ge=1.0)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    extra: dict[str, Any] = Field(default_factory=dict)


class ExecutionConfig(BaseModel):
    """Configuration for a single research execution run."""

    max_branches: int = Field(default=16, ge=1)
    max_depth: int = Field(default=3, ge=1)
    branch_prune_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    planner_config: AgentConfig = Field(default_factory=AgentConfig)
    reader_config: AgentConfig = Field(default_factory=AgentConfig)
    evaluator_config: AgentConfig = Field(default_factory=AgentConfig)


class RunResult(BaseModel):
    """The output of a completed research run."""

    run_id: str
    status: ExecutionStatus
    final_answer: str | None = None
    confidence_score: float | None = None
    total_branches: int = 0
    pruned_branches: int = 0
    error: str | None = None
    final_state: GraphState | None = None

    class Config:
        arbitrary_types_allowed = True
