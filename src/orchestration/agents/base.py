from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any

from orchestration.context.base import BaseContext


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


class BaseAgent(ABC):
    """
    Base class for all agents.
    """

    def __init__(self, name: str, context: BaseContext) -> None:
        self.name = name
        self.context = context
        raise NotImplementedError

    @abstractmethod
    def act(self, observation: Any) -> Any:
        """
        Perform an action based on the given observation.

        Args:
            observation (Any): The current observation from the environment.

        Returns:
            Any: The action to be taken by the agent.
        """
        raise NotImplementedError

    def fork(self, name: str | None = None, context: BaseContext | None = None) -> BaseAgent:
        """
        Create a new instance of the agent with the same configuration.

        Returns:
            BaseAgent: A new instance of the agent, with the exact same context
            and configuration as the original agent.
        """
        if name is None:
            name = self.name
        if context is None:
            context = self.context
        raise NotImplementedError
