"""
Application configuration using pydantic settings.
Loads from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "BuiltEnvironment.ai"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Security
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database - Can use DATABASE_URL directly or construct from parts
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "builtenvironment"

    def get_database_url(self) -> str:
        """Get database URL, using DATABASE_URL if set, otherwise construct from parts."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    def get_redis_url(self) -> str:
        """Get Redis URL, using REDIS_URL if set, otherwise construct from parts."""
        if self.REDIS_URL:
            return self.REDIS_URL
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # AI Services
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Langflow
    LANGFLOW_URL: str = "http://langflow:7860"
    LANGFLOW_API_KEY: Optional[str] = None

    # ChromaDB
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"

    @property
    def CHROMA_URL(self) -> str:
        """Construct ChromaDB URL."""
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"

    # File Storage
    STORAGE_TYPE: str = "local"  # "local" or "s3"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB in bytes
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".dwg"]

    # CORS - Parse from comma-separated string if provided
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins, parsing from env var if needed."""
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            return [origin.strip() for origin in cors_env.split(",")]
        return self.CORS_ORIGINS

    # Email (for future use)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@builtenvironment.ai"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to load settings only once.
    """
    return Settings()


# Export settings instance
settings = get_settings()
