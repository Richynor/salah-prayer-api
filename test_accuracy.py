"""
Verification test to ensure API matches our verified results.
Run this before deploying to Railway!
"""

import sys
sys.path.insert(0, '.')

from app.calculations.fazilet import FaziletMethodology
from datetime import datetime

print("="*80)
print("🔍 TESTING CALCULATION ACCURACY")
print("="*80)

# Test data from our global verification
test_cities = [
    ("Oslo, Norway", 59.9139, 10.7522, 1.0, "norway", {
        'fajr': '06:39', 'dhuhr': '12:30', 'asr': '13:30', 'maghrib': '15:45', 'isha': '18:11'
    }),
    ("Paris, France", 48.8566, 2.3522, 1.0, "world", {
        'fajr': '06:56', 'dhuhr': '13:04', 'asr': '14:59', 'maghrib': '17:21', 'isha': '19:07'
    }),
    ("Cairo, Egypt", 30.0444, 31.2357, 2.0, "world", {
        'fajr': '05:38', 'dhuhr': '12:09', 'asr': '14:58', 'maghrib': '17:19', 'isha': '18:37'
    }),
    ("New York, USA", 40.7128, -74.0060, -5.0, "world", {
        'fajr': '05:51', 'dhuhr': '12:10', 'asr': '14:33', 'maghrib': '16:54', 'isha': '18:24'
    }),
]

test_date = datetime(2026, 1, 9).date()

total = 0
correct = 0

for city, lat, lon, tz, country, expected in test_cities:
    print(f"\n{city}:")
    
    times = FaziletMethodology.calculate_prayer_times(
        latitude=lat,
        longitude=lon,
        date=test_date,
        timezone_offset=tz,
        country=country
    )
    
    for prayer, expected_time in expected.items():
        calculated = times[prayer]
        total += 1
        
        # Parse times
        e_h, e_m = map(int, expected_time.split(':'))
        c_h, c_m = map(int, calculated.split(':'))
        
        diff = abs((e_h * 60 + e_m) - (c_h * 60 + c_m))
        
        if diff <= 3:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"  {prayer.capitalize()}: {calculated} (expected {expected_time}) {status} ±{diff}min")

accuracy = (correct / total) * 100
print(f"\n{'='*80}")
print(f"ACCURACY: {correct}/{total} = {accuracy:.1f}%")
print(f"{'='*80}")

if accuracy >= 95:
    print("✅ EXCELLENT! Ready for deployment!")
    sys.exit(0)
elif accuracy >= 85:
    print("⚠️  GOOD but could be better. Review differences.")
    sys.exit(0)
else:
    print("❌ ACCURACY TOO LOW! Do not deploy.")
    sys.exit(1)
