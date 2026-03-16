#!/bin/sh
set -e
cd /app
uv sync

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

if [ -n "${DEBUGPY:-}" ]; then
  exec python -m debugpy --listen 0.0.0.0:5678 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
fi

exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
