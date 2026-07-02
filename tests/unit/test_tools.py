"""Tests for orchestration.tools.base.BaseTool (LangChain-backed)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from orchestration.tools.base import BaseTool


class AddArgs(BaseModel):
    a: int = Field(description="left operand")
    b: int = Field(description="right operand")


class AddTool(BaseTool):
    name: str = "add"
    description: str = "Add two integers."
    args_schema: type[BaseModel] = AddArgs

    def _run(self, a: int, b: int, **kwargs) -> int:
        return a + b


def test_execute_invokes_tool():
    assert AddTool().execute({"a": 2, "b": 3}) == 5


def test_json_schema_derived_from_args():
    schema = AddTool().json_schema()
    assert set(schema["properties"]) == {"a", "b"}
    assert schema["properties"]["a"]["description"] == "left operand"
