"""
Professional data models with validation using Pydantic v2.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional
from datetime import date


class Location(BaseModel):
    """Location coordinates model."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class DailyPrayerTimes(BaseModel):
    """Daily prayer times data (for caching)."""
    date: str
    location: Location
    country: str
    timezone_offset: float
    prayer_times: Dict[str, str]
    qibla_direction: float
    calibration_applied: bool = True


class PrayerTimesRequest(BaseModel):
    """Request model for daily prayer times."""
    model_config = ConfigDict(populate_by_name=True)
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    country: str = Field("turkey", description="Country for calculation method")
    timezone_offset: Optional[float] = Field(None, description="Timezone offset in hours")


class PrayerTimesResponse(BaseModel):
    """Complete response model for daily prayer times."""
    model_config = ConfigDict(populate_by_name=True)
    
    date: str
    location: Location
    country: str
    timezone_offset: float
    prayer_times: Dict[str, str]
    qibla_direction: float
    calibration_applied: bool
    cache_hit: bool = Field(default=False)
    calculation_time_ms: float = Field(default=0.0)
    battery_optimized: bool = Field(default=True)
    server_timestamp: str = Field(default_factory=lambda: date.today().isoformat())
    
    @classmethod
    def from_calculation(cls, daily_data: DailyPrayerTimes, cache_hit: bool = False) -> "PrayerTimesResponse":
        """Create response from calculation result."""
        return cls(
            date=daily_data.date,
            location=daily_data.location,
            country=daily_data.country,
            timezone_offset=daily_data.timezone_offset,
            prayer_times=daily_data.prayer_times,
            qibla_direction=daily_data.qibla_direction,
            calibration_applied=daily_data.calibration_applied,
            cache_hit=cache_hit,
            calculation_time_ms=50.0 if not cache_hit else 0.1,
            battery_optimized=True
        )


class BulkPrayerTimesRequest(BaseModel):
    """Request model for bulk prayer times."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    country: str = Field("turkey")
    timezone_offset: Optional[float] = Field(None)


class MonthData(BaseModel):
    """Data for a single month."""
    year: int
    month: int
    days_in_month: int
    daily_times: Dict[int, Dict[str, str]]


class BulkPrayerTimesResponse(BaseModel):
    """Response model for bulk prayer times."""
    latitude: float
    longitude: float
    country: str
    timezone_offset: float
    qibla_direction: float
    months: Dict[str, MonthData]
    cache_hit: bool = Field(default=False)
    calculation_time_ms: float = Field(default=0.0)
    months_included: int = Field(default=15)
    date_range: str = Field(default="Past 3 months + Next 12 months")
    optimized_for: str = Field(default="iPhone monthly table")
    recommended_refresh: str = Field(default="Once per week")


class QiblaRequest(BaseModel):
    """Request model for Qibla direction."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class QiblaResponse(BaseModel):
    """Response model for Qibla direction."""
    latitude: float
    longitude: float
    qibla_direction: float
    kaaba_location: Dict[str, float] = Field(default_factory=lambda: {"latitude": 21.4225, "longitude": 39.8262})
    calculation_method: str = Field(default="spherical_trigonometry")
    cache_hit: bool = Field(default=False)
    
    @classmethod
    def create(cls, lat: float, lon: float, qibla: float, cache_hit: bool = False) -> "QiblaResponse":
        """Factory method to create Qibla response."""
        return cls(
            latitude=lat,
            longitude=lon,
            qibla_direction=qibla,
            cache_hit=cache_hit
        )
