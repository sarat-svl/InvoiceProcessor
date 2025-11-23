#!/usr/bin/env python
"""
Script to start Celery beat scheduler for periodic tasks
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
    # Start Celery beat
    current_app.control.purge()  # Clear any existing tasks
    current_app.start(['beat', '--loglevel=info'])

