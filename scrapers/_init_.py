"""
Scrapers package for fetching prayer times from official sources.
"""

from .uzbekistan import UzbekistanPrayerTimesService, UZBEKISTAN_CITIES

__all__ = [
    'UzbekistanPrayerTimesService',
    'UZBEKISTAN_CITIES',
]
