"""
Configuration management for production deployment.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable fallbacks."""
    
    # API Settings
    APP_NAME: str = "Salah Prayer API"
    APP_VERSION: str = "3.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 2
    LOG_LEVEL: str = "info"
    
    # Database (Optional - for future scaling)
    DATABASE_URL: Optional[str] = None
    
    # Redis Cache (Optional - for future scaling)
    REDIS_URL: Optional[str] = None
    
    # Cache Settings
    CACHE_TTL_DAILY: int = 3600  # 1 hour for daily prayers
    CACHE_TTL_MONTHLY: int = 86400  # 24 hours for monthly
    CACHE_TTL_QIBLA: int = 604800  # 1 week for Qibla
    
    # iPhone Optimization
    IPHONE_CACHE_SIZE: int = 1000  # Max cache entries
    IPHONE_MAX_AGE: int = 1440  # 24 hours in minutes
    
    # Security
    CORS_ORIGINS: str = "*"
    RATE_LIMIT_ENABLED: bool = True
    MAX_REQUESTS_PER_MINUTE: int = 60
    
    # Monitoring
    ENABLE_METRICS: bool = True
    HEALTH_CHECK_INTERVAL: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
