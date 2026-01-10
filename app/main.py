from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import math

# Create FastAPI app
app = FastAPI(title="Fazilet Prayer Times API")

# Allow mobile app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model for mobile app request
class PrayerRequest(BaseModel):
    latitude: float
    longitude: float
    timezone_offset: float
    country: str
    date: Optional[str] = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Fazilet Prayer Times API",
        "status": "active",
        "endpoint": "POST /prayer-times/custom"
    }

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Main endpoint for mobile app
@app.post("/prayer-times/custom")
async def get_prayer_times(request: PrayerRequest):
    """Calculate prayer times for mobile app"""
    
    # Parse date or use today
    if request.date:
        try:
            target_date = datetime.strptime(request.date, "%Y-%m-%d")
        except:
            target_date = datetime.now()
    else:
        target_date = datetime.now()
    
    # Calculate prayer times (this is simplified - your app will use its own calculations)
    # These are placeholder times - your Swift app's fallback will calculate real times
    
    # Calculate Qibla direction
    qibla = calculate_qibla(request.latitude, request.longitude)
    
    return {
        "location": f"Custom ({request.latitude:.4f}, {request.longitude:.4f})",
        "date": target_date.strftime("%Y-%m-%d"),
        "country": request.country,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "timezone_offset": request.timezone_offset,
        "prayer_times": {
            "fajr": "06:00",     # Your Swift app will calculate real times
            "sunrise": "08:00",  # Your Swift app will calculate real times
            "dhuhr": "12:00",    # Your Swift app will calculate real times
            "asr": "15:00",      # Your Swift app will calculate real times
            "maghrib": "18:00",  # Your Swift app will calculate real times
            "isha": "20:00"      # Your Swift app will calculate real times
        },
        "qibla_direction": round(qibla, 2)
    }

def calculate_qibla(lat: float, lon: float) -> float:
    """Calculate Qibla direction to Kaaba (Mecca)"""
    kaaba_lat = 21.4225
    kaaba_lon = 39.8262
    
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    lat2 = math.radians(kaaba_lat)
    lon2 = math.radians(kaaba_lon)
    
    dlon = lon2 - lon1
    
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = math.atan2(y, x)
    qibla = math.degrees(bearing)
    qibla = (qibla + 360) % 360
    
    return qibla

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)