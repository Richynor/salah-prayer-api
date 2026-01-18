"""
Celery configuration for background tasks.
"""
import os
from celery import Celery
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    'salah_prayer_api',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['app.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Daily cache warmup at 00:01 AM
        'daily-cache-warmup': {
            'task': 'app.tasks.daily_cache_warmup',
            'schedule': crontab(minute=1, hour=0),  # 00:01 daily
        },
        # Monthly calculation at 1st of month, 02:00 AM
        'monthly-precalculation': {
            'task': 'app.tasks.precalculate_next_month',
            'schedule': crontab(day_of_month='1', hour=2, minute=0),  # 2 AM on 1st of month
        },
        # Health check every 10 minutes
        'celery-health-check': {
            'task': 'app.tasks.celery_health_check',
            'schedule': crontab(minute='*/10'),
        },
    }
)

# Set the Django settings module
celery_app.conf.broker_connection_retry_on_startup = True

if __name__ == '__main__':
    celery_app.start()
