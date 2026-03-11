from datetime import datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


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
        document: dict[str, Any] = {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "extracted_text": extracted_text,
            "status": status,
            "created_at": datetime.utcnow(),
        }
        result = await self._collection.insert_one(document)
        return str(result.inserted_id)


def create_motor_client(uri: str) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(uri)

