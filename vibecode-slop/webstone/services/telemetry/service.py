"""Telemetry service — initializes all observability backends at startup.

Called once from the FastAPI lifespan. Configures tracing, metrics,
and structured logging based on application settings.
"""

from __future__ import annotations

import logging
import sys

import structlog

from webstone.config.settings import Settings
from webstone.observability.metrics.collector import setup_metrics
from webstone.observability.tracing.tracer import setup_tracing


class TelemetryService:
    """Bootstraps all observability backends from application settings."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def initialize(self) -> None:
        """Initialize all telemetry backends. Call once at startup."""
        self._setup_logging()

        if self._settings.tracing_enabled:
            setup_tracing(
                service_name=self._settings.otel_service_name,
                export_to_console=self._settings.is_development,
            )

        if self._settings.metrics_enabled:
            setup_metrics(export_to_console=self._settings.is_development)

    def _setup_logging(self) -> None:
        """Configure structlog for structured JSON logging in production."""
        log_level = getattr(logging, self._settings.log_level)

        if self._settings.is_production:
            processors = [
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ]
            renderer = structlog.processors.JSONRenderer()
        else:
            processors = [
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="%H:%M:%S"),
                structlog.dev.ConsoleRenderer(),
            ]
            renderer = structlog.dev.ConsoleRenderer()

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(sys.stdout),
            wrapper_class=structlog.BoundLogger,
            cache_logger_on_first_use=True,
        )

        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=log_level,
        )
