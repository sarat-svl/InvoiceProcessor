# Invoice Processor

A Django-based PDF processing system that uses Celery for asynchronous task processing and RabbitMQ as the message broker. This application allows you to upload PDF documents, extract text and metadata, and track processing status through a RESTful API.

## Features

- 📄 **PDF Upload & Processing**: Upload PDF files and automatically extract text and metadata
- ⚡ **Asynchronous Processing**: Uses Celery for background task processing
- 🔄 **Task Tracking**: Monitor document processing status and task execution
- 📊 **Metadata Extraction**: Extracts document metadata (title, author, creation date, etc.)
- 🗂️ **Document Management**: List, view, and delete processed documents
- 🔍 **Multiple PDF Libraries**: Uses pdfplumber and PyPDF2 for robust text extraction
- 🧹 **Automatic Cleanup**: Periodic task to clean up old documents

## Tech Stack

- **Backend Framework**: Django 5.2.7
- **API**: Django REST Framework
- **Task Queue**: Celery 5.5.3
- **Message Broker**: RabbitMQ
- **PDF Processing**: pdfplumber, PyPDF2, pdfminer.six
- **Database**: SQLite (default, can be configured for PostgreSQL/MySQL)

## Prerequisites

- Python 3.8 or higher
- RabbitMQ Server
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd InvoiceProcessor
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Start RabbitMQ

#### On macOS (using Homebrew):

```bash
brew install rabbitmq
brew services start rabbitmq
```

#### On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

#### On Windows:

1. Download RabbitMQ installer from: https://www.rabbitmq.com/download.html
2. Install and start the service
3. Or use Docker: `docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`

### 5. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Running the Application

### 1. Start Django Development Server

```bash
python manage.py runserver
```

The server will be available at `http://localhost:8000`

### 2. Start Celery Services

You have three options to start Celery:

#### Option A: Using the provided script

```bash
./run_celery.sh
```

#### Option B: Using Python scripts

```bash
# Terminal 1: Start Celery Worker
python start_celery_worker.py

# Terminal 2: Start Celery Beat (for periodic tasks)
python start_celery_beat.py
```

#### Option C: Using Celery command directly

```bash
# Terminal 1: Start Celery Worker
# Note: Use --queues=pdf_processing to match the task routing configuration
celery -A invoice_processor worker --loglevel=info --concurrency=4 --queues=pdf_processing

# Terminal 2: Start Celery Beat
celery -A invoice_processor beat --loglevel=info
```

**Note**: The worker must listen to the `pdf_processing` queue to match the task routing configuration in `settings.py`. If using Option C, make sure to include `--queues=pdf_processing` in the command.

## API Endpoints

### Upload PDF

Upload a PDF file for processing.

```bash
curl -X POST http://localhost:8000/api/pdf/upload/ \
  -F "file=@/path/to/your/document.pdf" \
  -F "title=My Document"
```

**Response:**

```json
{
  "message": "PDF uploaded successfully",
  "document_id": "uuid-here",
  "task_id": "task-id-here",
  "status": "pending"
}
```

### Get Document Status

Check the processing status of a document.

```bash
curl http://localhost:8000/api/pdf/documents/{document_id}/status/
```

**Response:**

```json
{
  "document_id": "uuid-here",
  "title": "My Document",
  "processing_status": "completed",
  "upload_date": "2024-01-01T12:00:00Z",
  "processing_started_at": "2024-01-01T12:00:01Z",
  "processing_completed_at": "2024-01-01T12:00:05Z",
  "page_count": 10,
  "file_size": 1024000,
  "task_id": "task-id-here",
  "task_status": "SUCCESS"
}
```

### Get Document Content

Retrieve the extracted text and metadata from a processed document.

```bash
curl http://localhost:8000/api/pdf/documents/{document_id}/content/
```

**Response:**

```json
{
  "document_id": "uuid-here",
  "title": "My Document",
  "extracted_text": "--- Page 1 ---\nDocument content here...",
  "page_count": 10,
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "creation_date": "2024-01-01"
  },
  "processing_completed_at": "2024-01-01T12:00:05Z"
}
```

### List All Documents

Get a list of all uploaded documents.

```bash
curl http://localhost:8000/api/pdf/documents/
```

**Response:**

