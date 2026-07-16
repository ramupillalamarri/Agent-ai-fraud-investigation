import urllib.parse
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # General App Configuration
    APP_NAME: str = "Retail Fraud Investigation API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "replace_with_a_secure_random_key_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS Configuration
    # Accepts string representation of list or comma-separated strings
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(item) for item in v]
        return []

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fraud_investigation"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    @property
    def async_database_url(self) -> str:
        """Constructs the asynchronous PostgreSQL connection URI."""
        user = urllib.parse.quote_plus(self.POSTGRES_USER)
        password = urllib.parse.quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://"
            f"{user}:{password}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        """Constructs the synchronous PostgreSQL connection URI (for Alembic)."""
        user = urllib.parse.quote_plus(self.POSTGRES_USER)
        password = urllib.parse.quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql://"
            f"{user}:{password}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    # LLM & AI Agents Configuration
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-pro"
    LLM_TEMPERATURE: float = 0.0

    # Logging config
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"


# Instantiate settings to be imported where needed
settings = Settings()
