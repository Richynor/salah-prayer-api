"""
Core astronomical calculations for Islamic prayer times.
Based on proven algorithms with high precision for global locations.
"""

import math
from datetime import datetime, timedelta
from typing import Tuple


class AstronomicalCalculations:
    """High-precision astronomical calculations for prayer times."""
    
    @staticmethod
    def julian_day(date: datetime) -> float:
        """Calculate Julian Day number for a given date."""
        year = date.year
        month = date.month
        day = date.day + (date.hour + date.minute / 60.0 + date.second / 3600.0) / 24.0
        
        if month <= 2:
            year -= 1
            month += 12
        
        A = math.floor(year / 100.0)
        B = 2 - A + math.floor(A / 4.0)
        
        JD = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5
        return JD
    
    @staticmethod
    def equation_of_time(jd: float) -> float:
        """Calculate equation of time (in minutes)."""
        D = jd - 2451545.0
        g = 357.529 + 0.98560028 * D
        q = 280.459 + 0.98564736 * D
        L = q + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))
        
        e = 23.439 - 0.00000036 * D
        RA = math.degrees(math.atan2(math.cos(math.radians(e)) * math.sin(math.radians(L)), 
                                      math.cos(math.radians(L))))
        
        # Normalize RA to [0, 360]
        RA = RA % 360
        L = L % 360
        
        EqT = (L - RA) / 15.0  # Convert to time
        
        # Adjust for discontinuities
        if EqT > 12:
            EqT -= 24
        elif EqT < -12:
            EqT += 24
            
        return EqT * 60  # Convert to minutes
    
    @staticmethod
    def sun_declination(jd: float) -> float:
        """Calculate sun's declination angle."""
        D = jd - 2451545.0
        g = 357.529 + 0.98560028 * D
        q = 280.459 + 0.98564736 * D
        L = q + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))
        
        e = 23.439 - 0.00000036 * D
        sin_dec = math.sin(math.radians(e)) * math.sin(math.radians(L))
        
        return math.degrees(math.asin(sin_dec))
    
    @staticmethod
    def compute_time(angle: float, latitude: float, declination: float) -> float:
        """
        Compute time for a given sun angle.
        Returns time difference from solar noon in hours (can be negative).
        Returns None if sun never reaches that angle (high latitude problem).
        """
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        angle_rad = math.radians(angle)
        
        # Calculate hour angle
        cos_hour = (math.sin(angle_rad) - math.sin(lat_rad) * math.sin(dec_rad)) / \
                   (math.cos(lat_rad) * math.cos(dec_rad))
        
        # Check if sun reaches this angle
        if cos_hour > 1 or cos_hour < -1:
            return None
        
        hour_angle = math.degrees(math.acos(cos_hour))
        return hour_angle / 15.0  # Convert to hours
    
    @staticmethod
    def asr_time(latitude: float, declination: float, shadow_factor: float = 1.0) -> float:
        """
        Calculate Asr time based on shadow length.
        shadow_factor: 1.0 for Shafi (standard), 2.0 for Hanafi
        
        The shadow length at Asr = shadow_factor * object_height + shadow_at_noon
        
        Returns time difference from solar noon in hours.
        """
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        
        # Calculate sun's altitude at solar noon
        # altitude_noon = 90 - |latitude - declination|
        altitude_noon = 90.0 - abs(latitude - declination)
        
        # Calculate shadow length at noon relative to object height
        # shadow_noon = 1 / tan(altitude_noon)
        if altitude_noon > 0:
            shadow_noon = 1.0 / math.tan(math.radians(altitude_noon))
        else:
            shadow_noon = 9999  # Very long shadow
        
        # Total shadow at Asr
        total_shadow = shadow_factor + shadow_noon
        
        # Calculate sun altitude when shadow = total_shadow
        # tan(altitude) = 1 / total_shadow
        asr_altitude = math.degrees(math.atan(1.0 / total_shadow))
        
        # Now calculate the hour angle for this altitude
        # sin(altitude) = sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(H)
        # Solve for cos(H)
        sin_alt = math.sin(math.radians(asr_altitude))
        sin_lat = math.sin(lat_rad)
        cos_lat = math.cos(lat_rad)
        sin_dec = math.sin(dec_rad)
        cos_dec = math.cos(dec_rad)
        
        cos_hour = (sin_alt - sin_lat * sin_dec) / (cos_lat * cos_dec)
        
        # Check if sun reaches this altitude
        if cos_hour < -1 or cos_hour > 1:
            return None
        
        hour_angle = math.degrees(math.acos(cos_hour))
        return hour_angle / 15.0  # Convert to hours
    
    @staticmethod
    def solar_noon_time(longitude: float, timezone: float, equation_of_time: float) -> float:
        """Calculate solar noon time in decimal hours."""
        # Solar noon = 12:00 - (longitude/15) - (equation_of_time/60) + timezone_offset
        # timezone is in hours, equation_of_time is in minutes
        solar_noon = 12.0 - (longitude / 15.0) + timezone - (equation_of_time / 60.0)
        return solar_noon
    
    @staticmethod
    def decimal_to_time(decimal_hours: float) -> Tuple[int, int]:
        """Convert decimal hours to hours and minutes."""
        if decimal_hours < 0:
            decimal_hours += 24
        elif decimal_hours >= 24:
            decimal_hours -= 24
            
        hours = int(decimal_hours)
        minutes = int((decimal_hours - hours) * 60)
        
        return hours, minutes
    
    @staticmethod
    def minutes_to_time_string(minutes: float) -> str:
        """Convert minutes from midnight to time string HH:MM."""
        total_minutes = int(minutes)
        hours = total_minutes // 60
        mins = total_minutes % 60
        
        # Handle day overflow
        if hours >= 24:
            hours -= 24
        elif hours < 0:
            hours += 24
            
        return f"{hours:02d}:{mins:02d}"
