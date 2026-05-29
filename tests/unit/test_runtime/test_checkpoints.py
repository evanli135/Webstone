"""Unit tests for checkpoint store."""

from __future__ import annotations

import pytest

from webstone.core.state.base import ExecutionStatus, GraphState


@pytest.mark.asyncio
class TestInMemoryCheckpointStore:
    async def test_save_and_load(self, checkpoint_store, empty_state) -> None:
        await checkpoint_store.save(empty_state.run_id, empty_state)
        loaded = await checkpoint_store.load(empty_state.run_id)
        assert loaded is not None
        assert loaded.run_id == empty_state.run_id

    async def test_load_missing_returns_none(self, checkpoint_store) -> None:
        result = await checkpoint_store.load("nonexistent-run-id")
        assert result is None

    async def test_delete(self, checkpoint_store, empty_state) -> None:
        await checkpoint_store.save(empty_state.run_id, empty_state)
        await checkpoint_store.delete(empty_state.run_id)
        result = await checkpoint_store.load(empty_state.run_id)
        assert result is None

    async def test_returns_deep_copy(self, checkpoint_store, empty_state) -> None:
        await checkpoint_store.save(empty_state.run_id, empty_state)
        loaded = await checkpoint_store.load(empty_state.run_id)
        # Mutating the loaded state should not affect the stored one
        assert loaded is not empty_state
