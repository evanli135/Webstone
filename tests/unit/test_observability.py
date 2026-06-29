"""Tests for orchestration.observability event types and console telemetry."""

from __future__ import annotations

from datetime import datetime

from orchestration.observability.base import (
    AgentActionEvent,
    AgentEvent,
    ErrorEvent,
    FetchEvent,
    ToolEvent,
)
from orchestration.observability.console import ConsoleTelemetry


def test_fetch_event_defaults():
    event = FetchEvent(
        source="arxiv",
        query="transformers",
        duration_ms=12.0,
        result_count=3,
        success=True,
    )
    assert event.error is None
    assert isinstance(event.timestamp, datetime)


def test_console_records_fetch(capsys):
    ConsoleTelemetry().record_fetch(
        FetchEvent(
            source="arxiv",
            query="transformers",
            duration_ms=12.0,
            result_count=3,
            success=True,
        )
    )
    out = capsys.readouterr().out
    assert "arxiv" in out
    assert "3 results" in out
    assert "[OK]" in out


def test_console_records_failed_fetch(capsys):
    ConsoleTelemetry().record_fetch(
        FetchEvent(
            source="arxiv",
            query="transformers",
            duration_ms=12.0,
            result_count=0,
            success=False,
            error="timeout",
        )
    )
    assert "[FAIL]" in capsys.readouterr().out


def test_console_records_all_event_kinds(capsys):
    telemetry = ConsoleTelemetry()
    telemetry.record_agent(
        AgentEvent(agent_id="planner-1", action="plan", duration_ms=5.0, success=True)
    )
    telemetry.record_error(ErrorEvent(agent_id="reader-1", error="boom"))
    telemetry.record_tool(
        ToolEvent(
            agent_id="reader-1",
            tool="search_memory",
            args={"q": "x"},
            duration_ms=2.0,
            success=True,
        )
    )
    telemetry.record_agent_action(
        AgentActionEvent(
            source_agent_id="planner-1",
            target_agent_id="reader-1",
            action="delegate",
            result="reader-3",
        )
    )
    out = capsys.readouterr().out
    assert "planner-1" in out
    assert "boom" in out
    assert "search_memory" in out
    assert "delegate" in out
