"""WebSocket endpoint for streaming graph execution events.

Clients connect to ws://host/ws/runs/{run_id}/events and receive a stream
of JSON-serialized DomainEvent objects in real time as the graph executes.

This enables live dashboards, CLI progress displays, and IDE integrations.

Protocol:
  - Client connects
  - Server streams events: {"event_type": "...", "data": {...}, ...}
  - Server sends {"event_type": "graph.completed"} and closes when done

TODO: Add authentication (e.g., token in query param).
TODO: Handle reconnection with event replay from the event log.
TODO: Implement fan-out for multiple concurrent clients per run.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(tags=["streaming"])


@router.websocket("/ws/runs/{run_id}/events")
async def stream_run_events(websocket: WebSocket, run_id: str) -> None:
    """Stream domain events for a research run over WebSocket.

    Args:
        run_id: The research run ID to stream events for.
    """
    await websocket.accept()
    logger.info("WebSocket: client connected for run=%s", run_id)

    try:
        # TODO: Subscribe to the event bus for this run_id:
        #   event_bus = get_event_bus()
        #   async for event in event_bus.subscribe(f"run.{run_id}"):
        #       await websocket.send_text(json.dumps(event.model_dump_json_safe()))
        #       if event.event_type == EventType.GRAPH_COMPLETED:
        #           break

        # Placeholder: send a single stub message and close
        await websocket.send_text(
            json.dumps({
                "event_type": "stream.connected",
                "run_id": run_id,
                "message": "WebSocket streaming not yet implemented. Check back in v0.2.",
            })
        )
        # Keep connection open until client disconnects
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        logger.info("WebSocket: client disconnected for run=%s", run_id)
    except Exception as exc:
        logger.error("WebSocket: error for run=%s: %s", run_id, exc)
        await websocket.close(code=1011, reason="Internal server error")
