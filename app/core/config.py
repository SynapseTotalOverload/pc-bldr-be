from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Keepa FastAPI Service"
    api_prefix: str = "/api/v1"

    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")
    keepa_key: str = Field(..., alias="KEEPA_API_KEY")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
