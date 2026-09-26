from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed application settings.

    Secret values have no fallback so an environment cannot accidentally use a
    development key in production.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str
    redis_url: str
    field_encryption_current_version: int
    field_encryption_keys: dict[int, str]
    tag_signing_key_id: str
    tag_signing_private_key: str
    tag_signing_public_keys: dict[str, str]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
