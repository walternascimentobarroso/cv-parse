"""Unit tests for logging configuration helpers."""

from __future__ import annotations

from src.infra.logging_config import configure_logging, get_logger


def test_configure_logging_and_get_logger() -> None:
    configure_logging()
    logger = get_logger("test-logger")
    if logger.name != "test-logger":
        msg = f"Expected logger name 'test-logger', got {logger.name!r}"
        raise AssertionError(msg)
    if not logger.hasHandlers():
        msg = "Expected logger to have at least one handler after configure_logging()"
        raise AssertionError(
            msg,
        )
