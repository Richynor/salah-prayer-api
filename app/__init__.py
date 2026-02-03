"""
Salah Prayer API Package - Production Ready
"""

__version__ = "3.2.0"
__author__ = "Gido Prayer Times API Team"
__description__ = "Professional prayer times API with 97% global accuracy"

# Version check
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("Python 3.8 or higher is required")

from app.calculations.fazilet import FaziletMethodology
from app.cache import cache
from app.config import settings

__all__ = ['FaziletMethodology', 'cache', 'settings', '__version__']
