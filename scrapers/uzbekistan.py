"""
Uzbekistan Official Prayer Times Scraper
Source: islam.uz (Sheikh Muhammad Sodiq Muhammad Yusuf)
Official Islamic authority for Uzbekistan
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
    
    
# Uzbekistan Cities - Mapping to islam.uz city IDs
UZBEKISTAN_CITIES = {
    "tashkent": UzbekistanCity(27, "Ташкент", "Toshkent", "Tashkent"),
    "andijan": UzbekistanCity(1, "Андижан", "Andijon", "Andijan"),
    "bukhara": UzbekistanCity(4, "Бухара", "Buxoro", "Bukhara"),
    "samarkand": UzbekistanCity(18, "Самарканд", "Samarqand", "Samarkand"),
    "namangan": UzbekistanCity(15, "Наманган", "Namangan", "Namangan"),
    "qarshi": UzbekistanCity(25, "Карши", "Qarshi", "Qarshi"),
    "khiva": UzbekistanCity(21, "Хива", "Xiva", "Khiva"),
    "navoi": UzbekistanCity(14, "Навои", "Navoiy", "Navoi"),
    "jizzakh": UzbekistanCity(9, "Джизак", "Jizzax", "Jizzakh"),
    "nukus": UzbekistanCity(16, "Нукус", "Nukus", "Nukus"),
    "kokand": UzbekistanCity(26, "Кокандж", "Qo'qon", "Kokand"),
    "margilan": UzbekistanCity(13, "Маргилан", "Marg'ilon", "Margilan"),
    "gulistan": UzbekistanCity(5, "Гулистан", "G'uliston", "Gulistan"),
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
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'ru,en;q=0.9',
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
                    day = int(re.search(r'\d+', day_text).group())
                    
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
    ) -> Dict[str, Dict[str, str]]:
        """
        Fetch monthly prayer times for a city.
        
        Args:
            city: City key (e.g., "tashkent", "bukhara")
            year: Year
            month: Month (1-12)
        
        Returns:
            {"day": {prayer: time}} - day as string
        """
        try:
            # Get URL
            url = self._get_city_url(city, month)
            
            # Fetch HTML
            html = await self._fetch_html(url)
            
            # Parse table
            daily_times_int = self._parse_monthly_table(html, year, month)
            
            if not daily_times_int:
                raise ValueError("No prayer times found")
            
            # Convert day numbers to strings for JSON compatibility
            daily_times = {str(day): times for day, times in daily_times_int.items()}
            
            return daily_times
            
        except Exception as e:
            logger.error(f"Error fetching Uzbekistan times for {city} {year}-{month}: {e}")
            raise
    
    async def fetch_current_month(self, city: str) -> Dict[str, Dict[str, str]]:
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
