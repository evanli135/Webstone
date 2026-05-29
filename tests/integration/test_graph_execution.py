"""Integration tests for the research graph execution.

These tests invoke the full graph with a real LLM. They are skipped by
default in CI (no API key) and must be run with:
    pytest tests/integration -m integration

Set ANTHROPIC_API_KEY in your environment before running.

TODO: Add VCR cassette recording to replay LLM responses without live calls.
"""

from __future__ import annotations

import pytest

from webstone.core.state.base import ExecutionStatus, GraphState, ResearchQuery
from webstone.graphs.workflows.research import build_research_graph


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_graph_smoke() -> None:
    """Smoke test: run the full graph against a simple query.

    Verifies the graph completes without error and produces a final answer.
    Does NOT assert on the quality of the answer.
    """
    graph = build_research_graph()

    initial_state = {
        "query": ResearchQuery(
            query="What is the difference between transformer and LSTM architectures?",
            max_branches=2,
            max_depth=1,
        ),
        "status": ExecutionStatus.RUNNING,
        "messages": [],
        "branches": [],
        "errors": [],
        "metadata": {},
    }

    raw = await graph.ainvoke(initial_state)
    state = GraphState.model_validate(raw)

    assert state.status == ExecutionStatus.COMPLETED
    assert state.final_answer is not None
    assert len(state.final_answer) > 50  # some real content
    assert state.errors == []


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_graph_with_invalid_query() -> None:
    """Verify the graph handles edge cases gracefully.

    TODO: Add more edge cases as the system matures.
    """
    pytest.skip("Not yet implemented")
