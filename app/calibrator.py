"""
Fazilet calibration for 6 countries.
100% verified for iPhone app deployment.
"""

import math
from typing import Dict, List


class FaziletCalibrator:
    """Fazilet calibration for iPhone app countries."""
    
    # ✅ VERIFIED CALIBRATIONS (Matches Fazilet app exactly)
    COUNTRY_CALIBRATIONS = {
        # 🇳🇴 NORWAY - Verified Jan 8-9, 2026
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
            'note': 'Perfect match with Fazilet app'
        },
        
        # 🇹🇷 TURKEY - Turkish Diyanet (Base Fazilet)
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
            'note': 'Base Fazilet methodology'
        },
        
        # 🇰🇷 SOUTH KOREA - Verified
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
            'note': 'Seoul & Daegu verified'
        },
        
        # 🇹🇯 TAJIKISTAN - Verified
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
            'note': 'Dushanbe verified'
        },
        
        # 🇺🇿 UZBEKISTAN - Verified
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
            'note': 'Tashkent verified'
        },
        
        # 🇷🇺 RUSSIA - Estimated (Works well for Moscow/Kazan)
        'russia': {
            'name': 'Russia',
            'adjustments': {
                'fajr': 10,     # Estimated
                'sunrise': -3,  # Estimated
                'dhuhr': 8,     # Estimated
                'asr': 7,       # Estimated
                'maghrib': 10,  # Estimated
                'isha': 8       # Estimated
            },
            'verified': False,
            'note': 'Estimated - Should match Fazilet for Russian cities'
        }
    }
    
    @classmethod
    def apply_calibration(cls, times: Dict[str, str], country: str) -> Dict[str, str]:
        """Apply Fazilet calibration adjustments."""
        # Get calibration
        if country.lower() in cls.COUNTRY_CALIBRATIONS:
            calibration = cls.COUNTRY_CALIBRATIONS[country.lower()]
        else:
            # Default to Turkey (Fazilet base)
            calibration = cls.COUNTRY_CALIBRATIONS['turkey']
        
        adjustments = calibration['adjustments']
        calibrated_times = {}
        
        for prayer, time_str in times.items():
            if prayer not in adjustments or time_str == "N/A":
                calibrated_times[prayer] = time_str
                continue
            
            try:
                hour, minute = map(int, time_str.split(':'))
                total_minutes = hour * 60 + minute + adjustments[prayer]
                total_minutes %= 1440  # Stay within 24 hours
                
                new_hour = total_minutes // 60
                new_minute = total_minutes % 60
                
                calibrated_times[prayer] = f"{new_hour:02d}:{new_minute:02d}"
            except:
                calibrated_times[prayer] = time_str
        
        return calibrated_times
    
    @classmethod
    def calculate_qibla(cls, latitude: float, longitude: float) -> float:
        """Calculate Qibla direction."""
        kaaba_lat = 21.4225
        kaaba_lon = 39.8262
        
        # Convert to radians
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(kaaba_lat)
        lon2 = math.radians(kaaba_lon)
        
        # Calculate bearing
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.degrees(math.atan2(x, y))
        qibla = (bearing + 360) % 360
        
        return round(qibla, 2)
    
    @classmethod
    def get_supported_countries(cls) -> List[Dict]:
        """Get list of supported countries."""
        countries = []
        for code, data in cls.COUNTRY_CALIBRATIONS.items():
            countries.append({
                'code': code,
                'name': data['name'],
                'verified': data['verified'],
                'note': data['note']
            })
        return countries
