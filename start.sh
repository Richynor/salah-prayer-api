#!/bin/bash
# Start script for Railway

# Set default port if not set
PORT=${PORT:-8000}

# Start the application
uvicorn app.main:app --host=0.0.0.0 --port=$PORT --workers=2
