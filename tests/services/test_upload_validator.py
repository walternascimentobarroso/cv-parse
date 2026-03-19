"""Unit tests for upload validator (no HTTP)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.upload_validator import (
    UploadValidationSettings,
    ValidationError,
    ValidationOk,
    validate_upload,
)


@dataclass(frozen=True)
class _TestSettings:
    allowed_content_types: list[str]
    max_document_size_bytes: int


@pytest.fixture
def settings() -> UploadValidationSettings:
    """Minimal settings object for validator (allowed_content_types, max_document_size_bytes)."""
    return _TestSettings(
        allowed_content_types=["application/pdf", "text/plain"],
        max_document_size_bytes=100,
    )


def test_validate_upload_missing_file(settings: UploadValidationSettings) -> None:
    result = asyncio.run(validate_upload(None, settings))
    if not isinstance(result, ValidationError):
        msg = f"Expected ValidationError, got {type(result)}"
        raise AssertionError(msg)
    if result.status_code != 400:
        msg = f"Expected 400, got {result.status_code}"
        raise AssertionError(msg)
    if "required" not in result.detail.lower():
        msg = f"Expected 'required' in detail: {result.detail}"
        raise AssertionError(msg)


def test_validate_upload_unsupported_type(settings: UploadValidationSettings) -> None:
    file = MagicMock(spec=["read", "content_type", "filename"])
    file.content_type = "image/jpeg"
    file.filename = "x.jpg"
    file.read = AsyncMock(return_value=b"")
    result = asyncio.run(validate_upload(file, settings))
    if not isinstance(result, ValidationError):
        msg = f"Expected ValidationError, got {type(result)}"
        raise AssertionError(msg)
    if result.status_code != 400:
        msg = f"Expected 400, got {result.status_code}"
        raise AssertionError(msg)
    if "Unsupported" not in result.detail:
        msg = f"Expected 'Unsupported' in detail: {result.detail}"
        raise AssertionError(msg)


def test_validate_upload_size_exceeded(settings: UploadValidationSettings) -> None:
    file = MagicMock(spec=["read", "content_type", "filename"])
    file.content_type = "text/plain"
    file.filename = "big.txt"
    file.read = AsyncMock(side_effect=[b"x" * 50, b"x" * 60])  # 110 bytes > 100
    result = asyncio.run(validate_upload(file, settings))
    if not isinstance(result, ValidationError):
        msg = f"Expected ValidationError, got {type(result)}"
        raise AssertionError(msg)
    if result.status_code != 413:
        msg = f"Expected 413, got {result.status_code}"
        raise AssertionError(msg)


def test_validate_upload_ok_plain_text(settings: UploadValidationSettings) -> None:
    file = MagicMock(spec=["read", "content_type", "filename"])
    file.content_type = "text/plain"
    file.filename = "t.txt"
    file.read = AsyncMock(side_effect=[b"hello", b""])  # first chunk then EOF
    result = asyncio.run(validate_upload(file, settings))
    if not isinstance(result, ValidationOk):
        msg = f"Expected ValidationOk, got {type(result)}"
        raise AssertionError(msg)
    if result.content != b"hello":
        msg = f"Expected b'hello', got {result.content}"
        raise AssertionError(msg)
    if result.size_bytes != 5:
        msg = f"Expected size 5, got {result.size_bytes}"
        raise AssertionError(msg)
    if result.content_type != "text/plain":
        msg = f"Expected text/plain, got {result.content_type}"
        raise AssertionError(msg)
