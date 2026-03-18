"""Unit tests for ExtractionRepository (find_by_id, find_all, update, soft_delete)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infra.storage import ExtractionRepository, create_motor_client


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
    col.delete_one = AsyncMock()
    return col


@pytest.fixture
def repo(mock_collection):
    return ExtractionRepository(mock_collection)


def test_save_extraction_sets_audit_fields(repo: ExtractionRepository, mock_collection) -> None:
    mock_collection.insert_one.return_value = MagicMock(inserted_id="507f1f77bcf86cd799439011")
    result = _run(
        repo.save_extraction(
            filename="test.pdf",
            content_type="application/pdf",
            size_bytes=100,
            extracted_text="text",
            status="success",
        )
    )
    if result != "507f1f77bcf86cd799439011":
        raise AssertionError(f"Expected inserted id, got {result!r}")
    call_args = mock_collection.insert_one.call_args[0][0]
    if "created_at" not in call_args:
        raise AssertionError("Expected created_at in inserted document")
    if call_args.get("updated_at") is None:
        raise AssertionError("Expected updated_at to be set on insert")
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


def test_update_returns_none_when_document_not_found(
    repo: ExtractionRepository,
    mock_collection,
) -> None:
    mock_collection.find_one_and_update.return_value = None
    result = _run(repo.update("507f1f77bcf86cd799439011", {"extracted_text": "x"}))
    if result is not None:
        raise AssertionError(f"Expected None when find_one_and_update returns None, got {result!r}")


def test_find_by_id_returns_document_when_found(
    repo: ExtractionRepository,
    mock_collection,
) -> None:
    mock_collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "test.pdf",
        "content_type": "application/pdf",
        "size_bytes": 100,
        "extracted_text": "text",
        "status": "success",
        "created_at": "now",
        "updated_at": None,
        "deleted_at": None,
    }
    result = _run(repo.find_by_id("507f1f77bcf86cd799439011"))
    if result is None:
        raise AssertionError("Expected a document to be returned")
    if result.get("id") != "507f1f77bcf86cd799439011":
        raise AssertionError(f"Expected id to be stringified _id, got {result.get('id')!r}")


def test_update_returns_document_when_found(repo: ExtractionRepository, mock_collection) -> None:
    mock_collection.find_one_and_update.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "test.pdf",
        "content_type": "application/pdf",
        "size_bytes": 100,
        "extracted_text": "updated",
        "status": "success",
        "created_at": "now",
        "updated_at": None,
        "deleted_at": None,
    }
    result = _run(repo.update("507f1f77bcf86cd799439011", {"extracted_text": "updated"}))
    if result is None:
        raise AssertionError("Expected updated document")
    if result.get("extracted_text") != "updated":
        raise AssertionError(f"Expected updated text, got {result.get('extracted_text')!r}")


def test_soft_delete_returns_true_when_document_updated(
    repo: ExtractionRepository,
    mock_collection,
) -> None:
    mock_collection.update_one.return_value = MagicMock(modified_count=1)
    result = _run(repo.soft_delete("507f1f77bcf86cd799439011"))
    if result is not True:
        raise AssertionError(f"Expected True for successful soft delete, got {result!r}")


def test_restore_returns_false_for_invalid_id(repo: ExtractionRepository) -> None:
    result = _run(repo.restore("bad-id"))
    if result != "not_found":
        raise AssertionError(f"Expected 'not_found' for invalid id, got {result!r}")


def test_restore_returns_not_deleted_when_active(
    repo: ExtractionRepository,
    mock_collection,
) -> None:
    mock_collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "deleted_at": None,
    }
    result = _run(repo.restore("507f1f77bcf86cd799439011"))
    if result != "not_deleted":
        raise AssertionError(
            f"Expected 'not_deleted' when record is not soft deleted, got {result!r}",
        )


def test_restore_returns_restored_when_document_updated(
    repo: ExtractionRepository,
    mock_collection,
) -> None:
    mock_collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "deleted_at": "some-timestamp",
    }
    mock_collection.update_one.return_value = MagicMock(modified_count=1)
    result = _run(repo.restore("507f1f77bcf86cd799439011"))
    if result != "restored":
        raise AssertionError(f"Expected 'restored' for successful restore, got {result!r}")


def test_restore_returns_not_found_when_document_missing_before_update(
    repo: ExtractionRepository,
    mock_collection,
) -> None:
    """If find_one returns None for a valid id, restore should return 'not_found'."""
    mock_collection.find_one.return_value = None
    result = _run(repo.restore("507f1f77bcf86cd799439011"))
    if result != "not_found":
        raise AssertionError(f"Expected 'not_found' when document is missing, got {result!r}")


def test_restore_returns_not_found_when_update_does_not_modify(
    repo: ExtractionRepository,
    mock_collection,
) -> None:
    """If update_one modifies no documents, restore should return 'not_found'."""
    mock_collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "deleted_at": "some-timestamp",
    }
    mock_collection.update_one.return_value = MagicMock(modified_count=0)
    result = _run(repo.restore("507f1f77bcf86cd799439011"))
    if result != "not_found":
        raise AssertionError(
            f"Expected 'not_found' when update_one.modified_count == 0, got {result!r}",
        )


def test_force_delete_returns_false_for_invalid_id(repo: ExtractionRepository) -> None:
    result = _run(repo.force_delete("bad-id"))
    if result is not False:
        raise AssertionError(f"Expected False for invalid id, got {result!r}")


def test_force_delete_returns_true_when_document_deleted(
    repo: ExtractionRepository,
    mock_collection,
) -> None:
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
    result = _run(repo.force_delete("507f1f77bcf86cd799439011"))
    if result is not True:
        raise AssertionError(f"Expected True for successful force delete, got {result!r}")


def test_create_motor_client_returns_client() -> None:
    client = create_motor_client("mongodb://localhost:27017")
    # Motor client connects lazily; just check type and close.
    module_name = type(client).__module__
    if "motor" not in module_name:
        raise AssertionError(f"Expected motor client, got module {module_name!r}")
    client.close()
