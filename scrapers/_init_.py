"""
Gido Prayer Times API Package
Official prayer times for Norway, Turkey, South Korea, Tajikistan, and Uzbekistan
"""

__version__ = "4.0.0"
__author__ = "Gido Prayer API Team"
__description__ = "Prayer times API: Fazilet calculations + Official sources"

# Version check
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("Python 3.8 or higher is required")

from app.calculations.fazilet import FaziletMethodology
from app.cache import cache
from app.config import settings

__all__ = ['FaziletMethodology', 'cache', 'settings', '__version__']
