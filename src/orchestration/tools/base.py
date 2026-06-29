from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from context import BaseContext
from enum import Enum


class BaseTool(ABC):

    @abstractmethod
    def execute(self, arg: dict):
        """
        Execute the tool with the given argument.

        Args:
            arg (dict): The argument for the tool execution.

        Returns:
            Any: The result of the tool execution.
        """
        pass

    @abstractmethod
    def schema(self) -> dict:
        """
        Return the schema of the tool.

        Returns:
            dict: The schema of the tool.
        """
        return {}