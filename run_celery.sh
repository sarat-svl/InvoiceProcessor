#!/bin/bash

# Script to run Celery worker and beat scheduler
# Make sure RabbitMQ is running before executing this script

echo "Starting Celery services..."

# Activate virtual environment
source venv/bin/activate

# Start Celery worker in background
echo "Starting Celery worker..."
python start_celery_worker.py &

# Start Celery beat scheduler in background
echo "Starting Celery beat scheduler..."
python start_celery_beat.py &

echo "Celery services started!"
echo "Worker PID: $!"
echo "Beat PID: $!"

# Wait for user input to stop services
echo "Press Ctrl+C to stop all services"
wait

