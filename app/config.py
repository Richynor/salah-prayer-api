"""
Professional configuration management with validation.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings with validation."""
    
    APP_NAME: str = Field(default="Salah Prayer API")
    APP_VERSION: str = Field(default="3.2.0")
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="production")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000, ge=1, le=65535)
    WORKERS: int = Field(default=1, ge=1, le=4)
    LOG_LEVEL: str = Field(default="info")
    CORS_ORIGINS: str = Field(default="*")
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    MAX_REQUESTS_PER_MINUTE: int = Field(default=120, ge=1)
    IPHONE_CACHE_SIZE: int = Field(default=1000, ge=100, le=10000)
    IPHONE_MAX_AGE: int = Field(default=1440, ge=60)
    CACHE_TTL_DAILY: int = Field(default=3600, ge=60)
    CACHE_TTL_MONTHLY: int = Field(default=86400, ge=3600)
    CACHE_TTL_QIBLA: int = Field(default=604800, ge=3600)
    DATABASE_URL: Optional[str] = Field(default=None)
    REDIS_URL: Optional[str] = Field(default=None)
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @classmethod
    def from_env(cls):
        """Create settings from environment variables."""
        return cls(
            APP_NAME=os.getenv("APP_NAME", "Salah Prayer API"),
            APP_VERSION=os.getenv("APP_VERSION", "3.2.0"),
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            ENVIRONMENT=os.getenv("ENVIRONMENT", "production"),
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "8000")),
            WORKERS=int(os.getenv("WORKERS", "1")),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "info"),
            CORS_ORIGINS=os.getenv("CORS_ORIGINS", "*"),
            RATE_LIMIT_ENABLED=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            MAX_REQUESTS_PER_MINUTE=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "120")),
            IPHONE_CACHE_SIZE=int(os.getenv("IPHONE_CACHE_SIZE", "1000")),
            IPHONE_MAX_AGE=int(os.getenv("IPHONE_MAX_AGE", "1440")),
            CACHE_TTL_DAILY=int(os.getenv("CACHE_TTL_DAILY", "3600")),
            CACHE_TTL_MONTHLY=int(os.getenv("CACHE_TTL_MONTHLY", "86400")),
            CACHE_TTL_QIBLA=int(os.getenv("CACHE_TTL_QIBLA", "604800")),
            DATABASE_URL=os.getenv("DATABASE_URL"),
            REDIS_URL=os.getenv("REDIS_URL"),
        )


settings = Settings.from_env()
