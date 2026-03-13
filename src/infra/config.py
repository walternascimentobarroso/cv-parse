import json
from functools import lru_cache

from pydantic import computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.domain.constants import DEFAULT_ALLOWED_CONTENT_TYPES


def _parse_allowed_content_types(v: str) -> list[str]:
    s = (v or "").strip()
    if not s:
        return DEFAULT_ALLOWED_CONTENT_TYPES
    try:
        return json.loads(v)
    except json.JSONDecodeError:
        return [x.strip() for x in v.split(",") if x.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mongodb_uri: str = "mongodb://mongodb:27017"
    mongodb_db: str = "doctotext"
    max_document_size_bytes: int = 10 * 1024 * 1024
    allowed_content_types_raw: str = Field(
        default=",".join(DEFAULT_ALLOWED_CONTENT_TYPES),
        alias="ALLOWED_CONTENT_TYPES",
    )

    @computed_field
    @property
    def allowed_content_types(self) -> list[str]:
        return _parse_allowed_content_types(self.allowed_content_types_raw)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

