"""
Uzbekistan Official Prayer Times Scraper
Source: islam.uz (Sheikh Muhammad Sodiq Muhammad Yusuf)

LOCATION: /app/scrapers/uzbekistan.py
"""

import re
import logging
import asyncio
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UzbekistanCity:
    """Uzbekistan city configuration."""
    id: int
    name_ru: str
    name_uz: str
    name_en: str
    latitude: float
    longitude: float
    
    
# Uzbekistan Cities - Mapping to islam.uz city IDs with coordinates
UZBEKISTAN_CITIES = {
    "tashkent": UzbekistanCity(27, "Ташкент", "Toshkent", "Tashkent", 41.2995, 69.2401),
    "andijan": UzbekistanCity(1, "Андижан", "Andijon", "Andijan", 40.7821, 72.3442),
    "bukhara": UzbekistanCity(4, "Бухара", "Buxoro", "Bukhara", 39.7747, 64.4286),
    "samarkand": UzbekistanCity(18, "Самарканд", "Samarqand", "Samarkand", 39.6270, 66.9750),
    "namangan": UzbekistanCity(15, "Наманган", "Namangan", "Namangan", 40.9983, 71.6726),
    "qarshi": UzbekistanCity(25, "Карши", "Qarshi", "Qarshi", 38.8606, 65.7894),
    "khiva": UzbekistanCity(21, "Хива", "Xiva", "Khiva", 41.3775, 60.3642),
    "navoi": UzbekistanCity(14, "Навои", "Navoiy", "Navoi", 40.0844, 65.3792),
    "jizzakh": UzbekistanCity(9, "Джизак", "Jizzax", "Jizzakh", 40.1158, 67.8422),
    "nukus": UzbekistanCity(16, "Нукус", "Nukus", "Nukus", 42.4531, 59.6103),
    "kokand": UzbekistanCity(26, "Коканж", "Qo'qon", "Kokand", 40.5283, 70.9424),
    "margilan": UzbekistanCity(13, "Маргилан", "Marg'ilon", "Margilan", 40.4717, 71.7244),
    "gulistan": UzbekistanCity(5, "Гулистан", "G'uliston", "Gulistan", 40.4897, 68.7842),
}


