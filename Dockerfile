FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_CACHE_DIR=/app/.cache/uv

# nodejs: required so `uv run pyright` uses system Node (avoids nodeenv under HOME=/nonexistent)
RUN apt-get update && apt-get install -y --no-install-recommends curl nodejs \
    && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    chmod 755 /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:${PATH}"

# Application code is mounted at runtime via volume (see docker-compose.yml)
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create non-root user for running the application
RUN addgroup --system app && adduser --system --ingroup app app && \
    mkdir -p /app/.cache/uv && \
    chown -R app:app /app /docker-entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
