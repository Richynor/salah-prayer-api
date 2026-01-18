"""
Salah Prayer API - Application Package
"""
__version__ = "1.0.0"

# Export main components
from app.celery_app import celery_app
from app.iphone_cache import iphone_cache
from app.database import db

__all__ = ['celery_app', 'iphone_cache', 'db', '__version__']
