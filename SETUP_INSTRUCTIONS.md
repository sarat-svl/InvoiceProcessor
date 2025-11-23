# PDF Processing with Celery and RabbitMQ - Setup Instructions

## 🎉 System Status: READY TO USE!

✅ **RabbitMQ** is running on port 5672  
✅ **Django server** is running on port 8000  
✅ **Celery worker** is running and connected  
✅ **Database migrations** are applied  
✅ **All dependencies** are installed

## Prerequisites

1. **Python 3.8+** (already installed in your virtual environment)
2. **RabbitMQ Server** (✅ installed and running)

## RabbitMQ Installation and Setup

### On macOS (using Homebrew):

```bash
# Install RabbitMQ
brew install rabbitmq

# Start RabbitMQ service
brew services start rabbitmq

# Or start manually
rabbitmq-server
```

### On Ubuntu/Debian:

```bash
# Install RabbitMQ
sudo apt-get update
sudo apt-get install rabbitmq-server

# Start RabbitMQ service
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

### On Windows:

1. Download RabbitMQ installer from: https://www.rabbitmq.com/download.html
2. Install and start the service
3. Or use Docker: `docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`

## Project Setup

### 1. Activate Virtual Environment

```bash
cd /Users/saratchandra/Desktop/stuff/HLD/InvoiceProcessor
source venv/bin/activate
```

### 2. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 4. Start Django Development Server

```bash
python manage.py runserver
```

### 5. Start Celery Services

#### Option A: Using the provided script

```bash
./run_celery.sh
```

#### Option B: Manual startup

```bash
# Terminal 1: Start Celery Worker
python start_celery_worker.py

# Terminal 2: Start Celery Beat (for periodic tasks)
python start_celery_beat.py
```

#### Option C: Using Celery command directly

```bash
# Terminal 1: Start Celery Worker
celery -A invoice_processor worker --loglevel=info --concurrency=4

# Terminal 2: Start Celery Beat
celery -A invoice_processor beat --loglevel=info
```

## API Endpoints

Once everything is running, you can use these API endpoints:

### Upload PDF

```bash
curl -X POST http://localhost:8000/api/pdf/upload/ \
  -F "file=@/path/to/your/document.pdf" \
  -F "title=My Document"
```

### Check Document Status

```bash
curl http://localhost:8000/api/pdf/documents/{document_id}/status/
```

### Get Document Content

```bash
curl http://localhost:8000/api/pdf/documents/{document_id}/content/
```

### List All Documents

```bash
curl http://localhost:8000/api/pdf/documents/
```

### Check Task Status

```bash
curl http://localhost:8000/api/pdf/tasks/{task_id}/status/
```

### Delete Document

```bash
curl -X DELETE http://localhost:8000/api/pdf/documents/{document_id}/delete/
```

## Monitoring

### RabbitMQ Management Interface

- URL: http://localhost:15672
- Default username: `guest`
- Default password: `guest`

### Celery Monitoring

```bash
# Check active tasks
celery -A invoice_processor inspect active

# Check registered tasks
celery -A invoice_processor inspect registered

# Check worker stats
celery -A invoice_processor inspect stats
```

## File Structure

```
InvoiceProcessor/
├── invoice_processor/
│   ├── __init__.py
│   ├── celery.py          # Celery configuration
│   ├── settings.py        # Django settings with Celery config
│   └── urls.py           # URL routing
├── pdf_processing/
│   ├── models.py         # PDFDocument and ProcessingTask models
│   ├── tasks.py          # Celery tasks for PDF processing
│   ├── views.py          # API views
│   └── urls.py           # App URL patterns
├── start_celery_worker.py # Worker startup script
├── start_celery_beat.py   # Beat scheduler script
├── run_celery.sh         # Combined startup script
└── media/                # Uploaded PDF files (created automatically)
```

## Troubleshooting

### Common Issues:

1. **RabbitMQ Connection Error**

   - Ensure RabbitMQ is running: `brew services list | grep rabbitmq`
   - Check if port 5672 is available: `lsof -i :5672`

2. **Celery Worker Not Starting**

   - Check Django settings: `python manage.py check`
   - Verify Celery configuration: `python -c "from invoice_processor.celery import app; print(app.conf.broker_url)"`

3. **PDF Processing Fails**

   - Check file permissions in media/ directory
   - Verify PDF libraries are installed: `pip list | grep -E "(PyPDF2|pdfplumber)"`

4. **Database Errors**
   - Run migrations: `python manage.py migrate`
   - Check database connection: `python manage.py dbshell`

### Logs:

- Django logs: Check terminal running `python manage.py runserver`
- Celery logs: Check terminal running Celery worker
- RabbitMQ logs: Check system logs or RabbitMQ management interface

## Production Considerations

1. **Use a proper database** (PostgreSQL/MySQL) instead of SQLite
2. **Configure proper file storage** (AWS S3, etc.) for uploaded files
3. **Set up proper logging** and monitoring
4. **Use environment variables** for sensitive configuration
5. **Configure proper security settings** for production
6. **Set up Redis** as result backend for better performance
7. **Use Docker** for containerized deployment
