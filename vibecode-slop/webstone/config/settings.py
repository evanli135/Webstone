"""Application settings loaded from environment variables and .env file.

All configuration is centralized here. No scattered os.getenv() calls
in business logic — always import from this module.

Pydantic Settings v2 loads from:
  1. .env file (if present)
  2. Environment variables (override .env)

Usage:
    from webstone.config import get_settings
    settings = get_settings()
    print(settings.anthropic_api_key)
"""

from __future__ import annotations

import functools
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration for webstone."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WEBSTONE_",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ────────────────────────────────────────────────────────────────────
    anthropic_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias="ANTHROPIC_API_KEY",
        description="Anthropic API key for Claude models",
    )
    model_name: str = Field(default="claude-sonnet-4-6")

    # ── Runtime ────────────────────────────────────────────────────────────────
    env: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_workers: int = Field(default=8, ge=1)
    max_branches: int = Field(default=256, ge=1)

    # ── Memory ─────────────────────────────────────────────────────────────────
    graph_store_backend: Literal["memory", "neo4j", "kuzu"] = "memory"
    vector_store_backend: Literal["memory", "qdrant", "pinecone", "chroma"] = "memory"
    vector_store_url: str = ""
    vector_store_api_key: SecretStr = SecretStr("")

    # ── Queue ──────────────────────────────────────────────────────────────────
    queue_backend: Literal["memory", "redis"] = "memory"
    redis_url: str = "redis://localhost:6379/0"

    # ── Checkpoints ────────────────────────────────────────────────────────────
    checkpoint_backend: Literal["memory", "sqlite", "postgres"] = "memory"
    database_url: str = "sqlite:///webstone.db"

    # ── Observability ──────────────────────────────────────────────────────────
    otel_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "webstone"
    metrics_enabled: bool = True
    tracing_enabled: bool = True

    # ── API ────────────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_workers: int = Field(default=1, ge=1)

    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        return self.env == "production"


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton Settings instance (cached after first call)."""
    return Settings()
