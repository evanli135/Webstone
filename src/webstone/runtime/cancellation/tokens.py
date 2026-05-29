"""Cancellation token pattern for cooperative async cancellation.

Unlike asyncio.CancelledError (which is abrupt), cancellation tokens allow
code to check for cancellation at logical checkpoints and clean up gracefully.

This mirrors the CancellationToken pattern from .NET and Go's context.Context.
"""

from __future__ import annotations

import asyncio


class CancellationToken:
    """Read-only view of a cancellation signal.

    Workers and agents hold a CancellationToken. They check `is_cancelled`
    at safe points and raise or return early if True.

    Usage:
        async def my_agent(state, token: CancellationToken):
            for branch in branches:
                token.raise_if_cancelled()
                await process(branch)
    """

    def __init__(self, event: asyncio.Event) -> None:
        self._event = event

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def raise_if_cancelled(self) -> None:
        """Raise asyncio.CancelledError if cancellation has been requested."""
        if self.is_cancelled:
            raise asyncio.CancelledError("Operation cancelled via CancellationToken")

    async def wait_for_cancellation(self) -> None:
        """Async wait until cancellation is signalled."""
        await self._event.wait()


class CancellationTokenSource:
    """Controls the cancellation signal for a group of tokens.

    The source holds the write side; tokens hold the read side.
    Typically one source per job/run; tokens are passed to all workers.

    Usage:
        source = CancellationTokenSource()
        token = source.token
        # ... pass token to workers ...
        source.cancel()  # signals all tokens
    """

    def __init__(self) -> None:
        self._event = asyncio.Event()

    @property
    def token(self) -> CancellationToken:
        """Create a CancellationToken that listens to this source."""
        return CancellationToken(self._event)

    def cancel(self) -> None:
        """Signal cancellation to all tokens created from this source."""
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()
