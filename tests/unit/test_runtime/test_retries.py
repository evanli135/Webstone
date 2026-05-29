"""Unit tests for the retry executor."""

from __future__ import annotations

import pytest

from webstone.core.models.base import RetryPolicy
from webstone.runtime.retries.policy import RetryExecutor


@pytest.mark.asyncio
class TestRetryExecutor:
    async def test_success_on_first_attempt(self) -> None:
        executor = RetryExecutor(RetryPolicy(max_attempts=3))
        call_count = 0

        async def fn() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await executor.run(fn)
        assert result == "ok"
        assert call_count == 1

    async def test_retry_on_failure_then_success(self) -> None:
        executor = RetryExecutor(RetryPolicy(max_attempts=3, base_delay_seconds=0.01))
        call_count = 0

        async def fn() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("transient error")
            return "ok"

        result = await executor.run(fn)
        assert result == "ok"
        assert call_count == 3

    async def test_exhausts_retries_and_raises(self) -> None:
        executor = RetryExecutor(RetryPolicy(max_attempts=2, base_delay_seconds=0.01))

        async def always_fails() -> None:
            raise RuntimeError("permanent error")

        with pytest.raises(RuntimeError, match="permanent error"):
            await executor.run(always_fails)

    def test_delay_calculation(self) -> None:
        policy = RetryPolicy(
            max_attempts=5,
            base_delay_seconds=1.0,
            exponential_base=2.0,
            jitter=False,
            max_delay_seconds=60.0,
        )
        executor = RetryExecutor(policy)
        # Delay for attempt 1 = 1.0, attempt 2 = 2.0, attempt 3 = 4.0
        assert executor.policy.delay_for_attempt(1) == pytest.approx(1.0)
        assert executor.policy.delay_for_attempt(2) == pytest.approx(2.0)
        assert executor.policy.delay_for_attempt(3) == pytest.approx(4.0)
