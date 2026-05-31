# Webstone

> A production-grade agentic research runtime for large-scale multi-agent orchestration, recursive planning trees, and distributed execution.

[![CI](https://github.com/evanli135/Webstone/actions/workflows/ci.yml/badge.svg)](https://github.com/evanli135/Webstone/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## What is Webstone?

Webstone is an open-source agentic research runtime designed for:

- **Multi-agent orchestration** — Coordinate hundreds of specialized agents (planners, readers, evaluators) over a shared graph.
- **Recursive search trees** — Branch, explore, prune, and merge reasoning paths at scale.
- **Graph-based memory** — Persist and query structured knowledge across agent runs.
- **High-concurrency execution** — Async-first runtime designed for thousands of parallel branches.
- **Streaming observability** — Real-time event streaming, tracing, and metrics via OpenTelemetry.
- **Durable execution** — Checkpoint and resume long-running research workflows.

---

## Architecture Overview

Webstone separates cognition from execution:

```
┌──────────────────────────────────────────────────┐
│                  Cognitive Layer                  │
│  Agents · Planners · Evaluators · Memory · Graphs │
└──────────────────────┬───────────────────────────┘
                       │  typed state / events
┌──────────────────────▼───────────────────────────┐
│                  Execution Layer                  │
│  Scheduler · Workers · Queues · Retries · Checks  │
└──────────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full design document.

---

## Repository Structure

```
webstone/
├── src/webstone/
│   ├── core/          # State schemas, protocols, events, errors
│   ├── agents/        # Planner, Reader, Evaluator, Router agents
│   ├── graphs/        # LangGraph builders, nodes, edges, workflows
│   ├── runtime/       # Scheduler, workers, queues, retries, checkpoints
│   ├── memory/        # Graph store, vector store, retrieval abstractions
│   ├── services/      # FastAPI, WebSocket, telemetry service
│   ├── observability/ # Tracing, metrics, event bus
│   └── config/        # Settings, environment, feature flags
├── tests/
│   ├── unit/
│   └── integration/
├── docker/
└── .github/workflows/
```

---

## Quickstart

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (optional, for local services)

### Setup

```bash
# Clone the repository
git clone https://github.com/evanli135/Webstone.git
cd Webstone

# Install uv if you haven't
pip install uv

# Create virtual environment and install dependencies
make install

# Copy environment config
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY

# Run pre-commit hooks
make pre-commit-install

# Verify setup
make check
```

### Run the API server

```bash
make serve
```

### Run the example research graph

```bash
uv run python -m webstone.graphs.workflows.research
```

---

## Development

```bash
make lint          # Run Ruff linter
make typecheck     # Run Pyright type checker
make test          # Run pytest suite
make test-cov      # Run tests with coverage
make check         # lint + typecheck + test
make fmt           # Auto-format with Ruff
```

See the [Makefile](./Makefile) for all available commands.

---

## Roadmap

See [ROADMAP.md](./ROADMAP.md) for the detailed roadmap.

High-level milestones:

| Phase | Focus |
|-------|-------|
| v0.1 | Core scaffolding, graph execution, basic agents |
| v0.2 | Graph memory, retrieval, evaluator feedback loops |
| v0.3 | Distributed runtime, checkpoint persistence |
| v0.4 | Go execution sidecar integration |
| v1.0 | Production-hardened runtime |

---

## Design Philosophy

1. **Separation of concerns** — Cognitive logic and execution mechanics never bleed into each other.
2. **Typed interfaces** — All agent contracts, state schemas, and events are strongly typed via Pydantic v2.
3. **Async-first** — The entire execution layer is designed for high-concurrency async workflows.
4. **Composable** — Small, focused modules that compose cleanly; no monolithic god classes.
5. **Observable by default** — Every meaningful operation emits structured events and spans.
6. **Escape hatches** — Protocol-based interfaces everywhere to avoid framework lock-in.

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](./LICENSE).
