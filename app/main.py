"""
MAIN FASTAPI APPLICATION
Production-ready prayer times API with iPhone optimization.
"""

import time
import logging
from datetime import datetime, date
from typing import Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
import uvicorn

from .config import settings
from .calculator import ProfessionalAstroCalculator
from .calibrator import FaziletCalibrator
from .cache import iphone_cache
from .models import *
from .middleware import RequestTimingMiddleware, CacheControlMiddleware, SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['endpoint'])
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['endpoint'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['endpoint'])

# Startup time for uptime calculation
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Cache initialized with {iphone_cache.max_size} max entries")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Professional Prayer Times API calibrated to match Fazilet exactly. iPhone-optimized for battery efficiency.",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ORIGINS == "*" else settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestTimingMiddleware)
app.add_middleware(CacheControlMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """API information and documentation."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Professional Prayer Times API",
        "documentation": "/docs" if settings.DEBUG else None,
        "endpoints": {
            "daily_times": "/api/v1/times/daily",
            "monthly_times": "/api/v1/times/monthly",
            "qibla": "/api/v1/qibla",
            "countries": "/api/v1/countries",
            "health": "/health",
            "cache_stats": "/api/v1/cache/stats",
        },
        "features": {
            "calculation_method": "Fazilet-calibrated astronomical calculations",
            "accuracy": "Matches Fazilet app times exactly",
            "cache": "iPhone-optimized in-memory cache",
            "battery_optimized": True,
            "supported_countries": 5,
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status."""
    cache_stats = iphone_cache.get_stats()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.APP_VERSION,
        uptime_seconds=time.time() - START_TIME,
        cache_stats=cache_stats,
        endpoints_available=[
            "/api/v1/times/daily",
            "/api/v1/times/monthly",
            "/api/v1/qibla",
            "/api/v1/countries",
            "/health",
            "/metrics"
        ]
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()


@app.post("/api/v1/times/daily", response_model=PrayerTimesResponse)
async def get_daily_prayer_times(request: PrayerTimesRequest):
    """
    Get daily prayer times for a location.
    
    iPhone-optimized with intelligent caching to reduce battery usage.
    """
    REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/times/daily').inc()
    start_time = time.time()
    
    try:
        # Generate date string
        if request.date:
            date_str = request.date
        else:
            date_str = datetime.utcnow().date().isoformat()
        
        # CHECK CACHE (iPhone battery optimization)
        cached_data = iphone_cache.get_prayer_times(
            request.latitude,
            request.longitude,
            date_str,
            request.country
        )
        
        if cached_data:
            CACHE_HITS.labels(endpoint='/api/v1/times/daily').inc()
            calculation_time = (time.time() - start_time) * 1000
            
            # Return cached data with metadata
            response_data = cached_data.copy()
            response_data.update({
                "cache_hit": True,
                "calculation_time_ms": calculation_time,
                "battery_optimized": True
            })
            
            return PrayerTimesResponse(**response_data)
        
        CACHE_MISSES.labels(endpoint='/api/v1/times/daily').inc()
        
        # Parse date
        if request.date:
            target_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        else:
            target_date = datetime.utcnow().date()
        
        # Determine timezone offset
        if request.timezone_offset is not None:
            timezone_offset = request.timezone_offset
        else:
            # Simple estimation based on longitude
            timezone_offset = round(request.longitude / 15.0)
        
        # Calculate base times
        base_times = ProfessionalAstroCalculator.calculate_prayer_times(
            latitude=request.latitude,
            longitude=request.longitude,
            target_date=target_date,
            timezone_offset=timezone_offset,
            fajr_angle=18.0,
            isha_angle=17.0
        )
        
        # Apply Fazilet calibration
        calibrated_times = FaziletCalibrator.apply_calibration(base_times, request.country)
        
        # Calculate Qibla
        qibla = FaziletCalibrator.calculate_qibla(request.latitude, request.longitude)
        
        calculation_time = (time.time() - start_time) * 1000
        
        # Build response
        response_data = {
            "date": date_str,
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "country": request.country,
            "timezone_offset": timezone_offset,
            "prayer_times": calibrated_times,
            "qibla_direction": qibla,
            "calibration_applied": True,
            "cache_hit": False,
            "calculation_time_ms": calculation_time,
            "battery_optimized": True
        }
        
        # CACHE THE RESULT
        iphone_cache.set_prayer_times(
            request.latitude,
            request.longitude,
            date_str,
            request.country,
            response_data
        )
        
        return PrayerTimesResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error calculating prayer times: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.post("/api/v1/times/monthly", response_model=MonthlyPrayerTimesResponse)
async def get_monthly_prayer_times(request: MonthlyPrayerTimesRequest):
    """Get prayer times for an entire month."""
    REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/times/monthly').inc()
    start_time = time.time()
    
    try:
        # Determine timezone offset
        if request.timezone_offset is not None:
            timezone_offset = request.timezone_offset
        else:
            timezone_offset = round(request.longitude / 15.0)
        
        # Calculate for each day
        daily_times = {}
        
        # Iterate through days of month
        import calendar
        num_days = calendar.monthrange(request.year, request.month)[1]
        
        for day in range(1, num_days + 1):
            target_date = date(request.year, request.month, day)
            date_str = target_date.isoformat()
            
            # Calculate times for this day
            base_times = ProfessionalAstroCalculator.calculate_prayer_times(
                latitude=request.latitude,
                longitude=request.longitude,
                target_date=target_date,
                timezone_offset=timezone_offset
            )
            
            calibrated_times = FaziletCalibrator.apply_calibration(base_times, request.country)
            daily_times[day] = calibrated_times
        
        # Calculate Qibla
        qibla = FaziletCalibrator.calculate_qibla(request.latitude, request.longitude)
        
        calculation_time = (time.time() - start_time) * 1000
        
        return MonthlyPrayerTimesResponse(
            year=request.year,
            month=request.month,
            location={"latitude": request.latitude, "longitude": request.longitude},
            country=request.country,
            timezone_offset=timezone_offset,
            daily_times=daily_times,
            qibla_direction=qibla,
            cache_hit=False,
            calculation_time_ms=calculation_time
        )
        
    except Exception as e:
        logger.error(f"Error calculating monthly times: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.post("/api/v1/qibla", response_model=QiblaResponse)
async def get_qibla_direction(request: QiblaRequest):
    """Get Qibla direction for a location."""
    REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/qibla').inc()
    start_time = time.time()
    
    try:
        # CHECK CACHE
        cached_qibla = iphone_cache.get_qibla(request.latitude, request.longitude)
        
        if cached_qibla is not None:
            CACHE_HITS.labels(endpoint='/api/v1/qibla').inc()
            return QiblaResponse(
                latitude=request.latitude,
                longitude=request.longitude,
                qibla_direction=cached_qibla,
                kaaba_location={"latitude": 21.4225, "longitude": 39.8262},
                calculation_method="spherical_trigonometry",
                cache_hit=True
            )
        
        CACHE_MISSES.labels(endpoint='/api/v1/qibla').inc()
        
        # Calculate Qibla
        qibla = FaziletCalibrator.calculate_qibla(request.latitude, request.longitude)
        
        # Cache result
        iphone_cache.set_qibla(request.latitude, request.longitude, qibla)
        
        return QiblaResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            qibla_direction=qibla,
            kaaba_location={"latitude": 21.4225, "longitude": 39.8262},
            calculation_method="spherical_trigonometry",
            cache_hit=False
        )
        
    except Exception as e:
        logger.error(f"Error calculating Qibla: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.get("/api/v1/countries")
async def get_supported_countries():
    """Get list of supported countries with calibration status."""
    countries = FaziletCalibrator.get_supported_countries()
    
    return {
        "countries": countries,
        "total": len(countries),
        "default_country": "turkey",
        "calibration_method": "Fazilet (Turkish Diyanet)"
    }


@app.get("/api/v1/cache/stats")
async def get_cache_stats():
    """Get iPhone cache statistics for monitoring."""
    stats = iphone_cache.get_stats()
    
    return CacheStatsResponse(
        cache_type="iPhone-optimized in-memory LRU cache",
        battery_optimization=True,
        statistics=stats,
        estimated_battery_savings_percent=stats["battery_savings_percent"],
        timestamp=datetime.utcnow().isoformat()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request.headers.get('X-Request-ID', 'N/A')
        }
    )


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL,
        reload=settings.DEBUG
    )
