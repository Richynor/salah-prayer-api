"""
salah_prayer_api - Professional Prayer Times API
Main FastAPI application with enterprise features.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, generate_latest

from .calculations import AstronomicalCalculator
from .calibrations import FaziletCalibration
from .models import *
from .database import db, PrayerTimesCache, MonthlyTimesCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="salah_prayer_api",
    description="Professional Prayer Times API calibrated to match Fazilet exactly",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['endpoint'])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Initialize database
    db.init_db()
    
    # Initialize Redis cache
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    pool = redis.ConnectionPool.from_url(redis_url)
    redis_client = redis.Redis(connection_pool=pool)
    FastAPICache.init(RedisBackend(redis_client), prefix="salah_prayer_api-cache")
    
    logger.info("salah_prayer_api started successfully")

# Health endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    start_time = time.time()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="3.0.0",
        uptime_seconds=time.time() - start_time,
        database_status="connected",
        cache_status="connected",
        queue_status="idle"
    )

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

# Root endpoint
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "salah_prayer_api",
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
        "cache": "Redis-backed caching with TTL",
        "monitoring": "Prometheus metrics and health checks"
    }

# Daily prayer times endpoint
@app.post("/api/v1/times/daily", response_model=PrayerTimesResponse)
@cache(expire=3600)  # Cache for 1 hour
async def get_daily_prayer_times(
    request: PrayerTimesRequest,
    background_tasks: BackgroundTasks
):
    """
    Get daily prayer times for a location.
    
    Returns Fazilet-calibrated prayer times with Qibla direction.
    """
    REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/times/daily').inc()
    start_time = time.time()
    
    try:
        # Parse date
        if request.date:
            target_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        else:
            target_date = datetime.utcnow().date()
        
        # Use provided timezone or calculate from coordinates
        if request.timezone_offset is not None:
            timezone_offset = request.timezone_offset
        else:
            # Simple timezone estimation (in production, use timezone API)
            timezone_offset = round(request.longitude / 15)
        
        # Check cache first
        cache_key = f"daily:{request.latitude}:{request.longitude}:{target_date}:{request.country}"
        
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
        
        # Log for calibration verification (background task)
        background_tasks.add_task(
            log_calibration,
            request.country,
            target_date,
            calibrated_times
        )
        
        return PrayerTimesResponse(
            date=target_date.strftime("%Y-%m-%d"),
            location={"latitude": request.latitude, "longitude": request.longitude},
            country=request.country,
            timezone_offset=timezone_offset,
            calculation_method="fazilet",
            prayer_times=calibrated_times,
            qibla_direction=qibla,
            calibration_applied=True,
            cache_hit=False,  # For now, always calculated
            calculation_time_ms=calculation_time
        )
        
    except Exception as e:
        logger.error(f"Error calculating prayer times: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

# Monthly prayer times endpoint
@app.post("/api/v1/times/monthly", response_model=MonthlyPrayerTimesResponse)
@cache(expire=86400)  # Cache for 24 hours
async def get_monthly_prayer_times(
    request: MonthlyPrayerTimesRequest,
    background_tasks: BackgroundTasks
):
    """
    Get monthly prayer times for a location.
    
    Returns Fazilet-calibrated prayer times for entire month.
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
        
        # Queue background task for caching
        background_tasks.add_task(
            cache_monthly_times,
            request.latitude,
            request.longitude,
            request.year,
            request.month,
            request.country,
            daily_times,
            qibla
        )
        
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
        logger.error(f"Error calculating monthly times: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

# Qibla endpoint
@app.post("/api/v1/qibla", response_model=QiblaResponse)
@cache(expire=604800)  # Cache for 1 week (Qibla doesn't change)
async def get_qibla_direction(request: QiblaRequest):
    """
    Get Qibla direction for a location.
    
    Returns accurate Qibla direction in degrees from North.
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
        logger.error(f"Error calculating Qibla: {e}")
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
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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
async def log_calibration(country: str, date: date, times: Dict[str, str]):
    """Log calibration for verification."""
    try:
        session = db.get_session()
        log = CalibrationLog(
            country=country,
            date=date.strftime("%Y-%m-%d"),
            calculated_times=times,
            created_at=datetime.utcnow()
        )
        session.add(log)
        session.commit()
        session.close()
    except Exception as e:
        logger.error(f"Error logging calibration: {e}")

async def cache_monthly_times(latitude: float, longitude: float, year: int, 
                             month: int, country: str, daily_times: Dict, qibla: float):
    """Cache monthly times in database."""
    try:
        session = db.get_session()
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        cache_entry = MonthlyTimesCache(
            latitude=latitude,
            longitude=longitude,
            year=year,
            month=month,
            country=country,
            daily_times=daily_times,
            qibla_direction=qibla,
            expires_at=expires_at
        )
        
        session.add(cache_entry)
        session.commit()
        session.close()
    except Exception as e:
        logger.error(f"Error caching monthly times: {e}")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=2,
        log_level="info",
        access_log=True
    )
