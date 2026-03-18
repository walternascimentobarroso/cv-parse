"""Smoke tests for the production FastAPI app defined in src.main."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app


def test_main_app_health_endpoint() -> None:
    """Ensure the main app wiring and lifespan work without a real MongoDB for /health."""
    with TestClient(app) as client:
        response = client.get("/health")
        if response.status_code != 200:
            raise AssertionError(f"Expected status 200, got {response.status_code}")
        body = response.json()
        if body.get("status") != "ok":
            raise AssertionError(f"Expected status 'ok', got {body.get('status')!r}")
