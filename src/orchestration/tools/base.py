"""Tool base built on ``langchain_core.tools.BaseTool``.

Subclasses declare ``name``, ``description`` and (optionally) an ``args_schema``
pydantic model, then implement ``_run``. The argument JSON schema is derived by
LangChain from that model, so there is no hand-written schema to keep in sync.
"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool as LangChainBaseTool


class BaseTool(LangChainBaseTool):
    """Project tool base. Abstract until a subclass implements ``_run``."""

    def execute(self, arg: dict) -> Any:
        """Invoke the tool with a mapping of arguments."""
        return self.invoke(arg)

    def json_schema(self) -> dict:
        """Return the JSON schema for this tool's arguments (derived by LangChain)."""
        # LangChain types get_input_schema() as a pydantic v1-or-v2 model class;
        # langchain_core 1.x always yields v2, which exposes model_json_schema().
        schema = self.get_input_schema()
        return schema.model_json_schema()  # pyright: ignore[reportAttributeAccessIssue]
