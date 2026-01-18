web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000} --workers=2 --timeout-keep-alive=30
worker: celery -A tasks.monthly_calculator worker --loglevel=info
beat: celery -A tasks.monthly_calculator beat --loglevel=info
flower: celery -A tasks.monthly_calculator flower --port=5555
