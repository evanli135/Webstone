from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseContext(ABC):
    """
    Base class for context objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def get(self, key: str) -> Any:
        """
        Get the value associated with the given key.

        Args:
            key (str): The key for which to retrieve the value.

        Returns:
            Any: The value associated with the key.
        """

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set the value associated with the given key.

        Args:
            key (str): The key for which to set the value.
            value (Any): The value to associate with the key.
        """
