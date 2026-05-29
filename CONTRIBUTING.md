# Contributing to Webstone

Thank you for your interest in contributing! This document covers the development workflow, conventions, and review process.

---

## Getting Started

1. Fork the repository and clone your fork.
2. Follow the [quickstart in README.md](./README.md#quickstart) to set up your environment.
3. Create a branch: `git checkout -b feat/your-feature-name`

---

## Development Workflow

```bash
make install            # Install all dependencies (includes dev extras)
make pre-commit-install # Install pre-commit hooks
make check              # lint + typecheck + tests (run before every PR)
```

---

## Code Conventions

- **Python 3.12+** — Use modern type annotations, `match` statements where appropriate.
- **Pydantic v2** — All data models must use Pydantic `BaseModel`. No raw dicts crossing module boundaries.
- **Protocols over ABCs** — Prefer `typing.Protocol` for structural interfaces; use `ABC` only for shared base behavior.
- **Async-first** — Public APIs in the execution layer must be `async`. Pure cognitive functions may be sync.
- **No magic** — Explicit imports, explicit configuration, explicit dependencies.
- **Comments explain WHY** — Not what. If a reader would understand the code without the comment, delete it.

---

## Module Boundaries

Strictly enforce the cognitive/execution separation described in [ARCHITECTURE.md](./ARCHITECTURE.md):

- `core/`, `agents/`, `graphs/`, `memory/` — **Cognitive layer.** No imports from `runtime/`.
- `runtime/`, `services/`, `observability/` — **Execution layer.** May import from `core/` for state/event types only.

---

## Testing

- All new features require tests.
- Unit tests go in `tests/unit/`.
- Integration tests (requiring external services) go in `tests/integration/` and are skipped in CI unless `--integration` is passed.
- Use `pytest` fixtures from `tests/conftest.py`.
- Aim for deterministic tests — no sleep, no network calls in unit tests.

```bash
make test          # unit tests only
make test-cov      # with coverage report
```

---

## Pull Request Process

1. Run `make check` and ensure it passes cleanly.
2. Write a clear PR description explaining the motivation and approach.
3. For new features, update relevant docstrings and `ARCHITECTURE.md` if the design changes.
4. Request review from at least one maintainer.
5. PRs are squash-merged onto `main`.

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(agents): add evaluator critic loop
fix(runtime): correct retry backoff calculation
docs(architecture): clarify go runtime integration plan
chore(deps): bump langgraph to 0.2.x
```

---

## Reporting Issues

Use GitHub Issues. For security vulnerabilities, see [SECURITY.md](./SECURITY.md).
