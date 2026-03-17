"""Upload validation: file presence, content type, size. No HTTP; returns result type."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import UploadFile

from src.infra.config import Settings
from src.infra.logging_config import get_logger

logger = get_logger(__name__)

CHUNK_SIZE = 64 * 1024  # 64 KiB


@dataclass(frozen=True)
class ValidationOk:
    """Valid upload: content read in chunks, metadata for storage/response."""

    content: bytes
    size_bytes: int
    content_type: str
    filename: str | None
    ok: bool = True


@dataclass(frozen=True)
class ValidationError:
    """Invalid upload: status and message for route to map to HTTP."""

    status_code: int
    detail: str
    ok: bool = False


ValidationResult = ValidationOk | ValidationError


def _detail_unsupported(supported: list[str]) -> str:
    return (
        "Unsupported document format. "
        f"Supported formats: {', '.join(supported)}."
    )


def _detail_size_exceeded(max_bytes: int) -> str:
    return (
        "Document exceeds maximum allowed size "
        f"({max_bytes} bytes)."
    )


async def validate_upload(
    file: UploadFile | None,
    settings: Settings,
) -> ValidationResult:
    """
    Validate upload: presence, content type, size (via chunked read).
    Returns ValidationOk with content/metadata, or ValidationError.
    """
    if file is None:
        logger.info(
            "upload_validation",
            extra={"event": "validation_error", "reason": "missing_file"},
        )
        return ValidationError(
            status_code=400,
            detail="Document file is required.",
        )

    allowed = set(settings.allowed_content_types)
    content_type = file.content_type or ""
    if content_type not in allowed:
        logger.info(
            "upload_validation",
            extra={
                "event": "validation_error",
                "reason": "unsupported_type",
                "content_type": content_type,
            },
        )
        return ValidationError(
            status_code=400,
            detail=_detail_unsupported(list(allowed)),
        )

    max_bytes = settings.max_document_size_bytes
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            logger.info(
                "upload_validation",
                extra={"event": "validation_error", "reason": "size_exceeded", "size_bytes": total},
            )
            return ValidationError(
                status_code=413,
                detail=_detail_size_exceeded(max_bytes),
            )
        chunks.append(chunk)

    content = b"".join(chunks)
    return ValidationOk(
        content=content,
        size_bytes=len(content),
        content_type=content_type,
        filename=file.filename,
    )
