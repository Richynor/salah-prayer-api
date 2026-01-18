web: uvicorn api.main:app --host=0.0.0.0 --port=${PORT:-8000} --workers=${WEB_CONCURRENCY:-2}
worker: celery -A tasks.monthly_calculator worker --loglevel=info
beat: celery -A tasks.monthly_calculator beat --loglevel=info
flower: celery -A tasks.monthly_calculator flower --port=5555
