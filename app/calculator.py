"""
PROFESSIONAL ASTRONOMICAL CALCULATOR
High-precision calculations optimized for production.
"""

import math
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ProfessionalAstroCalculator:
    """Production-grade astronomical calculator for prayer times."""
    
    # Constants
    J2000 = 2451545.0
    OBLIQUITY = 23.4392911
    
    @staticmethod
    def julian_day(dt: datetime) -> float:
        """High-precision Julian Day calculation."""
        year = dt.year
        month = dt.month
        day = dt.day + (dt.hour + dt.minute/60.0 + dt.second/3600.0) / 24.0
        
        if month <= 2:
            year -= 1
            month += 12
        
        a = math.floor(year / 100.0)
        b = 2 - a + math.floor(a / 4.0)
        
        jd = (math.floor(365.25 * (year + 4716)) + 
              math.floor(30.6001 * (month + 1)) + 
              day + b - 1524.5)
        
        return jd
    
    @staticmethod
    def sun_declination(jd: float) -> float:
        """Calculate sun's declination angle with high precision."""
        # Mean anomaly
        g = 357.529 + 0.98560028 * (jd - ProfessionalAstroCalculator.J2000)
        g_rad = math.radians(g)
        
        # Equation of center
        c = 1.9148 * math.sin(g_rad) + 0.0200 * math.sin(2 * g_rad) + 0.0003 * math.sin(3 * g_rad)
        
        # Ecliptic longitude
        lam = g + c + 180.0 + 102.9372
        lam_rad = math.radians(lam)
        
        # Obliquity
        e_rad = math.radians(ProfessionalAstroCalculator.OBLIQUITY)
        
        # Declination
        sin_dec = math.sin(e_rad) * math.sin(lam_rad)
        return math.degrees(math.asin(sin_dec))
    
    @staticmethod
    def equation_of_time(jd: float) -> float:
        """Calculate equation of time in minutes."""
        # Mean anomaly
        g = 357.529 + 0.98560028 * (jd - ProfessionalAstroCalculator.J2000)
        g_rad = math.radians(g)
        
        # Equation of center
        c = 1.9148 * math.sin(g_rad) + 0.0200 * math.sin(2 * g_rad) + 0.0003 * math.sin(3 * g_rad)
        
        # Ecliptic longitude
        lam = g + c + 180.0 + 102.9372
        lam_rad = math.radians(lam)
        
        # Right ascension
        e_rad = math.radians(ProfessionalAstroCalculator.OBLIQUITY)
        ra = math.atan2(math.cos(e_rad) * math.sin(lam_rad), math.cos(lam_rad))
        ra_deg = math.degrees(ra)
        
        # Equation of time
        eq_time = lam - ra_deg
        if eq_time > 180:
            eq_time -= 360
        elif eq_time < -180:
            eq_time += 360
        
        return eq_time * 4  # Convert to minutes
    
    @staticmethod
    def hour_angle(latitude: float, declination: float, angle: float) -> Optional[float]:
        """Calculate hour angle for given sun angle below horizon."""
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        angle_rad = math.radians(angle)
        
        # Cosine of hour angle
        cos_h = (math.sin(angle_rad) - math.sin(lat_rad) * math.sin(dec_rad)) / \
                (math.cos(lat_rad) * math.cos(dec_rad))
        
        # Check if sun reaches this angle
        if abs(cos_h) > 1:
            return None
        
        h = math.degrees(math.acos(cos_h))
        return h
    
    @staticmethod
    def asr_hour_angle(latitude: float, declination: float, shadow_factor: float = 1.0) -> Optional[float]:
        """Calculate hour angle for Asr prayer."""
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        
        # Sun altitude for Asr
        altitude = math.degrees(math.atan(1.0 / shadow_factor))
        alt_rad = math.radians(altitude)
        
        # Calculate hour angle
        sin_alt = math.sin(alt_rad)
        sin_lat = math.sin(lat_rad)
        cos_lat = math.cos(lat_rad)
        sin_dec = math.sin(dec_rad)
        cos_dec = math.cos(dec_rad)
        
        cos_h = (sin_alt - sin_lat * sin_dec) / (cos_lat * cos_dec)
        
        if abs(cos_h) > 1:
            return None
        
        return math.degrees(math.acos(cos_h))
    
    @staticmethod
    def calculate_prayer_times(
        latitude: float,
        longitude: float,
        target_date: date,
        timezone_offset: float,
        fajr_angle: float = 18.0,
        isha_angle: float = 17.0
    ) -> Dict[str, str]:
        """Calculate prayer times for given location and date."""
        try:
            # Create datetime at solar noon
            dt = datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0)
            jd = ProfessionalAstroCalculator.julian_day(dt)
            
            # Get astronomical parameters
            declination = ProfessionalAstroCalculator.sun_declination(jd)
            eq_time = ProfessionalAstroCalculator.equation_of_time(jd)
            
            # Calculate solar noon
            solar_noon = 12.0 - (longitude / 15.0) + timezone_offset - (eq_time / 60.0)
            
            # Calculate hour angles
            fajr_ha = ProfessionalAstroCalculator.hour_angle(latitude, declination, -fajr_angle)
            sunrise_ha = ProfessionalAstroCalculator.hour_angle(latitude, declination, -0.833)
            asr_ha = ProfessionalAstroCalculator.asr_hour_angle(latitude, declination, 1.0)
            maghrib_ha = ProfessionalAstroCalculator.hour_angle(latitude, declination, -0.833)
            isha_ha = ProfessionalAstroCalculator.hour_angle(latitude, declination, -isha_angle)
            
            # Calculate times in decimal hours
            times = {}
            
            if fajr_ha:
                fajr_decimal = solar_noon - (fajr_ha / 15.0)
                times['fajr'] = fajr_decimal
            else:
                times['fajr'] = None
            
            if sunrise_ha:
                sunrise_decimal = solar_noon - (sunrise_ha / 15.0)
                times['sunrise'] = sunrise_decimal
            else:
                times['sunrise'] = None
            
            times['dhuhr'] = solar_noon
            
            if asr_ha:
                asr_decimal = solar_noon + (asr_ha / 15.0)
                times['asr'] = asr_decimal
            else:
                times['asr'] = None
            
            if maghrib_ha:
                maghrib_decimal = solar_noon + (maghrib_ha / 15.0)
                times['maghrib'] = maghrib_decimal
            else:
                times['maghrib'] = None
            
            if isha_ha:
                isha_decimal = solar_noon + (isha_ha / 15.0)
                times['isha'] = isha_decimal
            else:
                times['isha'] = None
            
            # Format times
            formatted_times = {}
            for prayer, decimal in times.items():
                if decimal is not None:
                    hour = int(decimal)
                    minute = int((decimal - hour) * 60)
                    formatted_times[prayer] = f"{hour:02d}:{minute:02d}"
                else:
                    formatted_times[prayer] = "N/A"
            
            return formatted_times
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            raise
    
    @staticmethod
    def format_time(decimal_hours: float) -> str:
        """Convert decimal hours to HH:MM format."""
        if decimal_hours < 0:
            decimal_hours += 24
        elif decimal_hours >= 24:
            decimal_hours -= 24
        
        hour = int(decimal_hours)
        minute = int((decimal_hours - hour) * 60)
        
        return f"{hour:02d}:{minute:02d}"
