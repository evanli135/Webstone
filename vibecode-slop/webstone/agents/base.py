"""Base agent implementation.

All concrete agents inherit from BaseAgent to get shared LLM construction,
retry logic, and event emission. The base class is intentionally thin —
it provides infrastructure, not reasoning.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

from webstone.core.models.base import AgentConfig
from webstone.core.state.base import AgentRole, GraphState

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base for all Webstone agents.

    Subclasses implement `invoke` and declare their `role`. The base class
    handles LLM construction and provides a hook for future telemetry injection.
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self._llm: BaseChatModel | None = None

    @property
    @abstractmethod
    def role(self) -> AgentRole:
        """The role this agent plays in the research graph."""
        ...

    @abstractmethod
    async def invoke(self, state: GraphState, **kwargs: Any) -> dict[str, Any]:
        """Execute the agent. Returns a partial GraphState update dict."""
        ...

    def get_llm(self) -> BaseChatModel:
        """Lazily construct and cache the LLM client."""
        if self._llm is None:
            self._llm = self._build_llm()
        return self._llm

    def _build_llm(self) -> BaseChatModel:
        """Construct the LLM backend from config.

        TODO: Support additional providers (OpenAI, Gemini) via config.
        """
        return ChatAnthropic(  # type: ignore[call-arg]
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role={self.role}, model={self.config.model_name})"
