"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import date


class PrayerTimesRequest(BaseModel):
    """Request model for daily prayer times."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format (default: today)")
    country: str = Field("turkey", description="Country for Fazilet calibration")
    timezone_offset: Optional[float] = Field(None, description="Timezone offset from UTC in hours")
    
    @validator('date')
    def validate_date(cls, v):
        if v is not None:
            try:
                # Validate date format
                year, month, day = map(int, v.split('-'))
                date(year, month, day)
            except:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class PrayerTimesResponse(BaseModel):
    """Response model for daily prayer times."""
    date: str
    location: Dict[str, float]
    country: str
    timezone_offset: float
    calculation_method: str = "fazilet"
    prayer_times: Dict[str, str]
    qibla_direction: float
    calibration_applied: bool = True
    cache_hit: bool = False
    calculation_time_ms: float
    battery_optimized: bool = True


class MonthlyPrayerTimesRequest(BaseModel):
    """Request model for monthly prayer times."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    country: str = Field("turkey")
    timezone_offset: Optional[float] = None


class MonthlyPrayerTimesResponse(BaseModel):
    """Response model for monthly prayer times."""
    year: int
    month: int
    location: Dict[str, float]
    country: str
    timezone_offset: float
    calculation_method: str = "fazilet"
    daily_times: Dict[int, Dict[str, str]]
    qibla_direction: float
    cache_hit: bool = False
    calculation_time_ms: float


class QiblaRequest(BaseModel):
    """Request model for Qibla direction."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class QiblaResponse(BaseModel):
    """Response model for Qibla direction."""
    latitude: float
    longitude: float
    qibla_direction: float
    kaaba_location: Dict[str, float]
    calculation_method: str = "spherical_trigonometry"
    cache_hit: bool = False


class CountryInfo(BaseModel):
    """Country information model."""
    code: str
    name: str
    verified: bool
    verified_dates: List[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    cache_stats: Dict
    endpoints_available: List[str]


class CacheStatsResponse(BaseModel):
    """Cache statistics response."""
    cache_type: str
    battery_optimization: bool
    statistics: Dict
    estimated_battery_savings_percent: float
    timestamp: str
