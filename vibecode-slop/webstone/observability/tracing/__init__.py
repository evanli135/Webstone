"""Distributed tracing integration."""

from webstone.observability.tracing.tracer import WebstoneTracer, get_tracer, setup_tracing

__all__ = ["WebstoneTracer", "get_tracer", "setup_tracing"]
