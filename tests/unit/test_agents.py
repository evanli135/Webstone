"""Tests for orchestration.agents.base."""

from __future__ import annotations

import pytest

from orchestration.agents.base import BaseAgent, Observable, ObservableType
from orchestration.context.base import BaseContext


class DictContext(BaseContext):
    def get(self, key: str):
        return getattr(self, key, None)

    def set(self, key: str, value) -> None:
        setattr(self, key, value)


class DummyAgent(BaseAgent):
    def act(self, observation):
        return observation


class Unstringable:
    def __str__(self) -> str:
        raise RuntimeError("cannot stringify")


def test_observable_type_members_are_distinct():
    members = {
        ObservableType.PROMPT,
        ObservableType.COMMAND,
        ObservableType.UPDATE,
        ObservableType.COMPLETION,
    }
    assert len(members) == 4


def test_observable_accepts_stringable_data():
    obs = Observable(ObservableType.PROMPT, {"a": 1})
    assert obs.observable_type is ObservableType.PROMPT
    assert obs.data == {"a": 1}


def test_observable_rejects_unstringable_data():
    with pytest.raises(ValueError, match="stringable"):
        Observable(ObservableType.UPDATE, Unstringable())


def test_base_agent_init_is_not_implemented():
    with pytest.raises(NotImplementedError):
        DummyAgent("planner", DictContext())


def test_fork_is_not_implemented():
    # __init__ intentionally raises, so build an instance without calling it.
    agent = DummyAgent.__new__(DummyAgent)
    agent.name = "planner"
    agent.context = DictContext()
    with pytest.raises(NotImplementedError):
        agent.fork()
