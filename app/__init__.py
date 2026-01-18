"""
Salah Prayer API - Professional Prayer Times Service
Version: 3.2.0
Optimized for iPhone app deployment
"""

__version__ = "3.2.0"
__author__ = "Salah Prayer API Team"
__description__ = "Professional prayer times API with iPhone optimization"
__license__ = "MIT"

# Version check
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("Python 3.8 or higher is required")

# Export main components
__all__ = [
    "ProfessionalAstroCalculator",
    "FaziletCalibrator", 
    "iPhoneOptimizedCache",
    "settings"
]
