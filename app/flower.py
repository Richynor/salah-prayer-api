"""
Flower monitoring entry point.
"""
import os
from app.celery_app import celery_app

if __name__ == '__main__':
    # Start Flower monitoring
    from flower.app import Flower
    flower = Flower(
        capp=celery_app,
        address=os.getenv('FLOWER_HOST', '0.0.0.0'),
        port=int(os.getenv('FLOWER_PORT', 5555)),
        url_prefix=os.getenv('FLOWER_URL_PREFIX', ''),
        auth=os.getenv('FLOWER_AUTH', ''),
        basic_auth=os.getenv('FLOWER_BASIC_AUTH', '').split(',') if os.getenv('FLOWER_BASIC_AUTH') else None,
        max_tasks=os.getenv('FLOWER_MAX_TASKS', 10000),
        db=os.getenv('FLOWER_DB', 'flower.db'),
        persistent=os.getenv('FLOWER_PERSISTENT', False),
        broker_api=os.getenv('FLOWER_BROKER_API', ''),
        enable_events=os.getenv('FLOWER_ENABLE_EVENTS', True)
    )
    flower.start()
