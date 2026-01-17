"""
Data models for salah_prayer_api.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import date, datetime


class PrayerTimesRequest(BaseModel):
    """Request model for prayer times calculation."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format (default: today)")
    country: str = Field("turkey", description="Country for Fazilet calibration")
    timezone_offset: Optional[float] = Field(None, description="Timezone offset from UTC in hours")
    calculation_method: Optional[str] = Field("fazilet", description="Calculation method")

class PrayerTimesResponse(BaseModel):
    """Response model for prayer times."""
    date: str
    location: Dict[str, float]
    country: str
    timezone_offset: float
    calculation_method: str
    prayer_times: Dict[str, str]
    qibla_direction: float
    calibration_applied: bool
    cache_hit: bool
    calculation_time_ms: float

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
    calculation_method: str
    daily_times: Dict[int, Dict[str, str]]
    qibla_direction: float
    cache_hit: bool
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
    calculation_method: str

class CountryInfo(BaseModel):
    """Country information model."""
    code: str
    name: str
    verified: bool
    verified_dates: List[str]
    calibration: Optional[Dict] = None

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    database_status: str
    cache_status: str
    queue_status: str

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None
