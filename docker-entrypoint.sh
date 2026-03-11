#!/bin/sh
set -e
cd /app
uv sync
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
