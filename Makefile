.PHONY: install dev-install pre-commit-install lint fmt typecheck test test-cov \
        check serve docker-up docker-down clean help

PYTHON := python
UV := uv
SRC := src/webstone
TESTS := tests

# ── Setup ──────────────────────────────────────────────────────────────────────

install:  ## Install all dependencies
	$(UV) sync --all-extras

dev-install: install  ## Install + pre-commit hooks
	$(UV) run pre-commit install

pre-commit-install:  ## Install pre-commit hooks only
	$(UV) run pre-commit install

# ── Code quality ───────────────────────────────────────────────────────────────

lint:  ## Run Ruff linter
	$(UV) run ruff check $(SRC) $(TESTS)

fmt:  ## Auto-format with Ruff
	$(UV) run ruff format $(SRC) $(TESTS)
	$(UV) run ruff check --fix $(SRC) $(TESTS)

typecheck:  ## Run Pyright type checker
	$(UV) run pyright $(SRC)

# ── Tests ──────────────────────────────────────────────────────────────────────

test:  ## Run unit tests
	$(UV) run pytest $(TESTS)/unit -v

test-integration:  ## Run integration tests (requires external services)
	$(UV) run pytest $(TESTS)/integration -v -m integration

test-cov:  ## Run tests with coverage report
	$(UV) run pytest $(TESTS)/unit --cov=$(SRC) --cov-report=term-missing --cov-report=html

# ── Composite ──────────────────────────────────────────────────────────────────

check: lint typecheck test  ## Run all checks (lint + typecheck + tests)

# ── Run ────────────────────────────────────────────────────────────────────────

serve:  ## Start the FastAPI development server
	$(UV) run uvicorn whetstone.services.api.app:app --host 0.0.0.0 --port 8000 --reload

# ── Docker ─────────────────────────────────────────────────────────────────────

docker-up:  ## Start local services (Redis, etc.)
	docker compose up -d

docker-down:  ## Stop local services
	docker compose down

docker-build:  ## Build production Docker image
	docker build -f docker/Dockerfile -t whetstone:latest .

docker-build-dev:  ## Build development Docker image
	docker build -f docker/Dockerfile.dev -t whetstone:dev .

# ── Utility ────────────────────────────────────────────────────────────────────

clean:  ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
