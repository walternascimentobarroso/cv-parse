from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from src.api.routes import router as api_router
from src.domain.extractor import SimpleDocumentExtractor
from src.infra.config import get_settings
from src.infra.storage import ExtractionRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]
    collection = db["extractions"]

    app.state.mongo_client = client
    app.state.mongo_db = db
    app.state.extraction_repo = ExtractionRepository(collection)
    app.state.document_extractor = SimpleDocumentExtractor(
        settings.allowed_content_types
    )

    try:
        yield
    finally:
        client.close()


app = FastAPI(title="Doc-to-Text API", lifespan=lifespan)

app.include_router(api_router)

