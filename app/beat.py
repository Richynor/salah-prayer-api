"""
Celery beat scheduler entry point for Railway.
"""
import os
from app.celery_app import celery_app

if __name__ == '__main__':
    # Start Celery beat scheduler
    beat = celery_app.Beat(
        loglevel=os.getenv('CELERY_LOG_LEVEL', 'info'),
        scheduler='celery.beat:PersistentScheduler'
    )
    beat.run()
