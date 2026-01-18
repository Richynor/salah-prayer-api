"""
Custom middleware for monitoring, security, and optimization.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware to measure request processing time."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests
        if process_time > 1.0:  # More than 1 second
            logger.warning(f"Slow request: {request.method} {request.url.path} - {process_time:.3f}s")
        
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware to add cache-control headers for iPhone optimization."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add cache headers for specific endpoints
        if request.url.path.startswith("/api/v1/"):
            # Different cache policies for different endpoints
            if "/times/daily" in request.url.path:
                response.headers["Cache-Control"] = "public, max-age=3600"  # 1 hour
            elif "/times/monthly" in request.url.path:
                response.headers["Cache-Control"] = "public, max-age=86400"  # 24 hours
            elif "/qibla" in request.url.path:
                response.headers["Cache-Control"] = "public, max-age=604800"  # 1 week
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # CORS headers (already set by CORS middleware, but added for completeness)
        if "Origin" in request.headers:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        return response
