"""Thin HTTP layer: delegate validation to services, use DI for repo and extractor."""

from __future__ import annotations

import re
from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from src.api.dependencies import get_extractor, get_repo
from src.domain.cv_parser import parse_cv
from src.domain.document_extractor_contracts import DocumentExtractor
from src.infra.config import Settings, get_settings
from src.infra.logging_config import get_logger
from src.infra.schemas import (
    ExtractionDetailResponse,
    ExtractionListResponse,
    ExtractionUpdateRequest,
    ExtractionUpdateResponse,
    ExtractResponse,
    HealthResponse,
)
from src.infra.storage import ExtractionRepository
from src.services.upload_validator import ValidationError, validate_upload

logger = get_logger(__name__)
router = APIRouter()

# 24-char hex string (MongoDB ObjectId). Invalid id → 404 like missing/deleted.
OBJECTID_PATTERN = re.compile(r"^[0-9a-fA-F]{24}$")

MSG_NOT_FOUND = "Not found"


def _is_valid_object_id(value: str) -> bool:
    return bool(value and OBJECTID_PATTERN.match(value))


def _doc_to_detail(doc: dict) -> ExtractionDetailResponse:
    return ExtractionDetailResponse(
        id=doc["id"],
        filename=doc.get("filename"),
        content_type=doc["content_type"],
        size_bytes=doc["size_bytes"],
        extracted_text=doc["extracted_text"],
        status=doc["status"],
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
        deleted_at=doc.get("deleted_at"),
        parsed_data=doc.get("parsed_data"),
    )


@router.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/extract")
async def extract_text(
    settings: Annotated[Settings, Depends(get_settings)],
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
    extractor: Annotated[DocumentExtractor, Depends(get_extractor)],
    file: Annotated[UploadFile | None, File(description="Document file")] = None,
) -> ExtractResponse:

    logger.info(
        "extract_upload_attempt",
        extra={"upload_filename": file.filename if file else None},
    )
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
        parsed = parse_cv(extracted_text)
        parsed_data = asdict(parsed)
        record_id = await repo.save_extraction(
            filename=result.filename,
            content_type=result.content_type,
            size_bytes=result.size_bytes,
            extracted_text=extracted_text,
            status="success",
            parsed_data=parsed_data,
        )
        logger.info(
            "extraction_success",
            extra={
                "record_id": record_id,
                "content_type": result.content_type,
                "size_bytes": result.size_bytes,
            },
        )
    except Exception as exc:
        logger.exception(
            "extraction_failure",
            extra={"content_type": result.content_type, "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document.",
        )

    return ExtractResponse(
        text=extracted_text,
        id=record_id,
        format=result.content_type or "",
        parsed_data=parsed_data,
    )


@router.get("/extractions")
async def list_extractions(
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
) -> ExtractionListResponse:
    docs = await repo.find_all()
    items = [_doc_to_detail(d) for d in docs]
    return ExtractionListResponse(items=items)


@router.get("/extractions/{id}")
async def get_extraction(
    id: Annotated[str, Path()],  # noqa: A002  # pylint: disable=redefined-builtin
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
) -> ExtractionDetailResponse:
    if not _is_valid_object_id(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    doc = await repo.find_by_id(id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    return _doc_to_detail(doc)


@router.patch("/extractions/{id}")
async def update_extraction(
    id: Annotated[str, Path()],  # noqa: A002  # pylint: disable=redefined-builtin
    body: ExtractionUpdateRequest,
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
) -> ExtractionUpdateResponse:
    if not _is_valid_object_id(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    payload = body.model_dump(exclude_unset=True)
    if not payload:
        doc = await repo.find_by_id(id)
        if doc is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
        return ExtractionUpdateResponse(
            id=doc["id"],
            filename=doc.get("filename"),
            content_type=doc["content_type"],
            size_bytes=doc["size_bytes"],
            extracted_text=doc["extracted_text"],
            status=doc["status"],
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
            deleted_at=doc.get("deleted_at"),
            parsed_data=doc.get("parsed_data"),
        )
    updated = await repo.update(id, payload)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    return ExtractionUpdateResponse(
        id=updated["id"],
        filename=updated.get("filename"),
        content_type=updated["content_type"],
        size_bytes=updated["size_bytes"],
        extracted_text=updated["extracted_text"],
        status=updated["status"],
        created_at=updated["created_at"],
        updated_at=updated.get("updated_at"),
        deleted_at=updated.get("deleted_at"),
        parsed_data=updated.get("parsed_data"),
    )


@router.delete("/extractions/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_extraction(
    id: Annotated[str, Path()],  # noqa: A002  # pylint: disable=redefined-builtin
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
) -> None:
    if not _is_valid_object_id(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    deleted = await repo.soft_delete(id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    logger.info("extraction_soft_deleted", extra={"record_id": id})


@router.post("/extractions/{id}/restore")
async def restore_extraction(
    id: Annotated[str, Path()],  # noqa: A002  # pylint: disable=redefined-builtin
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
) -> ExtractionDetailResponse:
    if not _is_valid_object_id(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    result = await repo.restore(id)
    if result == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    if result == "not_deleted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extraction is not deleted.",
        )
    logger.info("extraction_restored", extra={"record_id": id})
    doc = await repo.find_by_id(id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    return _doc_to_detail(doc)


@router.delete("/extractions/{id}/force", status_code=status.HTTP_204_NO_CONTENT)
async def force_delete_extraction(
    id: Annotated[str, Path()],  # noqa: A002  # pylint: disable=redefined-builtin
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
) -> None:
    if not _is_valid_object_id(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    deleted = await repo.force_delete(id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NOT_FOUND)
    logger.info("extraction_force_deleted", extra={"record_id": id})
