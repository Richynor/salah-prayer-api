"""
iPhone-optimized caching system for battery efficiency
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json


class iPhoneOptimizedCache:
    """
    Cache system optimized for iPhone battery efficiency:
    - In-memory cache for speed
    - Smart expiration based on prayer times
    - Minimal battery impact
    """
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        
    def get(self, key: str, max_age_minutes: int = 60) -> Optional[Dict]:
        """Get cached data if not expired."""
        if key not in self._cache:
            return None
            
        if key not in self._timestamps:
            return None
            
        # Check if cache is expired
        age = time.time() - self._timestamps[key]
        if age > max_age_minutes * 60:
            # Cache expired, remove it
            del self._cache[key]
            del self._timestamps[key]
            return None
            
        return self._cache[key]
    
    def set(self, key: str, data: Dict, expire_minutes: int = 60) -> None:
        """Cache data with expiration."""
        self._cache[key] = data
        self._timestamps[key] = time.time()
        
    def generate_cache_key(self, latitude: float, longitude: float, 
                          date_str: str, country: str) -> str:
        """Generate cache key for prayer times."""
        return f"prayer:{latitude}:{longitude}:{date_str}:{country}"
    
    def get_prayer_times(self, latitude: float, longitude: float,
                        date_str: str, country: str) -> Optional[Dict]:
        """Get cached prayer times."""
        key = self.generate_cache_key(latitude, longitude, date_str, country)
        return self.get(key, max_age_minutes=1440)  # 24 hours for same day
        
    def cache_prayer_times(self, latitude: float, longitude: float,
                          date_str: str, country: str, data: Dict) -> None:
        """Cache prayer times."""
        key = self.generate_cache_key(latitude, longitude, date_str, country)
        
        # Calculate smart expiration:
        # - If date is today, cache for 24 hours
        # - If date is future, cache longer
        today = datetime.now().date().isoformat()
        if date_str == today:
            expire_minutes = 1440  # 24 hours
        else:
            expire_minutes = 10080  # 7 days for future dates
            
        self.set(key, data, expire_minutes)


# Global cache instance
iphone_cache = iPhoneOptimizedCache()
