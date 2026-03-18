from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from src.api.routes import router as api_router
from src.infra.config import get_settings
from src.infra.extractors.registry import ExtractorRegistry
from src.infra.logging_config import configure_logging
from src.infra.storage import ExtractionRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    settings = get_settings()

    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]
    collection = db[settings.extractions_collection]

    app.state.mongo_client = client
    app.state.mongo_db = db
    app.state.extraction_repo = ExtractionRepository(collection)
    app.state.document_extractor = ExtractorRegistry(
        mime_type_plain=settings.mime_type_plain,
        mime_type_pdf=settings.mime_type_pdf,
    )

    try:
        yield
    finally:
        client.close()


app = FastAPI(title="Doc-to-Text API", lifespan=lifespan)

app.include_router(api_router)
