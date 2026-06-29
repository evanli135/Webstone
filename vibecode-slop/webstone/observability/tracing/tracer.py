"""OpenTelemetry tracing setup and helpers.

Every graph node execution, agent invocation, and memory query should be
wrapped in a span. This provides end-to-end trace visibility across a
complete research run.

Usage:
    tracer = get_tracer()
    with tracer.start_span("planner.invoke") as span:
        span.set_attribute("run_id", state.run_id)
        result = await agent.invoke(state)

TODO: Add OTLP exporter to push traces to Jaeger/Tempo.
TODO: Propagate trace context across asyncio tasks (branch parallelism).
TODO: Auto-instrument LangChain LLM calls via opentelemetry-instrumentation-langchain.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Generator

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = logging.getLogger(__name__)

_tracer_provider: TracerProvider | None = None


def setup_tracing(service_name: str = "webstone", export_to_console: bool = False) -> None:
    """Initialize the global OpenTelemetry tracer provider.

    Called once at application startup. Idempotent — subsequent calls are no-ops.

    Args:
        service_name: Service name reported in traces.
        export_to_console: If True, export spans to stdout (useful for dev).
    """
    global _tracer_provider
    if _tracer_provider is not None:
        return

    provider = TracerProvider()

    if export_to_console:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # TODO: Add OTLP exporter:
    #   from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    #   provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_endpoint)))

    trace.set_tracer_provider(provider)
    _tracer_provider = provider
    logger.info("Tracing: initialized (service=%s)", service_name)


def get_tracer(name: str = "webstone") -> trace.Tracer:
    """Return a tracer for the given instrumentation scope."""
    return trace.get_tracer(name)


class WebstoneTracer:
    """Convenience wrapper for common tracing patterns in webstone.

    Provides higher-level helpers that set standard attributes
    (run_id, agent_role, node_name) automatically.
    """

    def __init__(self, tracer: trace.Tracer | None = None) -> None:
        self._tracer = tracer or get_tracer()

    @contextmanager
    def node_span(self, node_name: str, run_id: str) -> Generator[Any, None, None]:
        """Context manager for a graph node execution span."""
        with self._tracer.start_as_current_span(f"node.{node_name}") as span:
            span.set_attribute("node.name", node_name)
            span.set_attribute("run.id", run_id)
            yield span

    @contextmanager
    def agent_span(self, agent_role: str, run_id: str) -> Generator[Any, None, None]:
        """Context manager for an agent invocation span."""
        with self._tracer.start_as_current_span(f"agent.{agent_role}") as span:
            span.set_attribute("agent.role", agent_role)
            span.set_attribute("run.id", run_id)
            yield span
