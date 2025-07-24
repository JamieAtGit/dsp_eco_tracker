#!/bin/bash
# Start script for Railway deployment

echo "Starting DSP Eco Tracker backend..."
echo "PORT: ${PORT:-5000}"
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"

# Set default port if not provided
export PORT=${PORT:-5000}

# Add current directory to Python path
export PYTHONPATH=/app:$PYTHONPATH

# Start gunicorn with the Railway PORT
echo "Starting gunicorn on port $PORT..."
exec gunicorn main:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --log-level info