from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from src.domain.extractor import DocumentExtractor
from src.infra.config import Settings, get_settings
from src.infra.storage import ExtractionRepository

router = APIRouter()


def get_repo(request: Request) -> ExtractionRepository:
    repo: ExtractionRepository = request.app.state.extraction_repo
    return repo


def get_extractor(request: Request) -> DocumentExtractor:
    extractor: DocumentExtractor = request.app.state.document_extractor
    return extractor


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/extract")
async def extract_text(
    request: Request,
    file: Annotated[UploadFile, File(..., description="Document file")],
    settings: Annotated[Settings, Depends(get_settings)],
    repo: Annotated[ExtractionRepository, Depends(get_repo)],
    extractor: Annotated[DocumentExtractor, Depends(get_extractor)],
) -> dict[str, str]:
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document file is required.",
        )

    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported document format.",
        )

    content = await file.read()
    size_bytes = len(content)

    if size_bytes == 0:
        extracted_text = ""
    else:
        if size_bytes > settings.max_document_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Document too large.",
            )

        try:
            extracted_text = await run_in_threadpool(
                extractor.extract, content, file.content_type
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while extracting text.",
            )

    record_id = await repo.save_extraction(
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
        extracted_text=extracted_text,
        status="success",
    )

    return {
        "text": extracted_text,
        "id": record_id,
        "format": file.content_type,
    }

