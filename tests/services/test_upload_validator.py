"""Unit tests for upload validator (no HTTP)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.upload_validator import ValidationError, ValidationOk, validate_upload


@pytest.fixture
def settings() -> SimpleNamespace:
    """Minimal settings object for validator (allowed_content_types, max_document_size_bytes)."""
    return SimpleNamespace(
        allowed_content_types=["application/pdf", "text/plain"],
        max_document_size_bytes=100,
    )


def test_validate_upload_missing_file(settings: SimpleNamespace) -> None:
    result = asyncio.run(validate_upload(None, settings))
    if not isinstance(result, ValidationError):
        raise AssertionError(f"Expected ValidationError, got {type(result)}")
    if result.status_code != 400:
        raise AssertionError(f"Expected 400, got {result.status_code}")
    if "required" not in result.detail.lower():
        raise AssertionError(f"Expected 'required' in detail: {result.detail}")


def test_validate_upload_unsupported_type(settings: SimpleNamespace) -> None:
    file = MagicMock(spec=["read", "content_type", "filename"])
    file.content_type = "image/jpeg"
    file.filename = "x.jpg"
    file.read = AsyncMock(return_value=b"")
    result = asyncio.run(validate_upload(file, settings))
    if not isinstance(result, ValidationError):
        raise AssertionError(f"Expected ValidationError, got {type(result)}")
    if result.status_code != 400:
        raise AssertionError(f"Expected 400, got {result.status_code}")
    if "Unsupported" not in result.detail:
        raise AssertionError(f"Expected 'Unsupported' in detail: {result.detail}")


def test_validate_upload_size_exceeded(settings: SimpleNamespace) -> None:
    file = MagicMock(spec=["read", "content_type", "filename"])
    file.content_type = "text/plain"
    file.filename = "big.txt"
    file.read = AsyncMock(side_effect=[b"x" * 50, b"x" * 60])  # 110 bytes > 100
    result = asyncio.run(validate_upload(file, settings))
    if not isinstance(result, ValidationError):
        raise AssertionError(f"Expected ValidationError, got {type(result)}")
    if result.status_code != 413:
        raise AssertionError(f"Expected 413, got {result.status_code}")


def test_validate_upload_ok_plain_text(settings: SimpleNamespace) -> None:
    file = MagicMock(spec=["read", "content_type", "filename"])
    file.content_type = "text/plain"
    file.filename = "t.txt"
    file.read = AsyncMock(side_effect=[b"hello", b""])  # first chunk then EOF
    result = asyncio.run(validate_upload(file, settings))
    if not isinstance(result, ValidationOk):
        raise AssertionError(f"Expected ValidationOk, got {type(result)}")
    if result.content != b"hello":
        raise AssertionError(f"Expected b'hello', got {result.content}")
    if result.size_bytes != 5:
        raise AssertionError(f"Expected size 5, got {result.size_bytes}")
    if result.content_type != "text/plain":
        raise AssertionError(f"Expected text/plain, got {result.content_type}")
