FROM python:3.12-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency specs first for layer caching
COPY pyproject.toml .
COPY README.md .

# Install production dependencies only
RUN uv sync --no-dev --no-editable

# Copy application source
COPY src/ src/

# Non-root user for security
RUN useradd -m -u 1000 whetstone && chown -R whetstone:whetstone /app
USER whetstone

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "whetstone.services.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
