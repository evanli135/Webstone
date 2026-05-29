# Architecture

This document describes the architectural decisions, layer boundaries, and scaling strategy for webstone.

---

## Core Design Principle: Cognitive / Execution Separation

Webstone enforces a hard boundary between two concerns:

### Cognitive Layer

Everything that reasons, plans, retrieves, and evaluates lives here. This layer has no knowledge of how work is scheduled or parallelized — it only defines *what* to do.

- **Agents** (`src/webstone/agents/`) — Specialized reasoning units (Planner, Reader, Evaluator, Router). Each agent is a pure function over typed state.
- **Graphs** (`src/webstone/graphs/`) — LangGraph workflow definitions, node protocols, edge routing logic.
- **Memory** (`src/webstone/memory/`) — Graph-structured and vector-backed knowledge stores with retrieval interfaces.
- **Core** (`src/webstone/core/`) — Shared state schemas, protocols, events, errors. No business logic.

### Execution Layer

Everything that schedules, parallelizes, persists, and recovers lives here. This layer has no knowledge of agent reasoning — it only defines *how* to run work.

- **Runtime** (`src/webstone/runtime/`) — Task scheduler, distributed worker pool, queue abstraction, cancellation tokens, retry policies, checkpoint persistence.
- **Observability** (`src/webstone/observability/`) — Structured event bus, tracing, metrics.
- **Services** (`src/webstone/services/`) — FastAPI HTTP/WebSocket entrypoints, telemetry service.

---

## Graph Execution Model

Webstone uses LangGraph as its graph execution backbone.

A research run is modeled as a directed acyclic graph (DAG) of agent nodes:

```
                    ┌─────────┐
                    │ Planner │
                    └────┬────┘
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
      ┌────────┐   ┌──────────┐  ┌──────────┐
      │ Reader │   │  Reader  │  │  Reader  │
      └────┬───┘   └────┬─────┘  └────┬─────┘
           └─────────────┼─────────────┘
                         ▼
                   ┌───────────┐
                   │ Evaluator │
                   └─────┬─────┘
                         ▼
                   ┌───────────┐
                   │  Router   │  ── branch/terminate/recurse
                   └───────────┘
```

Each node is a pure async function over `GraphState`. Edges encode conditional routing logic. The Evaluator can trigger recursive sub-graphs for deeper exploration.

Key design decisions:
- **Shared state schema** — all nodes read/write a single `GraphState` Pydantic model.
- **Immutable state transitions** — nodes return updated state copies rather than mutating in place.
- **Branch tokens** — each parallel branch carries a `BranchContext` with a unique ID and parent lineage.

---

## Memory System

The memory layer uses a two-tier approach:

### Graph Store (structural memory)

Nodes and edges represent entities and relationships discovered during research. Implemented as an in-process adjacency store with a protocol interface for swapping in Neo4j, Kuzu, or similar.

```
Entity(id="anthropic", type="organization")
  ──[founded_by]──> Entity(id="dario_amodei", type="person")
  ──[publishes]───> Entity(id="claude", type="model")
```

### Vector Store (semantic memory)

Chunks of retrieved text indexed by embedding for semantic similarity search. Protocol interface for swapping in Qdrant, Pinecone, ChromaDB, etc.

### Retrieval Layer

Agents query memory through a unified `MemoryRetriever` protocol that combines graph traversal and vector search into a single ranked result list.

---

## Runtime Scaling Strategy

### Current State (v0.x)

- Single-process, async Python
- `asyncio`-based concurrency via `asyncio.gather`
- In-memory queues and checkpoints
- LangGraph as the primary orchestration engine

### Near-term (v0.3)

- Replace in-memory queues with Redis Streams
- Checkpoint persistence to PostgreSQL
- Horizontal worker scaling via Python multiprocessing

### Future (v1.x): Go Runtime Integration

The execution layer (scheduler, worker pool, queue, retries) is designed to be replaceable. The Python cognitive layer communicates with the execution layer via a well-defined event/message protocol.

The planned Go runtime will:
1. Own all scheduling, worker lifecycle, and queue management
2. Communicate with Python cognitive workers via gRPC or message queue
3. Provide dramatically higher throughput for fan-out graph search

The `src/webstone/runtime/` module exposes Protocol interfaces that will be backed by gRPC stubs in the future without changes to any cognitive-layer code.

---

## Observability Architecture

All observability is structured and OpenTelemetry-compatible:

- **Traces** — Every agent invocation, graph node execution, and memory query creates a span.
- **Metrics** — Counters and histograms for throughput, latency, error rates.
- **Events** — Structured domain events (AgentStarted, NodeCompleted, BranchPruned, etc.) emitted to the event bus and consumable via WebSocket.

The `ObservabilityCollector` protocol allows swapping in different backends (Jaeger, Prometheus, Datadog) without touching business logic.

---

## Configuration

All runtime configuration is managed through `src/webstone/config/settings.py` via Pydantic Settings v2. Settings are loaded from:

1. `.env` file (development)
2. Environment variables (production/CI)
3. Secret manager integration (future)

Feature flags follow the same pattern and allow toggling experimental runtime paths at startup.
