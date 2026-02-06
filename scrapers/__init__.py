"""
Scrapers package for fetching prayer times from official sources.
"""

# ✅ RELATIVE IMPORTS within subpackage
from .uzbekistan import UzbekistanPrayerTimesService, UZBEKISTAN_CITIES

__all__ = [
    'UzbekistanPrayerTimesService',
    'UZBEKISTAN_CITIES',
]
