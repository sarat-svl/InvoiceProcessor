from django.db import models
from django.core.validators import FileExtensionValidator
import uuid


class PDFDocument(models.Model):
    """Model to store PDF document metadata and processing status"""
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='pdfs/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    file_size = models.BigIntegerField(help_text="File size in bytes")
    upload_date = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending'
    )
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Extracted content
    extracted_text = models.TextField(blank=True, null=True)
    page_count = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.title} ({self.processing_status})"


class ProcessingTask(models.Model):
    """Model to track Celery task execution"""
    
    document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='tasks')
    task_id = models.CharField(max_length=255, unique=True)
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    result = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task_name} - {self.document.title}"


