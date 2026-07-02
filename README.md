# Webstone

> An agentic research assistant that fetches, stores, and reasons over academic papers.

[![CI](https://github.com/evanli135/Webstone/actions/workflows/ci.yml/badge.svg)](https://github.com/evanli135/Webstone/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is Webstone?

Webstone is a research tool that aggregates academic papers from multiple sources (arXiv, Semantic Scholar, Crossref), persists them to a Postgres database, and uses LangChain-powered agents to plan, retrieve, and evaluate research queries.

The system is split into two layers:

- **Transport** (Go) — high-concurrency paper fetching from external APIs, fanning out requests in parallel.
- **Cognitive** (Python) — LangChain agents that plan research, retrieve papers, and evaluate results, backed by SQLModel + Postgres.

---

## Architecture

```
┌──────────────────────────────────┐
│         Cognitive Layer (Python) │
│  LangChain agents · Pydantic     │
│  SQLModel models · Postgres      │
└────────────────┬─────────────────┘
                 │  HTTP (paper fetch requests)
┌────────────────▼─────────────────┐
│         Transport Layer (Go)     │
│  Concurrent source fetching      │
│  arXiv · Semantic Scholar        │
│  Crossref                        │
└──────────────────────────────────┘
```

The Go transport service exposes a single `/fetch` endpoint that fans out to all requested paper sources concurrently and returns a unified list of results. Python agents call this service and persist results to Postgres via SQLModel.

---

## Repository Structure

```
webstone/
├── src/
│   ├── transport/               # Go transport service
│   │   ├── cmd/main.go          # Entry point
│   │   └── internal/
│   │       ├── server/          # HTTP handlers, routing
│   │       ├── sources/         # arXiv, Semantic Scholar, Crossref clients
│   │       └── models/          # Shared request/response types
|   |
│   └── orchestration/           # Python Agentic Service
|  
├── tests/
├── docker/
└── .github/workflows/
```

---

## Tech Stack

| Layer | Language | Key Libraries |
|-------|----------|---------------|
| Cognitive | Python 3.12 | LangChain, Pydantic v2, SQLModel |
| Transport | Go 1.24 | stdlib `net/http` |
| Persistence | — | PostgreSQL |

---

## Quickstart

### Prerequisites

- Python 3.12+, [uv](https://github.com/astral-sh/uv)
- Go 1.24+
- PostgreSQL

### Python setup

```bash
git clone https://github.com/evanli135/Webstone.git
cd Webstone

pip install uv
make install

cp .env.example .env
# Set DATABASE_URL and ANTHROPIC_API_KEY in .env
```

### Run the Go transport service

```bash
cd src/transport
go run ./cmd
# Listening on :8080
```

### Fetch papers

```bash
curl -X POST http://localhost:8080/fetch \
  -H "Content-Type: application/json" \
  -d '{"query": "transformer attention mechanisms", "limit": 10}'
```

---

## Development

```bash
make lint        # Ruff linter
make typecheck   # Pyright
make test        # pytest
make fmt         # auto-format
```

For the Go service:
```bash
cd src/transport
go build ./...
go vet ./...
```

---

## Roadmap

| Phase | Focus |
|-------|-------|
| v0.1 | Go transport service, paper fetching from all sources |
| v0.2 | Python agents (planner, reader, evaluator) wired up |
| v0.3 | Postgres persistence via SQLModel |
| v0.4 | End-to-end research query pipeline |
| v1.0 | Production deployment |

---

## License

MIT — see [LICENSE](./LICENSE).
