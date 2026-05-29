# Roadmap

This document describes the planned development trajectory for webstone.

---

## v0.1 — Foundation (current)

- [x] Repository scaffold: architecture, CI, tooling
- [ ] Core state/event/protocol types
- [ ] Planner, Reader, Evaluator agent skeletons
- [ ] Basic LangGraph research workflow
- [ ] FastAPI health + execution endpoints
- [ ] In-process graph memory store
- [ ] Structured logging + tracing hooks

## v0.2 — Memory & Evaluation

- [ ] Graph store with node/edge CRUD and traversal queries
- [ ] Vector store abstraction with pluggable backend
- [ ] Unified retrieval layer (graph + vector fusion)
- [ ] Evaluator critic loop with configurable scoring
- [ ] Branch pruning based on evaluator scores
- [ ] WebSocket streaming of graph execution events
- [ ] Checkpoint persistence to SQLite (dev) / PostgreSQL (prod)

## v0.3 — Distributed Runtime

- [ ] Redis Streams queue backend
- [ ] Multi-process worker pool
- [ ] Distributed cancellation tokens
- [ ] Retry policy with exponential backoff and jitter
- [ ] Horizontal scaling documentation and Helm chart skeleton
- [ ] Prometheus metrics export

## v0.4 — Go Runtime Sidecar

- [ ] gRPC protocol definition for cognitive ↔ execution boundary
- [ ] Go scheduler and worker pool implementation
- [ ] Python gRPC client stubs for Go runtime
- [ ] Performance benchmarks vs pure Python runtime
- [ ] Feature parity tests

## v1.0 — Production Hardened

- [ ] Full observability integration (Jaeger, Prometheus, OpenTelemetry Collector)
- [ ] Multi-tenant execution isolation
- [ ] Rate limiting and quota management
- [ ] Audit logging
- [ ] Security hardening review
- [ ] Performance optimization pass
- [ ] Documentation site

---

## Ideas Under Consideration

- Plugin system for custom agent types
- Workflow versioning and migration
- Visual graph execution debugger
- WASM agent sandboxing
- Federated memory across deployments
