"""Tests for orchestration.models.base."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic

from orchestration.models.base import AgentConfig, build_chat_model


def test_agent_config_defaults():
    cfg = AgentConfig()
    assert cfg.model_name == "claude-haiku-4-5-20251001"
    assert cfg.temperature == 0.0
    assert cfg.max_tokens is None


def test_build_chat_model_uses_config(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-used")
    cfg = AgentConfig(temperature=0.2, max_tokens=256)
    model = build_chat_model(cfg)
    assert isinstance(model, ChatAnthropic)
    assert model.temperature == 0.2
