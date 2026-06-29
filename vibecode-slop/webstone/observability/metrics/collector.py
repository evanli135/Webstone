"""OpenTelemetry metrics integration.

Tracks key operational metrics:
  - webstone.runs.started / completed / failed
  - webstone.branches.created / pruned
  - webstone.agent.latency (histogram per role)
  - webstone.memory.queries

TODO: Wire up OTLP metrics exporter.
TODO: Add Prometheus-compatible scrape endpoint via FastAPI route.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

logger = logging.getLogger(__name__)

_meter_provider: MeterProvider | None = None


def setup_metrics(export_to_console: bool = False) -> None:
    """Initialize the global OpenTelemetry meter provider.

    TODO: Add OTLP metrics exporter for production.
    """
    global _meter_provider
    if _meter_provider is not None:
        return

    readers = []
    if export_to_console:
        readers.append(PeriodicExportingMetricReader(ConsoleMetricExporter()))

    provider = MeterProvider(metric_readers=readers)
    metrics.set_meter_provider(provider)
    _meter_provider = provider
    logger.info("Metrics: initialized")


def get_metrics(name: str = "webstone") -> "MetricsCollector":
    """Return a MetricsCollector for the given instrumentation scope."""
    return MetricsCollector(metrics.get_meter(name))


class MetricsCollector:
    """Convenience wrapper that creates and caches OTel instruments.

    Usage:
        m = get_metrics()
        m.record_run_started()
        async with m.agent_latency("planner"):
            await planner.invoke(state)
    """

    def __init__(self, meter: metrics.Meter) -> None:
        self._meter = meter

        # Counters
        self._runs_started = meter.create_counter("webstone.runs.started")
        self._runs_completed = meter.create_counter("webstone.runs.completed")
        self._runs_failed = meter.create_counter("webstone.runs.failed")
        self._branches_created = meter.create_counter("webstone.branches.created")
        self._branches_pruned = meter.create_counter("webstone.branches.pruned")
        self._memory_queries = meter.create_counter("webstone.memory.queries")

        # Histograms
        self._agent_latency = meter.create_histogram(
            "webstone.agent.latency",
            unit="s",
            description="Agent invocation latency in seconds",
        )

    def record_run_started(self) -> None:
        self._runs_started.add(1)

    def record_run_completed(self) -> None:
        self._runs_completed.add(1)

    def record_run_failed(self) -> None:
        self._runs_failed.add(1)

    def record_branch_created(self, count: int = 1) -> None:
        self._branches_created.add(count)

    def record_branch_pruned(self, count: int = 1) -> None:
        self._branches_pruned.add(count)

    def record_memory_query(self) -> None:
        self._memory_queries.add(1)

    @asynccontextmanager
    async def agent_latency(self, role: str) -> AsyncGenerator[None, None]:
        """Async context manager that records agent invocation latency."""
        start = time.monotonic()
        try:
            yield
        finally:
            elapsed = time.monotonic() - start
            self._agent_latency.record(elapsed, {"agent.role": role})
