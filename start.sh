#!/bin/bash
# Start script for Salah Prayer API

set -e

# Wait for Redis to be ready
if [ -n "$REDIS_URL" ]; then
    echo "Waiting for Redis..."
    timeout 30 bash -c 'until curl -s ${REDIS_URL/redis:/http:}/ping 2>/dev/null | grep -q "PONG"; do sleep 1; done'
fi

# Wait for PostgreSQL to be ready
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for PostgreSQL..."
    timeout 30 bash -c 'until pg_isready -h ${DATABASE_URL//*@/} -p 5432 2>/dev/null; do sleep 1; done'
fi

# Initialize database
python -c "from app.database import db; db.init_db()"

# Start the appropriate service based on command
case "$1" in
    "web")
        echo "Starting FastAPI server..."
        exec uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000} --workers=2 --timeout-keep-alive=30 --log-level=info
        ;;
    "worker")
        echo "Starting Celery worker..."
        exec python -m app.worker
        ;;
    "beat")
        echo "Starting Celery beat scheduler..."
        exec python -m app.beat
        ;;
    "flower")
        echo "Starting Flower monitoring..."
        exec python -m app.flower
        ;;
    *)
        echo "Usage: $0 {web|worker|beat|flower}"
        exit 1
        ;;
esac
