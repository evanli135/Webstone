"""Unit tests for cancellation tokens."""

from __future__ import annotations

import asyncio

import pytest

from webstone.runtime.cancellation.tokens import CancellationTokenSource


class TestCancellationToken:
    def test_not_cancelled_by_default(self) -> None:
        source = CancellationTokenSource()
        token = source.token
        assert not token.is_cancelled
        assert not source.is_cancelled

    def test_cancel_signals_token(self) -> None:
        source = CancellationTokenSource()
        token = source.token
        source.cancel()
        assert token.is_cancelled
        assert source.is_cancelled

    def test_raise_if_cancelled(self) -> None:
        source = CancellationTokenSource()
        token = source.token
        source.cancel()
        with pytest.raises(asyncio.CancelledError):
            token.raise_if_cancelled()

    def test_multiple_tokens_from_same_source(self) -> None:
        source = CancellationTokenSource()
        t1 = source.token
        t2 = source.token
        source.cancel()
        assert t1.is_cancelled
        assert t2.is_cancelled
