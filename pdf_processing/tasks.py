import os
import logging
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import PDFDocument, ProcessingTask
import PyPDF2
import pdfplumber
from io import BytesIO

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_pdf_document(self, document_id):
    """
    Celery task to process a PDF document and extract text and metadata
    """
    try:
        # Get the document
        document = PDFDocument.objects.get(id=document_id)
        
        # Update document status to processing
        document.processing_status = 'processing'
        document.processing_started_at = timezone.now()
        document.save()
        
        # Create task tracking record
        task_record = ProcessingTask.objects.create(
            document=document,
            task_id=self.request.id,
            task_name='process_pdf_document',
            status='PROCESSING'
        )
        
        # Get file path
        file_path = document.file.path
        
        # Extract text and metadata
        extracted_data = extract_pdf_content(file_path)
        
        # Update document with extracted data
        document.extracted_text = extracted_data['text']
        document.page_count = extracted_data['page_count']
        document.metadata = extracted_data['metadata']
        document.processing_status = 'completed'
        document.processing_completed_at = timezone.now()
        document.save()
        
        # Update task record
        task_record.status = 'SUCCESS'
        task_record.result = {
            'page_count': extracted_data['page_count'],
            'text_length': len(extracted_data['text']),
            'processing_time': str(timezone.now() - document.processing_started_at)
        }
        task_record.save()
        
        logger.info(f"Successfully processed PDF document: {document.title}")
        return {
            'status': 'success',
            'document_id': str(document_id),
            'page_count': extracted_data['page_count'],
            'text_length': len(extracted_data['text'])
        }
        
    except PDFDocument.DoesNotExist:
        error_msg = f"PDF document with id {document_id} not found"
        logger.error(error_msg)
        return {'status': 'error', 'message': error_msg}
        
    except Exception as e:
        error_msg = f"Error processing PDF document: {str(e)}"
        logger.error(error_msg)
        
        # Update document status to failed
        try:
            document = PDFDocument.objects.get(id=document_id)
            document.processing_status = 'failed'
            document.error_message = error_msg
            document.save()
            
            # Update task record
            task_record = ProcessingTask.objects.get(task_id=self.request.id)
            task_record.status = 'FAILURE'
            task_record.error = error_msg
            task_record.save()
        except:
            pass
            
        return {'status': 'error', 'message': error_msg}


def extract_pdf_content(file_path):
    """
    Extract text, page count, and metadata from PDF file
    """
    extracted_data = {
        'text': '',
        'page_count': 0,
        'metadata': {}
    }
    
    try:
        # Method 1: Using pdfplumber (better for text extraction)
        with pdfplumber.open(file_path) as pdf:
            extracted_data['page_count'] = len(pdf.pages)
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
            
            extracted_data['text'] = '\n\n'.join(text_parts)
            
            # Extract metadata
            if pdf.metadata:
                extracted_data['metadata'] = {
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'subject': pdf.metadata.get('Subject', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'producer': pdf.metadata.get('Producer', ''),
                    'creation_date': str(pdf.metadata.get('CreationDate', '')),
                    'modification_date': str(pdf.metadata.get('ModDate', ''))
                }
    
    except Exception as e:
        logger.warning(f"pdfplumber failed, trying PyPDF2: {str(e)}")
        
        # Fallback: Using PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                extracted_data['page_count'] = len(pdf_reader.pages)
                
                # Extract text from all pages
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                
                extracted_data['text'] = '\n\n'.join(text_parts)
                
                # Extract metadata
                if pdf_reader.metadata:
                    extracted_data['metadata'] = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                        'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
                    }
        except Exception as e2:
            logger.error(f"Both PDF extraction methods failed: {str(e2)}")
            raise e2
    
    return extracted_data


@shared_task
def cleanup_old_documents():
    """
    Periodic task to cleanup old processed documents
    """
    from datetime import timedelta
    
    # Delete documents older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    old_documents = PDFDocument.objects.filter(
        upload_date__lt=cutoff_date,
        processing_status='completed'
    )
    
    count = 0
    for document in old_documents:
        # Delete the file from filesystem
        if document.file and os.path.exists(document.file.path):
            os.remove(document.file.path)
        
        # Delete the database record
        document.delete()
        count += 1
    
    logger.info(f"Cleaned up {count} old documents")
    return f"Cleaned up {count} old documents"

