"""Tests for orchestration.context.base.BaseContext."""

from __future__ import annotations

from orchestration.context.base import BaseContext


class DictContext(BaseContext):
    """Minimal concrete BaseContext backed by instance attributes."""

    def get(self, key: str):
        return getattr(self, key, None)

    def set(self, key: str, value) -> None:
        setattr(self, key, value)


def test_kwargs_become_attributes():
    ctx = DictContext(model="claude", depth=2)
    assert ctx.get("model") == "claude"
    assert ctx.get("depth") == 2


def test_set_and_get_roundtrip():
    ctx = DictContext()
    assert ctx.get("missing") is None
    ctx.set("missing", 42)
    assert ctx.get("missing") == 42
