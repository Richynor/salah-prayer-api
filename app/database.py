"""
Database connection and models for salah_prayer_api.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

Base = declarative_base()

class PrayerTimesCache(Base):
    """Cache for prayer times calculations."""
    __tablename__ = 'prayer_times_cache'
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    date = Column(String, nullable=False)
    country = Column(String, nullable=False)
    prayer_times = Column(JSON, nullable=False)
    qibla_direction = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class MonthlyTimesCache(Base):
    """Cache for monthly prayer times."""
    __tablename__ = 'monthly_times_cache'
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    daily_times = Column(JSON, nullable=False)
    qibla_direction = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

class CalibrationLog(Base):
    """Log of calibration verifications."""
    __tablename__ = 'calibration_log'
    
    id = Column(Integer, primary_key=True)
    country = Column(String, nullable=False)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    date = Column(String, nullable=False)
    actual_times = Column(JSON)
    calculated_times = Column(JSON)
    differences = Column(JSON)
    accuracy_score = Column(Float)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    """Database connection manager."""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///salah_prayer_api.db')
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
    """Initialize database tables."""
    # Temporarily disable database initialization
    # Base.metadata.create_all(bind=self.engine)
    print("Database initialization skipped - running in cache-only mode")
    
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close database session."""
        session.close()

# Singleton database instance
db = Database()
