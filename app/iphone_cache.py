"""
iPhone-optimized caching system for battery efficiency
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import hashlib


class iPhoneOptimizedCache:
    """Professional caching system optimized for iPhone battery efficiency."""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str, max_age_minutes: int = 60) -> Optional[Dict]:
        """Get cached data if not expired with cache statistics."""
        if key not in self._cache:
            self._misses += 1
            return None
            
        if key not in self._timestamps:
            self._misses += 1
            return None
            
        # Check if cache is expired
        age = time.time() - self._timestamps[key]
        if age > max_age_minutes * 60:
            # Cache expired
            del self._cache[key]
            del self._timestamps[key]
            self._misses += 1
            return None
            
        self._hits += 1
        return self._cache[key].copy()  # Return copy to prevent mutation
    
    def set(self, key: str, data: Dict, expire_minutes: int = 60) -> None:
        """Cache data with expiration."""
        self._cache[key] = data.copy()  # Store copy
        self._timestamps[key] = time.time()
        
    def generate_cache_key(self, latitude: float, longitude: float, 
                          date_str: str, country: str) -> str:
        """Generate deterministic cache key for prayer times."""
        key_data = f"{latitude:.6f}:{longitude:.6f}:{date_str}:{country}"
        return f"prayer:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get_prayer_times(self, latitude: float, longitude: float,
                        date_str: str, country: str) -> Optional[Dict]:
        """Get cached prayer times."""
        key = self.generate_cache_key(latitude, longitude, date_str, country)
        return self.get(key, max_age_minutes=1440)  # 24 hours for same day
        
    def cache_prayer_times(self, latitude: float, longitude: float,
                          date_str: str, country: str, data: Dict) -> None:
        """Cache prayer times with intelligent expiration."""
        key = self.generate_cache_key(latitude, longitude, date_str, country)
        
        # Calculate smart expiration based on date
        today = datetime.now().date().isoformat()
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        if date_str == today:
            # Today's times: cache until next day
            expire_minutes = 1440  # 24 hours
        elif target_date > datetime.now().date():
            # Future date: cache longer
            expire_minutes = 10080  # 7 days
        else:
            # Past date: cache indefinitely (won't change)
            expire_minutes = 525600  # 1 year
            
        self.set(key, data, expire_minutes)
    
    def get_stats(self) -> Dict:
        """Get cache statistics for monitoring."""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0,
            "active_entries": len(self._cache),
            "memory_usage_mb": sum(len(str(v)) for v in self._cache.values()) / 1024 / 1024
        }


# Global cache instance
iphone_cache = iPhoneOptimizedCache()
