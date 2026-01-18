"""
Professional configuration management with validation.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings with validation."""
    
    # API Settings
    APP_NAME: str = Field(default="Salah Prayer API", description="Application name")
    APP_VERSION: str = Field(default="3.2.0", description="API version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="production", description="Runtime environment")
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Server port")
    WORKERS: int = Field(default=1, ge=1, le=4, description="Worker processes")
    LOG_LEVEL: str = Field(default="info", description="Logging level")
    
    # Security
    CORS_ORIGINS: str = Field(default="*", description="CORS allowed origins")
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    MAX_REQUESTS_PER_MINUTE: int = Field(default=60, ge=1, description="Rate limit per minute")
    
    # iPhone Optimization
    IPHONE_CACHE_SIZE: int = Field(default=500, ge=100, le=10000, description="Cache size for iPhone")
    IPHONE_MAX_AGE: int = Field(default=1440, ge=60, description="Max cache age in minutes")
    
    # Cache Settings
    CACHE_TTL_DAILY: int = Field(default=3600, ge=60, description="Daily cache TTL in seconds")
    CACHE_TTL_MONTHLY: int = Field(default=86400, ge=3600, description="Monthly cache TTL")
    CACHE_TTL_QIBLA: int = Field(default=604800, ge=3600, description="Qibla cache TTL")
    
    # For future use (Optional)
    DATABASE_URL: Optional[str] = Field(default=None, description="Database URL")
    REDIS_URL: Optional[str] = Field(default=None, description="Redis URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @classmethod
    def from_env(cls):
        """Create settings from environment variables with defaults."""
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
            MAX_REQUESTS_PER_MINUTE=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60")),
            IPHONE_CACHE_SIZE=int(os.getenv("IPHONE_CACHE_SIZE", "500")),
            IPHONE_MAX_AGE=int(os.getenv("IPHONE_MAX_AGE", "1440")),
            CACHE_TTL_DAILY=int(os.getenv("CACHE_TTL_DAILY", "3600")),
            CACHE_TTL_MONTHLY=int(os.getenv("CACHE_TTL_MONTHLY", "86400")),
            CACHE_TTL_QIBLA=int(os.getenv("CACHE_TTL_QIBLA", "604800")),
            DATABASE_URL=os.getenv("DATABASE_URL"),
            REDIS_URL=os.getenv("REDIS_URL"),
        )


# Global settings instance
settings = Settings.from_env()