class UzbekistanPrayerTimesService:
    """Service to fetch official Uzbekistan prayer times from islam.uz"""
    
    BASE_URL = "https://islam.uz/vremyanamazov"
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    
    # Prayer name mapping: Russian -> Central Asian names
    PRAYER_NAMES = {
        "fajr": "bomdod",     # Bomdod (Dawn)
        "sunrise": "quyosh",  # Sunrise (Шурук)
        "dhuhr": "peshin",    # Peshin (Noon)
        "asr": "asr",         # Asr (Afternoon)
        "maghrib": "shom",    # Shom (Sunset)
        "isha": "khuftan"     # Khuftan (Night)
    }
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        )
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    def _parse_time(self, time_str: str) -> str:
        """
        Parse time string from table.
        Input: "06:13" or "6:13"
        Output: "06:13" (normalized HH:MM)
        """
        try:
            time_str = time_str.strip()
            # Handle both "06:13" and "6:13" formats
            parts = time_str.split(':')
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])
                return f"{hour:02d}:{minute:02d}"
            return time_str
        except Exception as e:
            logger.error(f"Error parsing time '{time_str}': {e}")
            return time_str
    
    def _get_city_url(self, city_key: str, month: int) -> str:
        """
        Get URL for city prayer times.
        Format: https://islam.uz/vremyanamazov/{city_id}/{month}
        """
        city = UZBEKISTAN_CITIES.get(city_key.lower())
        if not city:
            raise ValueError(f"Unknown city: {city_key}")
        
        return f"{self.BASE_URL}/{city.id}/{month}"
    
    async def _fetch_html(self, url: str) -> str:
        """Fetch HTML with retry logic."""
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = await self.client.get(url)
                response.raise_for_status()
                return response.text
                
            except httpx.HTTPError as e:
                last_error = e
                logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))
            
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))
        
        raise Exception(f"Failed to fetch after {self.MAX_RETRIES} attempts: {last_error}")
    
    def _parse_monthly_table(self, html: str, year: int, month: int) -> Dict[int, Dict[str, str]]:
        """
        Parse monthly prayer times table.
        
        Table structure:
        | День | День недели | Фаджр (Сухур) | Шурук | Зухр | Аср | Магриб (Ифтар) | Иша |
        | 1    | Понедельник | 06:13         | 07:35 | 12:37| 15:57| 17:42           | 19:00|
        
        Returns: {day: {prayer: time}}
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find the prayer times table
            table = soup.find('table')
            if not table:
                raise ValueError("Prayer times table not found")
            
            rows = table.find_all('tr')
            if len(rows) < 2:
                raise ValueError("Table has insufficient rows")
            
            # Parse header to find column indices
            header = rows[0]
            headers = [th.get_text(strip=True) for th in header.find_all(['th', 'td'])]
            logger.info(f"Table headers: {headers}")
            
            # Find column indices (flexible to handle variations)
            day_idx = 0  # First column is always day
            fajr_idx = None
            sunrise_idx = None
            dhuhr_idx = None
            asr_idx = None
            maghrib_idx = None
            isha_idx = None
            
            for idx, h in enumerate(headers):
                h_lower = h.lower()
                if 'фаджр' in h_lower or 'сухур' in h_lower:
                    fajr_idx = idx
                elif 'шурук' in h_lower:
                    sunrise_idx = idx
                elif 'зухр' in h_lower:
                    dhuhr_idx = idx
                elif 'аср' in h_lower:
                    asr_idx = idx
                elif 'магриб' in h_lower or 'ифтар' in h_lower:
                    maghrib_idx = idx
                elif 'иша' in h_lower or 'хуфтан' in h_lower:
                    isha_idx = idx
            
            if None in [fajr_idx, sunrise_idx, dhuhr_idx, asr_idx, maghrib_idx, isha_idx]:
                raise ValueError(f"Could not find all prayer columns. Headers: {headers}")
            
            logger.info(f"Column indices - Fajr:{fajr_idx}, Sunrise:{sunrise_idx}, Dhuhr:{dhuhr_idx}, Asr:{asr_idx}, Maghrib:{maghrib_idx}, Isha:{isha_idx}")
            
            # Parse data rows
            daily_times = {}
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) < max(fajr_idx, sunrise_idx, dhuhr_idx, asr_idx, maghrib_idx, isha_idx) + 1:
                    continue
                
                try:
                    # Parse day number
                    day_text = cells[day_idx].get_text(strip=True)
                    day_match = re.search(r'\d+', day_text)
                    if not day_match:
                        continue
                    day = int(day_match.group())
                    
                    # Parse times
                    fajr = self._parse_time(cells[fajr_idx].get_text(strip=True))
                    sunrise = self._parse_time(cells[sunrise_idx].get_text(strip=True))
                    dhuhr = self._parse_time(cells[dhuhr_idx].get_text(strip=True))
                    asr = self._parse_time(cells[asr_idx].get_text(strip=True))
                    maghrib = self._parse_time(cells[maghrib_idx].get_text(strip=True))
                    isha = self._parse_time(cells[isha_idx].get_text(strip=True))
                    
                    daily_times[day] = {
                        "bomdod": fajr,
                        "quyosh": sunrise,
                        "peshin": dhuhr,
                        "asr": asr,
                        "shom": maghrib,
                        "khuftan": isha
                    }
                    
                except (ValueError, AttributeError, IndexError) as e:
                    logger.warning(f"Error parsing row: {e}")
                    continue
            
            logger.info(f"Parsed {len(daily_times)} days for {year}-{month:02d}")
            return daily_times
            
        except Exception as e:
            logger.error(f"Error parsing table: {e}")
            raise
    
    async def fetch_monthly_times(
        self,
        city: str,
        year: int,
        month: int
    ) -> Dict[int, Dict[str, str]]:
        """
        Fetch monthly prayer times for a city.
        
        Args:
            city: City key (e.g., "tashkent", "bukhara")
            year: Year
            month: Month (1-12)
        
        Returns:
            {day: {prayer: time}}
        """
        try:
            # Get URL
            url = self._get_city_url(city, month)
            
            # Fetch HTML
            html = await self._fetch_html(url)
            
            # Parse table
            daily_times = self._parse_monthly_table(html, year, month)
            
            if not daily_times:
                raise ValueError("No prayer times found")
            
            return daily_times
            
        except Exception as e:
            logger.error(f"Error fetching Uzbekistan times for {city} {year}-{month}: {e}")
            raise
    
    async def fetch_current_month(self, city: str) -> Dict[int, Dict[str, str]]:
        """Fetch current month's prayer times."""
        now = datetime.now()
        return await self.fetch_monthly_times(city, now.year, now.month)
    
    def get_city_info(self, city_key: str) -> Optional[UzbekistanCity]:
        """Get city information."""
        return UZBEKISTAN_CITIES.get(city_key.lower())
    
    @staticmethod
    def get_all_cities() -> Dict[str, UzbekistanCity]:
        """Get all available cities."""
        return UZBEKISTAN_CITIES.copy()
    
    @staticmethod
    def find_nearest_city(latitude: float, longitude: float) -> Tuple[str, UzbekistanCity, float]:
        """
        Find nearest Uzbekistan city to given coordinates.
        
        Returns:
            (city_key, city_info, distance_km)
        """
        import math
        
        def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate distance between two points in kilometers."""
            R = 6371  # Earth radius in kilometers
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            return R * c
        
        nearest_key = None
        nearest_city = None
        nearest_distance = float('inf')
        
        for key, city in UZBEKISTAN_CITIES.items():
            distance = haversine_distance(latitude, longitude, city.latitude, city.longitude)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_key = key
                nearest_city = city
        
        return nearest_key, nearest_city, nearest_distance
