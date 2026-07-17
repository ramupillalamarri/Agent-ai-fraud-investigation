import urllib.parse
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # General App Configuration
    APP_NAME: str = "Retail Fraud Investigation API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "replace_with_a_secure_random_key_in_production"
    JWT_ISSUER: str = "retail-fraud-investigation-api"
    JWT_AUDIENCE: str = "retail-fraud-investigation-clients"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    ALLOW_PUBLIC_REGISTRATION: bool = False
    INITIAL_ADMIN_EMAIL: str = ""
    INITIAL_ADMIN_PASSWORD: str = ""

    # CORS Configuration - comma-separated string
    BACKEND_CORS_ORIGINS: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse BACKEND_CORS_ORIGINS string into a list."""
        if not self.BACKEND_CORS_ORIGINS:
            return []
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

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
        """Constructs the sync PostgreSQL connection URI (for Alembic)."""
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

    def validate_security(self) -> None:
        """Reject production configurations that would weaken authentication."""
        if self.APP_ENV.lower() != "production":
            return
        if self.SECRET_KEY == "replace_with_a_secure_random_key_in_production" or len(
            self.SECRET_KEY
        ) < 32:
            raise ValueError("SECRET_KEY must be a unique value of at least 32 characters.")
        if self.BCRYPT_ROUNDS < 12:
            raise ValueError("BCRYPT_ROUNDS must be at least 12 in production.")
        if self.DEBUG:
            raise ValueError("DEBUG must be disabled in production.")


# Instantiate settings to be imported where needed
settings = Settings()
