#!/bin/bash
# Start script for Railway deployment

echo "Starting DSP Eco Tracker backend..."
echo "PORT: $PORT"

# Start gunicorn with the Railway PORT
exec gunicorn main:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300