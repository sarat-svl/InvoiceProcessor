#!/usr/bin/env python
"""
Script to start Celery worker for PDF processing
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_processor.settings')
django.setup()

from celery import current_app

if __name__ == '__main__':
    # Start Celery worker
    current_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--queues=pdf_processing'
    ])

