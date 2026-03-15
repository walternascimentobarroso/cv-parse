"""Unit tests for ExtractionRepository (find_by_id, find_all, update, soft_delete)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infra.storage import ExtractionRepository


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
def mock_collection():
    """AsyncIOMotorCollection double for testing without MongoDB."""
    col = MagicMock()
    col.insert_one = AsyncMock()
    col.find_one = AsyncMock()
    col.find = MagicMock()
    col.find_one_and_update = AsyncMock()
    col.update_one = AsyncMock()
    return col


@pytest.fixture
def repo(mock_collection):
    return ExtractionRepository(mock_collection)


def test_save_extraction_sets_audit_fields(repo: ExtractionRepository, mock_collection) -> None:
    mock_collection.insert_one.return_value = MagicMock(inserted_id="507f1f77bcf86cd799439011")
    result = _run(repo.save_extraction(
        filename="test.pdf",
        content_type="application/pdf",
        size_bytes=100,
        extracted_text="text",
        status="success",
    ))
    if result != "507f1f77bcf86cd799439011":
        raise AssertionError(f"Expected inserted id, got {result!r}")
    call_args = mock_collection.insert_one.call_args[0][0]
    if "created_at" not in call_args:
        raise AssertionError("Expected created_at in inserted document")
    if call_args.get("updated_at") is not None:
        raise AssertionError("Expected updated_at to be None on insert")
    if call_args.get("deleted_at") is not None:
        raise AssertionError("Expected deleted_at to be None on insert")


def test_find_by_id_returns_none_for_invalid_id(repo: ExtractionRepository) -> None:
    result = _run(repo.find_by_id("invalid"))
    if result is not None:
        raise AssertionError(f"Expected None for invalid id, got {result!r}")


def test_find_by_id_uses_active_filter(repo: ExtractionRepository, mock_collection) -> None:
    mock_collection.find_one.return_value = None
    _run(repo.find_by_id("507f1f77bcf86cd799439011"))
    query = mock_collection.find_one.call_args[0][0]
    if "deleted_at" not in query:
        raise AssertionError("Expected deleted_at in find_one query (active filter)")
    if query.get("deleted_at") is not None:
        raise AssertionError("Expected deleted_at: None in active filter")


def test_find_all_uses_active_filter(repo: ExtractionRepository, mock_collection) -> None:
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_collection.find.return_value = mock_cursor
    _run(repo.find_all())
    call_args = mock_collection.find.call_args[0]
    if not call_args:
        raise AssertionError("Expected find to be called with a filter")
    query = call_args[0]
    if query.get("deleted_at") is not None:
        raise AssertionError("Expected deleted_at: None in find filter")


def test_update_returns_none_for_invalid_id(repo: ExtractionRepository) -> None:
    result = _run(repo.update("bad-id", {"extracted_text": "x"}))
    if result is not None:
        raise AssertionError(f"Expected None for invalid id, got {result!r}")


def test_soft_delete_returns_false_for_invalid_id(repo: ExtractionRepository) -> None:
    result = _run(repo.soft_delete("bad-id"))
    if result is not False:
        raise AssertionError(f"Expected False for invalid id, got {result!r}")
