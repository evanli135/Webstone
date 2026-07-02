"""Model configuration and chat-model construction.

Keeps a small, explicit config object under our control and defers to
``langchain_anthropic.ChatAnthropic`` for the actual client, so we don't
re-implement provider wiring.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from enum import Enum

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class ModelType(Enum):
    """Enum representing different types of models."""

    HAIKU = "claude-haiku-4-5-20251001"
    SONNET = "claude-sonnet-5"
    OPUS = "claude-opus-4.8"


class AgentConfig(BaseModel):
    """Tunables for an agent's language model."""

    model_name: ModelType = Field(default=ModelType.SONNET)
    temperature: float = 0.0
    max_tokens: int | None = Field(default=None, ge=1)



def build_chat_model(config: AgentConfig | None = None) -> BaseChatModel:
    """
    Construct a chat model from an :class:`AgentConfig`.

    The provider client (``ChatAnthropic``) is imported lazily so that importing
    this module does not require ``langchain_anthropic`` or an API key until a
    model is actually built. The Anthropic API key is read from the environment
    (``ANTHROPIC_API_KEY``) by the client.
    """
    from langchain_anthropic import ChatAnthropic

    config = config or AgentConfig()
    kwargs: dict[str, Any] = {
        "model": config.model_name,
        "temperature": config.temperature,
    }
    if config.max_tokens is not None:
        kwargs["max_tokens"] = config.max_tokens
    return ChatAnthropic(**kwargs)
