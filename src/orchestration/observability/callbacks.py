"""Bridge LangChain runtime events into a project telemetry backend.

Attach a :class:`TelemetryCallbackHandler` to any LangChain call
(``model.invoke(..., config={"callbacks": [handler]})``) and its LLM and tool
executions are recorded as project telemetry events — no need to hand-instrument
each call site.
"""

from __future__ import annotations

import time
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler

from orchestration.observability.base import (
    AgentEvent,
    BaseTelemetry,
    ErrorEvent,
    ToolEvent,
)


class TelemetryCallbackHandler(BaseCallbackHandler):
    """Forward LangChain LLM/tool callbacks to a :class:`BaseTelemetry` backend."""

    def __init__(self, telemetry: BaseTelemetry, agent_id: str = "unknown") -> None:
        self.telemetry = telemetry
        self.agent_id = agent_id
        self._llm_starts: dict[UUID, float] = {}
        self._tool_starts: dict[UUID, tuple[float, str, dict]] = {}

    # -- LLM / chat model ---------------------------------------------------

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], *, run_id: UUID, **kwargs: Any
    ) -> None:
        self._llm_starts[run_id] = time.perf_counter()

    def on_chat_model_start(
        self, serialized: dict[str, Any], messages: Any, *, run_id: UUID, **kwargs: Any
    ) -> None:
        self._llm_starts[run_id] = time.perf_counter()

    def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs: Any) -> None:
        self.telemetry.record_agent(
            AgentEvent(
                agent_id=self.agent_id,
                action="llm",
                duration_ms=self._elapsed(self._llm_starts.pop(run_id, None)),
                success=True,
            )
        )

    def on_llm_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        self._llm_starts.pop(run_id, None)
        self.telemetry.record_error(ErrorEvent(agent_id=self.agent_id, error=str(error)))

    # -- Tools --------------------------------------------------------------

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        name = (serialized or {}).get("name", "tool")
        args = inputs if isinstance(inputs, dict) else {"input": input_str}
        self._tool_starts[run_id] = (time.perf_counter(), name, args)

    def on_tool_end(self, output: Any, *, run_id: UUID, **kwargs: Any) -> None:
        start, name, args = self._tool_starts.pop(run_id, (None, "tool", {}))
        self.telemetry.record_tool(
            ToolEvent(
                agent_id=self.agent_id,
                tool=name,
                args=args,
                duration_ms=self._elapsed(start),
                success=True,
            )
        )

    def on_tool_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        start, name, args = self._tool_starts.pop(run_id, (None, "tool", {}))
        self.telemetry.record_tool(
            ToolEvent(
                agent_id=self.agent_id,
                tool=name,
                args=args,
                duration_ms=self._elapsed(start),
                success=False,
                error=str(error),
            )
        )

    # -- Internal -----------------------------------------------------------

    @staticmethod
    def _elapsed(start: float | None) -> float:
        """Milliseconds since ``start`` (0.0 if the start was never recorded)."""
        if start is None:
            return 0.0
        return (time.perf_counter() - start) * 1000.0
