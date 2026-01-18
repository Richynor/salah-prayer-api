"""
Celery worker entry point for Railway.
"""
import os
from app.celery_app import celery_app

if __name__ == '__main__':
    # Start Celery worker
    worker = celery_app.Worker(
        include=['app.tasks'],
        loglevel=os.getenv('CELERY_LOG_LEVEL', 'info'),
        hostname=os.getenv('HOSTNAME', 'worker@%h'),
        queues=['default', 'celery'],
        pool='solo'  # Use 'solo' for Railway compatibility
    )
    worker.start()
