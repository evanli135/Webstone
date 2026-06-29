"""Retry policy and executor.

Provides a composable retry decorator and an imperative RetryExecutor for
wrapping async callables with configurable backoff.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import random
from typing import Any, Callable, TypeVar

from webstone.core.models.base import RetryPolicy

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class RetryExecutor:
    """Executes an async callable with retry semantics defined by RetryPolicy."""

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self.policy = policy or RetryPolicy()

    async def run(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute fn with retries on exception.

        Args:
            fn: Async callable to execute.
            *args, **kwargs: Arguments forwarded to fn.

        Returns:
            The return value of fn on success.

        Raises:
            The last exception if all attempts fail.
        """
        last_exc: Exception | None = None

        for attempt in range(1, self.policy.max_attempts + 1):
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if attempt == self.policy.max_attempts:
                    break

                delay = self.policy.delay_for_attempt(attempt)
                if self.policy.jitter:
                    delay *= (0.5 + random.random())  # jitter ±50%

                logger.warning(
                    "RetryExecutor: attempt %d/%d failed for %s, retrying in %.1fs: %s",
                    attempt,
                    self.policy.max_attempts,
                    fn.__name__,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)

        raise last_exc  # type: ignore[misc]


def with_retry(policy: RetryPolicy | None = None) -> Callable[[F], F]:
    """Decorator that wraps an async function with retry logic.

    Usage:
        @with_retry(RetryPolicy(max_attempts=3))
        async def my_function():
            ...
    """
    executor = RetryExecutor(policy)

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await executor.run(fn, *args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
