from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from context import BaseContext
from enum import Enum

class ObservableType(Enum):
    """
    Enum representing different types of observations.
    """
    PROMPT
    COMMAND
    UPDATE
    COMPLETION

class Observable:
    """
    Class representing an observable entity.
    """

    def __init__(self, observable_type: ObservableType, data: Any):
        if not self._stringable(data):
            raise ValueError("Data must be stringable.")

        self.observable_type = observable_type
        self.data = data

    def _stringable(data: Any) -> bool:
        """
        Check if the data can be converted to a string.

        Args:
            data (Any): The data to check.
        """
        try:
            str(data)
            return True
        except:
            return False


class BaseAgent(ABC):
    """
    Base class for all agents.
    """

    def __init__(self, name: str, context: BaseContext):
        self.name = name
        self.context = context

    @abstractmethod
    def act(self, observation: Any) -> Any:
        """
        Perform an action based on the given observation.

        Args:
            observation (Any): The current observation from the environment.

        Returns:
            Any: The action to be taken by the agent.
        """
        pass

    def fork(self, name: Optional[str] = None, context: Optional[BaseContext] = None) -> BaseAgent:
        """
        Create a new instance of the agent with the same configuration.

        Returns:
            BaseAgent: A new instance of the agent, with the exact same context and configuration as the original agent.
        """
        if name is None:
            name = self.name
        if context is None:
            context = self.context
        return self.__class__(name, context)
