"""
Background tasks for Celery workers.
"""
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from celery import current_app

from app.calculations import AstronomicalCalculator
from app.calibrations import FaziletCalibration
from app.database import db
from app.iphone_cache import iphone_cache

logger = logging.getLogger(__name__)

@current_app.task(name='app.tasks.calculate_prayer_times_async')
def calculate_prayer_times_async(latitude: float, longitude: float, 
                                date_str: str, country: str = 'turkey',
                                timezone_offset: float = None) -> Dict:
    """Calculate prayer times asynchronously (for batch processing)."""
    try:
        from datetime import date as date_type
        
        # Parse date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Calculate timezone if not provided
        if timezone_offset is None:
            timezone_offset = round(longitude / 15)
        
        # Calculate base times
        base_times = AstronomicalCalculator.calculate_prayer_times_base(
            latitude=latitude,
            longitude=longitude,
            date_obj=target_date,
            timezone_offset=timezone_offset,
            fajr_angle=18.0,
            isha_angle=17.0,
            asr_shadow_factor=1.0
        )
        
        # Apply Fazilet calibration
        calibrated_times = FaziletCalibration.apply_calibration(base_times, country)
        
        # Calculate Qibla
        qibla = FaziletCalibration.calculate_qibla(latitude, longitude)
        
        result = {
            "date": date_str,
            "location": {"latitude": latitude, "longitude": longitude},
            "country": country,
            "timezone_offset": timezone_offset,
            "prayer_times": calibrated_times,
            "qibla_direction": qibla,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        # Cache the result
        iphone_cache.cache_prayer_times(latitude, longitude, date_str, country, result)
        
        logger.info(f"Async calculation completed for {date_str}, {country}")
        return result
        
    except Exception as e:
        logger.error(f"Error in async prayer times calculation: {e}")
        raise

@current_app.task(name='app.tasks.daily_cache_warmup')
def daily_cache_warmup():
    """Warm up cache for today's prayer times for popular locations."""
    try:
        # Popular locations to pre-cache
        popular_locations = [
            # Norway
            (59.9139, 10.7522, 'oslo', 'norway', 1.0),
            # Turkey
            (41.0082, 28.9784, 'istanbul', 'turkey', 3.0),
            # South Korea
            (37.5665, 126.9780, 'seoul', 'south_korea', 9.0),
            # Tajikistan
            (38.5598, 68.7738, 'dushanbe', 'tajikistan', 5.0),
            # Uzbekistan
            (41.2995, 69.2401, 'tashkent', 'uzbekistan', 5.0),
        ]
        
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
        
        for lat, lon, city, country, tz in popular_locations:
            # Calculate for today
            calculate_prayer_times_async.delay(lat, lon, today, country, tz)
            
            # Calculate for tomorrow (pre-cache)
            calculate_prayer_times_async.delay(lat, lon, tomorrow, country, tz)
        
        logger.info(f"Daily cache warmup completed for {len(popular_locations)} locations")
        return {"status": "success", "locations_processed": len(popular_locations)}
        
    except Exception as e:
        logger.error(f"Error in daily cache warmup: {e}")
        return {"status": "error", "error": str(e)}

@current_app.task(name='app.tasks.precalculate_next_month')
def precalculate_next_month():
    """Pre-calculate prayer times for next month for popular locations."""
    try:
        popular_locations = [
            (59.9139, 10.7522, 'oslo', 'norway', 1.0),
            (41.0082, 28.9784, 'istanbul', 'turkey', 3.0),
            (37.5665, 126.9780, 'seoul', 'south_korea', 9.0),
        ]
        
        # Calculate for next month
        today = datetime.now()
        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year
        
        for lat, lon, city, country, tz in popular_locations:
            # Calculate for each day of next month
            for day in range(1, 32):  # Max 31 days
                try:
                    date_str = f"{next_year}-{next_month:02d}-{day:02d}"
                    calculate_prayer_times_async.delay(lat, lon, date_str, country, tz)
                except ValueError:  # Invalid date (e.g., Feb 30)
                    continue
        
        logger.info(f"Pre-calculated next month for {len(popular_locations)} locations")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error in monthly pre-calculation: {e}")
        return {"status": "error", "error": str(e)}

@current_app.task(name='app.tasks.celery_health_check')
def celery_health_check():
    """Celery health check task."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "celery",
        "queue": current_app.conf.task_default_queue
    }

@current_app.task(name='app.tasks.batch_calculate_locations')
def batch_calculate_locations(locations: List[Dict], date_str: str):
    """Batch calculate prayer times for multiple locations."""
    results = []
    
    for location in locations:
        lat = location.get('latitude')
        lon = location.get('longitude')
        country = location.get('country', 'turkey')
        tz = location.get('timezone_offset')
        
        if lat is not None and lon is not None:
            result = calculate_prayer_times_async.delay(lat, lon, date_str, country, tz)
            results.append(result.id)
    
    return {
        "task_ids": results,
        "total_locations": len(locations),
        "date": date_str
    }
