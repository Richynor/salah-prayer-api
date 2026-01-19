"""
Custom middleware for monitoring, security, and optimization.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware to measure request processing time."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        if process_time > 1.0:
            logger.warning(f"Slow request: {request.method} {request.url.path} - {process_time:.3f}s")
        
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware to add cache-control headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        if request.url.path.startswith("/api/v1/"):
            if "/times/daily" in request.url.path:
                response.headers["Cache-Control"] = "public, max-age=3600"
            elif "/times/bulk" in request.url.path:
                response.headers["Cache-Control"] = "public, max-age=86400"
            elif "/qibla" in request.url.path:
                response.headers["Cache-Control"] = "public, max-age=604800"
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        if "Origin" in request.headers:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        return response
