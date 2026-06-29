from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    @abstractmethod
    def execute(self, arg: dict) -> Any:
        """
        Execute the tool with the given argument.

        Args:
            arg (dict): The argument for the tool execution.

        Returns:
            Any: The result of the tool execution.
        """

    @abstractmethod
    def schema(self) -> dict:
        """
        Return the schema of the tool.

        Returns:
            dict: The schema of the tool.
        """
