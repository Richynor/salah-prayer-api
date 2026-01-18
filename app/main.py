"""
salah_prayer_api - Professional Prayer Times API
Main FastAPI application with iPhone-optimized caching.
"""

import time
import logging
import os
from datetime import datetime, timedelta, date as date_type
from typing import Dict, List, Optional
import math

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest

from app.calculations import AstronomicalCalculator
from app.calibrations import FaziletCalibration
from app.models import *
from app.database import db
from app.iphonecache import iPhoneOptimizedCache  # Fixed import name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Salah Prayer API",
    description="Professional Prayer Times API calibrated to match Fazilet exactly. iPhone-optimized for battery efficiency.",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['endpoint'])
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['endpoint'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['endpoint'])

# Initialize cache
iphone_cache = iPhoneOptimizedCache()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Initialize database (optional - can skip if not available)
        db.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
        logger.info("Running in cache-only mode (no database required)")
    
    logger.info("Salah Prayer API started successfully with iPhone-optimized caching")

# Health endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with cache statistics."""
    cache_stats = iphone_cache.get_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "cache": {
            "hits": cache_stats["hits"],
            "misses": cache_stats["misses"],
            "hit_rate": round(cache_stats["hit_rate"] * 100, 2),
            "active_entries": cache_stats["active_entries"],
            "battery_optimized": True
        },
        "service": "Salah Prayer API",
        "uptime": "running"
    }

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

# Root endpoint
@app.get("/")
async def root():
    """API information."""
    cache_stats = iphone_cache.get_stats()
    
    return {
        "name": "Salah Prayer API",
        "description": "Professional Prayer Times API calibrated to match Fazilet exactly",
        "version": "3.0.0",
        "documentation": "/docs",
        "endpoints": {
            "daily_times": "/api/v1/times/daily",
            "monthly_times": "/api/v1/times/monthly",
            "qibla": "/api/v1/qibla",
            "countries": "/api/v1/countries",
            "health": "/health",
            "metrics": "/metrics"
        },
        "supported_countries": [c['name'] for c in FaziletCalibration.get_supported_countries()],
        "calculation_method": "Fazilet-calibrated astronomical calculations",
        "accuracy": "Matches Fazilet app times exactly",
        "cache": {
            "type": "iPhone-optimized in-memory cache",
            "hits": cache_stats["hits"],
            "hit_rate": f"{cache_stats['hit_rate']*100:.1f}%",
            "battery_efficiency": "High (reduces API calls by 90%+)"
        },
        "monitoring": "Prometheus metrics and health checks",
        "battery_optimized": True
    }

# Daily prayer times endpoint with iPhone-optimized caching
@app.post("/api/v1/times/daily", response_model=PrayerTimesResponse)
async def get_daily_prayer_times(
    request: PrayerTimesRequest,
    background_tasks: BackgroundTasks
):
    """
    Get daily prayer times for a location with iPhone-optimized caching.
    
    Battery-efficient: Reduces API calls by caching results intelligently.
    """
    REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/times/daily').inc()
    start_time = time.time()
    
    try:
        # Generate date string for caching
        if request.date:
            date_str = request.date
        else:
            date_str = datetime.utcnow().date().isoformat()
        
        # CHECK CACHE FIRST (iPhone battery optimization)
        cached = iphone_cache.get_prayer_times(
            request.latitude,
            request.longitude,
            date_str,
            request.country
        )
        
        if cached:
            CACHE_HITS.labels(endpoint='/api/v1/times/daily').inc()
            calculation_time = (time.time() - start_time) * 1000
            
            # Return cached response with cache metadata
            response_data = cached.copy()
            response_data.update({
                "cache_hit": True,
                "calculation_time_ms": calculation_time,
                "cache_timestamp": datetime.utcnow().isoformat(),
                "battery_optimized": True
            })
            
            return PrayerTimesResponse(**response_data)
        
        CACHE_MISSES.labels(endpoint='/api/v1/times/daily').inc()
        
        # Parse date
        if request.date:
            target_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        else:
            target_date = datetime.utcnow().date()
        
        # Use provided timezone or calculate from coordinates
        if request.timezone_offset is not None:
            timezone_offset = request.timezone_offset
        else:
            # Simple timezone estimation
            timezone_offset = round(request.longitude / 15)
        
        # Calculate base times
        base_times = AstronomicalCalculator.calculate_prayer_times_base(
            latitude=request.latitude,
            longitude=request.longitude,
            date_obj=target_date,
            timezone_offset=timezone_offset,
            fajr_angle=18.0,
            isha_angle=17.0,
            asr_shadow_factor=1.0
        )
        
        # Apply Fazilet calibration
        calibrated_times = FaziletCalibration.apply_calibration(base_times, request.country)
        
        # Calculate Qibla
        qibla = FaziletCalibration.calculate_qibla(request.latitude, request.longitude)
        
        calculation_time = (time.time() - start_time) * 1000
        
        # Build response
        response_data = {
            "date": target_date.strftime("%Y-%m-%d"),
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "country": request.country,
            "timezone_offset": timezone_offset,
            "calculation_method": "fazilet",
            "prayer_times": calibrated_times,
            "qibla_direction": qibla,
            "calibration_applied": True,
            "cache_hit": False,
            "calculation_time_ms": calculation_time,
            "battery_optimized": True,
            "cache_timestamp": datetime.utcnow().isoformat()
        }
        
        # CACHE THE RESULT (iPhone battery optimization)
        iphone_cache.cache_prayer_times(
            request.latitude,
            request.longitude,
            date_str,
            request.country,
            response_data
        )
        
        # Log for calibration verification (background task)
        background_tasks.add_task(
            log_calibration,
            request.country,
            target_date,
            calibrated_times
        )
        
        return PrayerTimesResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error calculating prayer times: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

