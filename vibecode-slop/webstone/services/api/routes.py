"""API route definitions.

Endpoints:
  GET  /health              — Liveness probe
  POST /runs                — Submit a new research run
  GET  /runs/{run_id}       — Get run status and result
  DELETE /runs/{run_id}     — Cancel a running job

All request/response bodies are typed Pydantic models.

TODO: Add authentication middleware (API key or JWT).
TODO: Add pagination to list endpoints.
TODO: Wire up the real scheduler (currently returns stubs).
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from webstone.core.state.base import ExecutionStatus, ResearchQuery
from webstone.core.models.base import ExecutionConfig, RunResult

router = APIRouter(tags=["research"])


# ── Request / Response models ─────────────────────────────────────────────────

class RunRequest(BaseModel):
    """Request body for starting a research run."""

    query: str = Field(..., min_length=10, description="The research question")
    max_branches: int = Field(default=8, ge=1, le=256)
    max_depth: int = Field(default=3, ge=1, le=10)
    config: ExecutionConfig | None = None


class RunResponse(BaseModel):
    """Response after submitting a research run."""

    run_id: str
    status: ExecutionStatus
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness probe. Always returns 200 if the process is running."""
    from webstone.config import get_settings
    settings = get_settings()
    return HealthResponse(status="ok", version="0.1.0", environment=settings.env)


@router.post("/runs", response_model=RunResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_run(request: RunRequest) -> RunResponse:
    """Submit a new research run.

    The run is queued and processed asynchronously. Poll GET /runs/{run_id}
    for status and results.

    TODO: Inject the scheduler via FastAPI dependency injection.
    TODO: Validate that the API key is set before accepting requests.
    """
    run_id = str(uuid.uuid4())

    # TODO: Build ExecutionConfig from request, submit to scheduler
    # scheduler = get_scheduler()
    # job_id = await scheduler.submit(graph, initial_state)

    return RunResponse(
        run_id=run_id,
        status=ExecutionStatus.PENDING,
        message="Research run submitted. Poll GET /runs/{run_id} for results.",
    )


@router.get("/runs/{run_id}", response_model=RunResult)
async def get_run(run_id: str) -> RunResult:
    """Get the status and result of a research run.

    TODO: Query the scheduler for job status and the checkpoint store for state.
    """
    # TODO: scheduler.status(run_id), checkpoint_store.load(run_id)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Run {run_id} not found")


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_run(run_id: str) -> None:
    """Cancel a running or pending research job.

    TODO: scheduler.cancel(run_id)
    """
    # TODO: check if run exists first, return 404 if not found
    pass
