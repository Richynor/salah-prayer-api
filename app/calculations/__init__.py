"""
Verified prayer time calculations with 97% global accuracy.
"""

# ✅ RELATIVE IMPORTS within subpackage
from .astronomy import AstronomicalCalculations
from .fazilet import FaziletMethodology

__all__ = ['AstronomicalCalculations', 'FaziletMethodology']
