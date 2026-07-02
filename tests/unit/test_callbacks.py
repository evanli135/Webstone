"""Tests for the LangChain -> telemetry callback bridge."""

from __future__ import annotations

from uuid import uuid4

from orchestration.observability.base import (
    AgentActionEvent,
    AgentEvent,
    BaseTelemetry,
    ErrorEvent,
    FetchEvent,
    ToolEvent,
)
from orchestration.observability.callbacks import TelemetryCallbackHandler


class CollectingTelemetry(BaseTelemetry):
    """Telemetry backend that records every event into a list for assertions."""

    def __init__(self) -> None:
        self.agent: list[AgentEvent] = []
        self.fetch: list[FetchEvent] = []
        self.error: list[ErrorEvent] = []
        self.tool: list[ToolEvent] = []
        self.action: list[AgentActionEvent] = []

    def record_agent(self, event):
        self.agent.append(event)

    def record_fetch(self, event):
        self.fetch.append(event)

    def record_error(self, event):
        self.error.append(event)

    def record_tool(self, event):
        self.tool.append(event)

    def record_agent_action(self, event):
        self.action.append(event)


def test_tool_events_recorded():
    tel = CollectingTelemetry()
    handler = TelemetryCallbackHandler(tel, agent_id="reader-1")
    run_id = uuid4()

    handler.on_tool_start({"name": "search_memory"}, "q", run_id=run_id, inputs={"query": "x"})
    handler.on_tool_end("result", run_id=run_id)

    assert len(tel.tool) == 1
    event = tel.tool[0]
    assert event.tool == "search_memory"
    assert event.args == {"query": "x"}
    assert event.success is True
    assert event.agent_id == "reader-1"


def test_tool_error_recorded():
    tel = CollectingTelemetry()
    handler = TelemetryCallbackHandler(tel)
    run_id = uuid4()

    handler.on_tool_start({"name": "boom"}, "", run_id=run_id)
    handler.on_tool_error(RuntimeError("nope"), run_id=run_id)

    assert tel.tool[0].success is False
    assert "nope" in (tel.tool[0].error or "")


def test_llm_events_recorded():
    tel = CollectingTelemetry()
    handler = TelemetryCallbackHandler(tel, agent_id="planner-1")
    run_id = uuid4()

    handler.on_llm_start({}, ["hello"], run_id=run_id)
    handler.on_llm_end(None, run_id=run_id)

    assert len(tel.agent) == 1
    assert tel.agent[0].action == "llm"
    assert tel.agent[0].success is True


def test_llm_error_recorded():
    tel = CollectingTelemetry()
    handler = TelemetryCallbackHandler(tel)
    run_id = uuid4()

    handler.on_llm_start({}, ["hi"], run_id=run_id)
    handler.on_llm_error(ValueError("bad"), run_id=run_id)

    assert len(tel.error) == 1
    assert "bad" in tel.error[0].error
