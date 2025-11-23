# Quick Setup Instructions

> 📖 **For comprehensive documentation, see [README.md](README.md)**

This is a quick reference guide for setting up the Invoice Processor. For detailed information about features, API endpoints, troubleshooting, and more, please refer to the main README.md file.

## Prerequisites

1. **Python 3.8+**
2. **RabbitMQ Server**

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

### 1. Clone and Navigate to Project

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

### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start Django Development Server

```bash
python manage.py runserver
```

The server will be available at `http://localhost:8000`

### 7. Start Celery Services

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

## Quick Start Checklist

- [ ] RabbitMQ installed and running
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Django server running (`python manage.py runserver`)
- [ ] Celery worker running (see options above)
- [ ] Celery beat running (optional, for periodic tasks)

## Quick API Test

Test the API with a sample upload:

```bash
curl -X POST http://localhost:8000/api/pdf/upload/ \
  -F "file=@/path/to/your/document.pdf" \
  -F "title=Test Document"
```

## Next Steps

- 📖 See [README.md](README.md) for complete API documentation
- 📖 See [README.md](README.md) for detailed monitoring instructions
- 📖 See [README.md](README.md) for troubleshooting guide

## Troubleshooting

For detailed troubleshooting information, see the [Troubleshooting section in README.md](README.md#troubleshooting).

### Quick Fixes:

1. **RabbitMQ Connection Error**

   - Ensure RabbitMQ is running: `brew services list | grep rabbitmq` (macOS) or `sudo systemctl status rabbitmq-server` (Linux)
   - Check if port 5672 is available: `lsof -i :5672`

2. **Celery Worker Not Starting**

   - Verify RabbitMQ is running
   - Check Django settings: `python manage.py check`

3. **Import Errors**

   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Database Errors**
   - Run migrations: `python manage.py migrate`

For more detailed troubleshooting, monitoring, and API documentation, please refer to [README.md](README.md).
