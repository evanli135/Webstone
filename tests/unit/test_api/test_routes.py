"""Unit tests for FastAPI routes (no LLM calls, no external services)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from webstone.services.api.app import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_body(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body
        assert "environment" in body


class TestRunEndpoints:
    def test_create_run_accepts(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/runs",
            json={"query": "What are the main theories of consciousness?"},
        )
        assert response.status_code == 202
        body = response.json()
        assert "run_id" in body
        assert body["status"] == "pending"

    def test_create_run_too_short_query(self, client: TestClient) -> None:
        response = client.post("/api/v1/runs", json={"query": "short"})
        assert response.status_code == 422  # validation error

    def test_get_run_not_found(self, client: TestClient) -> None:
        response = client.get("/api/v1/runs/nonexistent-run-id")
        assert response.status_code == 404
