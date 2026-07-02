"""Tests for orchestration.agents.base."""

from __future__ import annotations

import pytest

from orchestration.agents.base import Agent, BaseAgent, Observable, ObservableType
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


def test_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Agent()  # type: ignore[abstract]


def test_base_agent_cannot_be_instantiated_without_act():
    # BaseAgent leaves `act` abstract, so it is not directly constructible.
    with pytest.raises(TypeError):
        BaseAgent("planner", DictContext())  # type: ignore[abstract]


def test_concrete_agent_construction():
    ctx = DictContext()
    agent = DummyAgent("planner", ctx)
    assert agent.name == "planner"
    assert agent.context is ctx
    assert agent.act("obs") == "obs"


def test_fork_returns_same_type_with_inherited_config():
    ctx = DictContext()
    agent = DummyAgent("planner", ctx)

    same = agent.fork()
    assert isinstance(same, DummyAgent)
    assert same is not agent
    assert same.name == "planner"
    assert same.context is ctx


def test_fork_overrides_name_and_context():
    agent = DummyAgent("planner", DictContext())
    new_ctx = DictContext()

    forked = agent.fork(name="reader", context=new_ctx)
    assert forked.name == "reader"
    assert forked.context is new_ctx


def test_injected_model_is_used_without_building():
    sentinel = object()
    agent = DummyAgent("planner", DictContext(), model=sentinel)  # type: ignore[arg-type]
    # `.model` returns the injected instance and never calls build_chat_model.
    assert agent.model is sentinel


def test_fork_propagates_config_and_model():
    sentinel = object()
    agent = DummyAgent("planner", DictContext(), model=sentinel)  # type: ignore[arg-type]

    forked = agent.fork()
    assert forked.model is sentinel
    assert forked.config is agent.config
