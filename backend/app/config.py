from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import re


def _ensure_async_driver(url: str) -> str:
    if url.startswith("sqlite"):
        if "+aiosqlite" not in url and url.startswith("sqlite://"):
            return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url
    if url.startswith("postgresql+asyncpg://") or url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    APP_NAME: str = "AgriBrain AI"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "agribrain"

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

    WEATHER_API_KEY: Optional[str] = None
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def db_url(self) -> str:
        from pathlib import Path
        env_file = Path(".env")
        if env_file.exists():
            from dotenv import dotenv_values
            env_vals = dotenv_values(".env")
            db_url = env_vals.get("DATABASE_URL")
            if db_url:
                return _ensure_async_driver(db_url)
        import os
        if os.environ.get("USE_POSTGRES"):
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return "sqlite+aiosqlite:///./agribrain_dev.db"


settings = Settings()
