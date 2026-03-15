from __future__ import annotations

from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import ReturnDocument

from src.infra.schemas import ExtractionRecord

# Filter for documents that are not soft-deleted. Use in all reads and in update/soft_delete.
ACTIVE_FILTER: dict = {"deleted_at": None}


def _doc_to_record(doc: dict) -> dict:
    """Convert MongoDB document (with _id) to API-shaped dict with string id."""
    out = dict(doc)
    out["id"] = str(out.pop("_id", ""))
    return out


class ExtractionRepository:
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    async def save_extraction(
        self,
        *,
        filename: str | None,
        content_type: str,
        size_bytes: int,
        extracted_text: str,
        status: str = "success",
    ) -> str:
        record = ExtractionRecord(
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            extracted_text=extracted_text,
            status=status,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        result = await self._collection.insert_one(record.to_mongo())
        return str(result.inserted_id)

    async def find_by_id(self, extraction_id: str) -> dict | None:
        try:
            oid = ObjectId(extraction_id)
        except (InvalidId, TypeError):
            return None
        query = {"_id": oid, **ACTIVE_FILTER}
        doc = await self._collection.find_one(query)
        if doc is None:
            return None
        return _doc_to_record(doc)

    async def find_all(self) -> list[dict]:
        cursor = self._collection.find(ACTIVE_FILTER)
        docs = await cursor.to_list(length=None)
        return [_doc_to_record(d) for d in docs]

    async def update(self, extraction_id: str, payload: dict) -> dict | None:
        try:
            oid = ObjectId(extraction_id)
        except (InvalidId, TypeError):
            return None
        query = {"_id": oid, **ACTIVE_FILTER}
        update_doc = {**payload, "updated_at": datetime.now(UTC)}
        result = await self._collection.find_one_and_update(
            query,
            {"$set": update_doc},
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            return None
        return _doc_to_record(result)

    async def soft_delete(self, extraction_id: str) -> bool:
        try:
            oid = ObjectId(extraction_id)
        except (InvalidId, TypeError):
            return False
        query = {"_id": oid, **ACTIVE_FILTER}
        result = await self._collection.update_one(
            query,
            {"$set": {"deleted_at": datetime.now(UTC)}},
        )
        return result.modified_count == 1


def create_motor_client(uri: str) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(uri)
