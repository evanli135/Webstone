from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

class BaseContext(ABC):
    """
    Base class for context objects.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @abstractmethod
    def get(self, key: str) -> Any:
        """
        Get the value associated with the given key.

        Args:
            key (str): The key for which to retrieve the value.

        Returns:
            Any: The value associated with the key.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set the value associated with the given key.

        Args:
            key (str): The key for which to set the value.
            value (Any): The value to associate with the key.
        """
        pass