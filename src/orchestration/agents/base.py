from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from orchestration.context.base import BaseContext
from orchestration.models.base import AgentConfig, build_chat_model
from orchestration.observability.base import BaseTelemetry

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class ObservableType(Enum):
    """
    Enum representing different types of observations.
    """

    PROMPT = auto()
    COMMAND = auto()
    UPDATE = auto()
    COMPLETION = auto()


class Observable:
    """
    Class representing an observable entity.
    """

    def __init__(self, observable_type: ObservableType, data: Any) -> None:
        if not self._stringable(data):
            raise ValueError("Data must be stringable.")

        self.observable_type = observable_type
        self.data = data

    @staticmethod
    def _stringable(data: Any) -> bool:
        """
        Check if the data can be converted to a string.

        Args:
            data (Any): The data to check.
        """
        try:
            str(data)
            return True
        except Exception:
            return False


class Agent(ABC):
    """
    Abstract agent interface.

    This is the contract to program against: annotate parameters and return
    values as ``Agent`` and depend only on the members declared here. Concrete
    agents typically extend :class:`BaseAgent`, which supplies the shared
    implementation, but any object honoring this interface is a valid agent.
    """

    name: str
    context: BaseContext

    @abstractmethod
    def act(self, observation: Any) -> Any:
        """
        Perform an action based on the given observation.

        Args:
            observation (Any): The current observation from the environment.

        Returns:
            Any: The action to be taken by the agent.
        """

    @abstractmethod
    def fork(self, name: str | None = None, context: BaseContext | None = None) -> Agent:
        """
        Create a new agent with the same configuration.

        Args:
            name (str | None): Name for the new agent; defaults to this agent's name.
            context (BaseContext | None): Context for the new agent; defaults to
                this agent's context.

        Returns:
            Agent: A new agent with the given (or inherited) name and context.
        """


class BaseAgent(Agent):
    """
    Composable base implementation of :class:`Agent`.

    Concrete agents subclass this and implement :meth:`act`. Construction,
    telemetry wiring, and :meth:`fork` are provided here so subclasses only
    supply behavior. ``BaseAgent`` itself is abstract because :meth:`act` is
    left unimplemented.
    """

    def __init__(
        self,
        name: str,
        context: BaseContext,
        *,
        config: AgentConfig | None = None,
        model: BaseChatModel | None = None,
    ) -> None:
        self.name = name
        self.context = context
        self.base_telemetry: BaseTelemetry = context.get("telemetry")
        self.config: AgentConfig = config or AgentConfig()
        self._model = model

    @property
    def model(self) -> BaseChatModel:
        """
        The agent's chat model, built lazily from :attr:`config` on first use.

        Inject a model via the constructor to override (e.g. in tests); otherwise
        it is constructed on demand so agents that never call an LLM stay cheap.
        """
        if self._model is None:
            self._model = build_chat_model(self.config)
        return self._model

    def fork(self, name: str | None = None, context: BaseContext | None = None) -> BaseAgent:
        """
        Create a new instance of the same agent type with the same configuration.

        Returns:
            BaseAgent: A new instance of this agent's concrete type, carrying the
            given (or inherited) name and context, plus this agent's config and
            model.
        """
        return type(self)(
            name if name is not None else self.name,
            context if context is not None else self.context,
            config=self.config,
            model=self._model,
        )
