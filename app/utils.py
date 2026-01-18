"""
Utility functions for salah_prayer_api.
"""
import math
from datetime import datetime, date
from typing import Tuple, Optional


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
    """Validate latitude and longitude coordinates."""
    if not (-90 <= latitude <= 90):
        return False, f"Latitude {latitude} is out of range (-90 to 90)"
    
    if not (-180 <= longitude <= 180):
        return False, f"Longitude {longitude} is out of range (-180 to 180)"
    
    return True, "Coordinates are valid"


def calculate_timezone_from_longitude(longitude: float) -> float:
    """
    Estimate timezone offset from longitude.
    15 degrees of longitude = 1 hour timezone difference.
    """
    return round(longitude / 15.0)


def format_time_difference(minutes: float) -> str:
    """Format time difference in a human-readable way."""
    if minutes < 1:
        return f"{minutes*60:.0f} seconds"
    elif minutes < 60:
        return f"{minutes:.1f} minutes"
    else:
        hours = minutes / 60
        return f"{hours:.1f} hours"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c
