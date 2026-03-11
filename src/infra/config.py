from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mongodb_uri: str = "mongodb://mongodb:27017"
    mongodb_db: str = "doctotext"
    max_document_size_bytes: int = 10 * 1024 * 1024
    allowed_content_types: list[str] = ["application/pdf", "text/plain"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

