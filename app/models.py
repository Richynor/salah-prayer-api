"""
Data models for iPhone app API.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional


class PrayerTimesRequest(BaseModel):
    """Request for daily prayer times (iPhone home screen)."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    date: Optional[str] = None  # YYYY-MM-DD or today
    country: str = Field("turkey")
    timezone_offset: Optional[float] = None


class PrayerTimesResponse(BaseModel):
    """Daily prayer times response."""
    date: str
    location: Dict[str, float]
    country: str
    timezone_offset: float
    prayer_times: Dict[str, str]
    qibla_direction: float
    calibration_applied: bool
    cache_hit: bool
    calculation_time_ms: float
    battery_optimized: bool


class BulkPrayerTimesRequest(BaseModel):
    """
    🎯 CRITICAL: Request for 18 months of data.
    For iPhone app monthly table screen.
    Past 6 months + Future 12 months.
    """
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    country: str = Field("turkey")
    timezone_offset: Optional[float] = None


class BulkPrayerTimesResponse(BaseModel):
    """18 months of prayer times for iPhone monthly table."""
    latitude: float
    longitude: float
    country: str
    timezone_offset: float
    qibla_direction: float
    months: Dict[str, Dict]  # Format: {"2025-01": {...}, "2025-02": {...}}
    cache_hit: bool
    calculation_time_ms: float
    months_included: int
    date_range: str
    optimized_for: str
    recommended_refresh: str


class QiblaRequest(BaseModel):
    """Request for Qibla direction (iPhone compass)."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class QiblaResponse(BaseModel):
    """Qibla direction response."""
    latitude: float
    longitude: float
    qibla_direction: float
    kaaba_location: Dict[str, float]
    calculation_method: str
    cache_hit: bool
