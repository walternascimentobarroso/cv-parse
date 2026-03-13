"""Thin HTTP layer: delegate validation to services, use DI for repo and extractor."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from src.api.dependencies import get_extractor, get_repo
from src.domain.document_extractor_contracts import DocumentExtractor
from src.infra.config import Settings, get_settings
from src.infra.logging_config import get_logger
from src.infra.schemas import ExtractResponse, HealthResponse
from src.infra.storage import ExtractionRepository
from src.services.upload_validator import ValidationError, validate_upload

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/extract", response_model=ExtractResponse)
async def extract_text(
    settings: Annotated[Settings, Depends(get_settings)],
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
    extractor: Annotated[DocumentExtractor, Depends(get_extractor)],
    file: Annotated[UploadFile | None, File(description="Document file")] = None,
) -> ExtractResponse:
    logger.info("extract_upload_attempt", extra={"filename": file.filename if file else None})
    result = await validate_upload(file, settings)

    if isinstance(result, ValidationError):
        raise HTTPException(
            status_code=result.status_code,
            detail=result.detail,
        )

    if result.size_bytes == 0:
        return ExtractResponse(
            text="",
            id="",
            format=result.content_type or "",
        )

    try:
        extracted_text = await run_in_threadpool(
            extractor.extract,
            result.content,
            result.content_type,
        )
        record_id = await repo.save_extraction(
            filename=result.filename,
            content_type=result.content_type,
            size_bytes=result.size_bytes,
            extracted_text=extracted_text,
            status="success",
        )
        logger.info(
            "extraction_success",
            extra={"record_id": record_id, "content_type": result.content_type, "size_bytes": result.size_bytes},
        )
    except Exception as exc:
        logger.exception("extraction_failure", extra={"content_type": result.content_type, "error": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document.",
        )

    return ExtractResponse(
        text=extracted_text,
        id=record_id,
        format=result.content_type or "",
    )
