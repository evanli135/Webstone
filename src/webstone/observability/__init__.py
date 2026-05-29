"""Observability layer — tracing, metrics, structured logging, and event bus.

All observability is OpenTelemetry-compatible. This layer sits in the execution
side of the architecture: cognitive components emit events, this layer routes
them to backends (Jaeger, Prometheus, stdout).
"""
