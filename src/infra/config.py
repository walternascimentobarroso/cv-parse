import json
from functools import lru_cache

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_ALLOWED_CONTENT_TYPES = "application/pdf,text/plain"


def _default_content_types_list() -> list[str]:
    return [x.strip() for x in _DEFAULT_ALLOWED_CONTENT_TYPES.split(",") if x.strip()]


def _split_content_types(s: str) -> list[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


def _parse_allowed_content_types(v: str) -> list[str]:
    s = (v or "").strip()
    if not s:
        return _default_content_types_list()
    try:
        result = json.loads(v)
    except json.JSONDecodeError:
        result = _split_content_types(v)
    if isinstance(result, list) and result:
        return [str(x).strip() for x in result if str(x).strip()]
    return _default_content_types_list()


class Settings(BaseSettings):
    # For tests, prefer .env.test when presente; otherwise fallback to .env.
    # Pydantic v2 does not support multiple env_file values directly, so we keep
    # the default here and rely on pytest/CI to point cwd and env correctly.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # NOTE: these are required at runtime, but Pyright doesn't understand
    # "required via env var" semantics. We provide defaults and validate.
    mongodb_uri: str = Field(default="", alias="MONGODB_URI")
    mongodb_db: str = Field(default="", alias="MONGODB_DB")
    extractions_collection: str = Field(default="extractions", alias="EXTRACTIONS_COLLECTION")
    # Consumed from env so Pydantic allows it; actual use is in docker-entrypoint.sh
    debugpy: str = Field(default="", alias="DEBUGPY")
    mime_type_pdf: str = Field(default="application/pdf", alias="MIME_TYPE_PDF")
    mime_type_plain: str = Field(default="text/plain", alias="MIME_TYPE_PLAIN")
    max_document_size_bytes: int = 10 * 1024 * 1024
    allowed_content_types_raw: str = Field(
        default=_DEFAULT_ALLOWED_CONTENT_TYPES,
        alias="ALLOWED_CONTENT_TYPES",
    )

    @computed_field
    @property
    def allowed_content_types(self) -> list[str]:
        return _parse_allowed_content_types(self.allowed_content_types_raw)

    @field_validator("mongodb_uri", "mongodb_db")
    @classmethod
    def _require_non_empty(cls, v: str) -> str:
        s = (v or "").strip()
        if not s:
            raise ValueError("MongoDB settings must be provided via environment variables.")
        return s


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