```json
{
  "documents": [
    {
      "document_id": "uuid-here",
      "title": "My Document",
      "processing_status": "completed",
      "upload_date": "2024-01-01T12:00:00Z",
      "file_size": 1024000,
      "page_count": 10
    }
  ],
  "total_count": 1
}
```

### Get Task Status

Check the status of a specific Celery task.

```bash
curl http://localhost:8000/api/pdf/tasks/{task_id}/status/
```

**Response:**

```json
{
  "task_id": "task-id-here",
  "task_name": "process_pdf_document",
  "status": "SUCCESS",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:05Z",
  "result": {
    "page_count": 10,
    "text_length": 5000
  },
  "document_id": "uuid-here",
  "document_title": "My Document"
}
```

### Delete Document

Delete a document and its associated file.

```bash
curl -X DELETE http://localhost:8000/api/pdf/documents/{document_id}/delete/
```

**Response:**

```json
{
  "message": "Document deleted successfully"
}
```

## Project Structure

```
InvoiceProcessor/
├── invoice_processor/          # Django project settings
│   ├── __init__.py
│   ├── celery.py              # Celery configuration
│   ├── settings.py            # Django settings with Celery config
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── pdf_processing/            # Main application
│   ├── models.py              # PDFDocument and ProcessingTask models
│   ├── tasks.py               # Celery tasks for PDF processing
│   ├── views.py               # API views
│   ├── urls.py                # App URL patterns
│   └── admin.py               # Django admin configuration
├── media/                     # Uploaded PDF files (created automatically)
│   └── pdfs/                  # PDF storage directory
├── start_celery_worker.py    # Worker startup script
├── start_celery_beat.py      # Beat scheduler script
├── run_celery.sh             # Combined startup script
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Monitoring

### RabbitMQ Management Interface

Access the RabbitMQ management interface at:

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

## Configuration

### File Upload Settings

The maximum file upload size is configured in `invoice_processor/settings.py`:

```python
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
```

### Celery Configuration

Celery settings are configured in `invoice_processor/settings.py`:

```python
CELERY_BROKER_URL = "amqp://localhost:5672"
CELERY_RESULT_BACKEND = "rpc://"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Task routing - send PDF processing tasks to pdf_processing queue
CELERY_TASK_ROUTES = {
    "pdf_processing.tasks.*": {"queue": "pdf_processing"},
}
```

**Important**: The worker listens to the `pdf_processing` queue. Tasks are automatically routed to this queue via the `CELERY_TASK_ROUTES` configuration. This ensures proper task distribution and allows for scalable, organized task processing.

## Troubleshooting

### Common Issues

1. **RabbitMQ Connection Error**

   - Ensure RabbitMQ is running: `brew services list | grep rabbitmq` (macOS)
   - Check if port 5672 is available: `lsof -i :5672`
   - Verify RabbitMQ is accessible: `rabbitmqctl status`

2. **Celery Worker Not Starting**

   - Check Django settings: `python manage.py check`
   - Verify Celery configuration: `python -c "from invoice_processor.celery import app; print(app.conf.broker_url)"`
   - Ensure RabbitMQ is running and accessible

3. **PDF Processing Fails**

   - Check file permissions in `media/` directory
   - Verify PDF libraries are installed: `pip list | grep -E "(PyPDF2|pdfplumber)"`
   - Check Celery worker logs for detailed error messages

4. **Tasks Stuck in Pending Status**

   - **Queue Mismatch**: Ensure tasks are being routed to the correct queue. The worker listens to `pdf_processing` queue.
   - Check RabbitMQ queues: `rabbitmqctl list_queues name messages`
   - Verify task routing is configured in `settings.py`: `CELERY_TASK_ROUTES`
   - Ensure Celery worker is listening to the correct queue: Check `start_celery_worker.py` for `--queues=pdf_processing`
   - If tasks are stuck, restart the Celery worker after verifying configuration

5. **Database Errors**
   - Run migrations: `python manage.py migrate`
   - Check database connection: `python manage.py dbshell`
   - Verify database file permissions (for SQLite)

### Logs

- **Django logs**: Check terminal running `python manage.py runserver`
- **Celery logs**: Check terminal running Celery worker
- **RabbitMQ logs**: Check system logs or RabbitMQ management interface

## Development

### Running Tests

```bash
python manage.py test
```