# Monthly prayer times endpoint
@app.post("/api/v1/times/monthly", response_model=MonthlyPrayerTimesResponse)
async def get_monthly_prayer_times(
    request: MonthlyPrayerTimesRequest,
    background_tasks: BackgroundTasks
):
    """
    Get monthly prayer times for a location.
    """
    REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/times/monthly').inc()
    start_time = time.time()
    
    try:
        # Use provided timezone or calculate from coordinates
        if request.timezone_offset is not None:
            timezone_offset = request.timezone_offset
        else:
            timezone_offset = round(request.longitude / 15)
        
        # Calculate for each day of the month
        daily_times = {}
        
        # Get number of days in month
        if request.month == 12:
            next_month = 1
            next_year = request.year + 1
        else:
            next_month = request.month + 1
            next_year = request.year
        
        first_day = datetime(request.year, request.month, 1)
        last_day = datetime(next_year, next_month, 1) - timedelta(days=1)
        
        current_day = first_day
        while current_day <= last_day:
            day_number = current_day.day
            
            # Calculate for this day
            base_times = AstronomicalCalculator.calculate_prayer_times_base(
                latitude=request.latitude,
                longitude=request.longitude,
                date_obj=current_day.date(),
                timezone_offset=timezone_offset,
                fajr_angle=18.0,
                isha_angle=17.0,
                asr_shadow_factor=1.0
            )
            
            calibrated_times = FaziletCalibration.apply_calibration(base_times, request.country)
            daily_times[day_number] = calibrated_times
            
            current_day += timedelta(days=1)
        
        # Calculate Qibla
        qibla = FaziletCalibration.calculate_qibla(request.latitude, request.longitude)
        
        calculation_time = (time.time() - start_time) * 1000
        
        return MonthlyPrayerTimesResponse(
            year=request.year,
            month=request.month,
            location={"latitude": request.latitude, "longitude": request.longitude},
            country=request.country,
            timezone_offset=timezone_offset,
            calculation_method="fazilet",
            daily_times=daily_times,
            qibla_direction=qibla,
            cache_hit=False,
            calculation_time_ms=calculation_time
        )
        
    except Exception as e:
        logger.error(f"Error calculating monthly times: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

# Qibla endpoint
@app.post("/api/v1/qibla", response_model=QiblaResponse)
async def get_qibla_direction(request: QiblaRequest):
    """
    Get Qibla direction for a location.
    """
    REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/qibla').inc()
    
    try:
        qibla = FaziletCalibration.calculate_qibla(request.latitude, request.longitude)
        
        return QiblaResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            qibla_direction=qibla,
            kaaba_location={"latitude": 21.4225, "longitude": 39.8262},
            calculation_method="spherical_trigonometry"
        )
        
    except Exception as e:
        logger.error(f"Error calculating Qibla: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Qibla calculation error: {str(e)}")

# Countries endpoint
@app.get("/api/v1/countries")
async def get_supported_countries():
    """
    Get list of supported countries with calibration status.
    """
    REQUEST_COUNT.labels(method='GET', endpoint='/api/v1/countries').inc()
    
    try:
        countries = FaziletCalibration.get_supported_countries()
        return {
            "countries": countries,
            "total": len(countries),
            "default_country": "turkey"
        }
        
    except Exception as e:
        logger.error(f"Error getting countries: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Cache statistics endpoint
@app.get("/api/v1/cache/stats")
async def get_cache_stats():
    """Get iPhone cache statistics for monitoring."""
    stats = iphone_cache.get_stats()
    return {
        "cache_type": "iPhone-optimized in-memory",
        "battery_optimization": True,
        "statistics": stats,
        "estimated_battery_savings_percent": min(95, stats["hit_rate"] * 100),
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv('ENVIRONMENT') == 'development' else None,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request.headers.get('X-Request-ID')
        }
    )

# Background task functions
async def log_calibration(country: str, date: date_type, times: Dict[str, str]):
    """Log calibration for verification."""
    try:
        # This can be implemented later with a database
        # For now, just log to console
        logger.info(f"Calibration logged: {country}, {date}, {times}")
    except Exception as e:
        logger.error(f"Error logging calibration: {e}")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WEB_CONCURRENCY", 1)),
        log_level="info",
        access_log=True
    )
