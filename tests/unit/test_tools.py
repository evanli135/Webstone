"""Tests for orchestration.tools.base.BaseTool."""

from __future__ import annotations

import pytest

from orchestration.tools.base import BaseTool


class EchoTool(BaseTool):
    def execute(self, arg: dict):
        return arg

    def schema(self) -> dict:
        return {"name": "echo"}


def test_cannot_instantiate_abstract_base():
    with pytest.raises(TypeError):
        BaseTool()  # type: ignore[abstract]


def test_concrete_tool_execute_and_schema():
    tool = EchoTool()
    assert tool.execute({"x": 1}) == {"x": 1}
    assert tool.schema() == {"name": "echo"}
