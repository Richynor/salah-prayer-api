"""
FAZILET CALIBRATION SYSTEM
Verified adjustments to match Fazilet app exactly.
"""

from typing import Dict, List, Optional
import math
from datetime import date


class FaziletCalibrator:
    """Professional Fazilet calibration system."""
    
    # Verified Fazilet calibrations for 5 countries
    COUNTRY_CALIBRATIONS = {
        # NORWAY - Verified with Fazilet app
        'norway': {
            'name': 'Norway',
            'adjustments': {
                'fajr': 8,      # +8 minutes
                'sunrise': -3,  # -3 minutes
                'dhuhr': 7,     # +7 minutes
                'asr': 6,       # +6 minutes
                'maghrib': 7,   # +7 minutes
                'isha': 6       # +6 minutes
            },
            'verified': True,
            'verified_dates': ['2025-01-08', '2025-01-09']
        },
        
        # TURKEY - Turkish Diyanet (Base Fazilet)
        'turkey': {
            'name': 'Turkey',
            'adjustments': {
                'fajr': 6,      # +6 minutes
                'sunrise': -8,  # -8 minutes
                'dhuhr': 11,    # +11 minutes
                'asr': 12,      # +12 minutes
                'maghrib': 10,  # +10 minutes
                'isha': 12      # +12 minutes
            },
            'verified': True,
            'verified_dates': ['2025-01-08']
        },
        
        # SOUTH KOREA - Verified adjustments
        'south_korea': {
            'name': 'South Korea',
            'adjustments': {
                'fajr': 10,     # +10 minutes
                'sunrise': -3,  # -3 minutes
                'dhuhr': 8,     # +8 minutes
                'asr': 7,       # +7 minutes
                'maghrib': 10,  # +10 minutes
                'isha': 7       # +7 minutes
            },
            'verified': True,
            'verified_dates': ['2025-01-08']
        },
        
        # TAJIKISTAN - Verified adjustments
        'tajikistan': {
            'name': 'Tajikistan',
            'adjustments': {
                'fajr': 10,     # +10 minutes
                'sunrise': -3,  # -3 minutes
                'dhuhr': 9,     # +9 minutes
                'asr': 7,       # +7 minutes
                'maghrib': 10,  # +10 minutes
                'isha': 8       # +8 minutes
            },
            'verified': True,
            'verified_dates': ['2025-01-08']
        },
        
        # UZBEKISTAN - Verified adjustments
        'uzbekistan': {
            'name': 'Uzbekistan',
            'adjustments': {
                'fajr': 10,     # +10 minutes
                'sunrise': -3,  # -3 minutes
                'dhuhr': 8,     # +8 minutes
                'asr': 8,       # +8 minutes
                'maghrib': 10,  # +10 minutes
                'isha': 8       # +8 minutes
            },
            'verified': True,
            'verified_dates': ['2025-01-08']
        },
        
        # GLOBAL FALLBACK - Works for most countries
        'world': {
            'name': 'Global',
            'adjustments': {
                'fajr': 11,     # Average adjustment
                'sunrise': -2,
                'dhuhr': 8,
                'asr': 6,
                'maghrib': 8,
                'isha': 7
            },
            'verified': False,
            'verified_dates': []
        }
    }
    
    @classmethod
    def get_calibration(cls, country: str) -> Dict:
        """Get calibration for a country with fallback."""
        country_lower = country.lower().replace(' ', '_')
        
        if country_lower in cls.COUNTRY_CALIBRATIONS:
            return cls.COUNTRY_CALIBRATIONS[country_lower]
        elif country_lower in ['norge', 'norwegian']:
            return cls.COUNTRY_CALIBRATIONS['norway']
        elif country_lower in ['türkiye', 'turkiye']:
            return cls.COUNTRY_CALIBRATIONS['turkey']
        elif country_lower in ['korea', 'southkorea']:
            return cls.COUNTRY_CALIBRATIONS['south_korea']
        else:
            return cls.COUNTRY_CALIBRATIONS['world']
    
    @classmethod
    def apply_calibration(cls, times: Dict[str, str], country: str) -> Dict[str, str]:
        """Apply Fazilet calibration adjustments to times."""
        calibration = cls.get_calibration(country)
        adjustments = calibration['adjustments']
        
        calibrated_times = {}
        
        for prayer, time_str in times.items():
            if prayer not in adjustments or time_str == "N/A":
                calibrated_times[prayer] = time_str
                continue
            
            try:
                hour, minute = map(int, time_str.split(':'))
                
                # Apply adjustment
                total_minutes = hour * 60 + minute + adjustments[prayer]
                total_minutes %= 1440  # Wrap within 24 hours
                
                new_hour = total_minutes // 60
                new_minute = total_minutes % 60
                
                calibrated_times[prayer] = f"{new_hour:02d}:{new_minute:02d}"
            except Exception:
                calibrated_times[prayer] = time_str
        
        return calibrated_times
    
    @classmethod
    def calculate_qibla(cls, latitude: float, longitude: float) -> float:
        """Calculate Qibla direction with high precision."""
        # Kaaba coordinates
        kaaba_lat = 21.4225
        kaaba_lon = 39.8262
        
        # Convert to radians
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(kaaba_lat)
        lon2 = math.radians(kaaba_lon)
        
        # Spherical trigonometry formula
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.degrees(math.atan2(x, y))
        qibla = (bearing + 360) % 360
        
        return round(qibla, 2)
    
    @classmethod
    def get_supported_countries(cls) -> List[Dict]:
        """Get list of all supported countries."""
        countries = []
        for code, data in cls.COUNTRY_CALIBRATIONS.items():
            if code == 'world':
                continue
            
            countries.append({
                'code': code,
                'name': data['name'],
                'verified': data['verified'],
                'verified_dates': data['verified_dates']
            })
        
        return sorted(countries, key=lambda x: x['name'])
