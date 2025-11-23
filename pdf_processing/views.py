import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PDFDocument, ProcessingTask
from .tasks import process_pdf_document
import json


@api_view(['POST'])
def upload_pdf(request):
    """
    Upload a PDF file and trigger processing
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    title = request.data.get('title', file.name)
    
    # Validate file type
    if not file.name.lower().endswith('.pdf'):
        return Response(
            {'error': 'Only PDF files are allowed'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        return Response(
            {'error': f'File size exceeds {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB limit'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create PDF document record
        document = PDFDocument.objects.create(
            title=title,
            file=file,
            file_size=file.size
        )
        
        # Trigger Celery task
        task = process_pdf_document.delay(str(document.id))
        
        return Response({
            'message': 'PDF uploaded successfully',
            'document_id': str(document.id),
            'task_id': task.id,
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Upload failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def document_status(request, document_id):
    """
    Get the processing status of a document
    """
    try:
        document = get_object_or_404(PDFDocument, id=document_id)
        
        # Get latest task for this document
        latest_task = document.tasks.order_by('-created_at').first()
        
        response_data = {
            'document_id': str(document.id),
            'title': document.title,
            'processing_status': document.processing_status,
            'upload_date': document.upload_date,
            'processing_started_at': document.processing_started_at,
            'processing_completed_at': document.processing_completed_at,
            'error_message': document.error_message,
            'page_count': document.page_count,
            'file_size': document.file_size,
        }
        
        if latest_task:
            response_data['task_id'] = latest_task.task_id
            response_data['task_status'] = latest_task.status
            response_data['task_created_at'] = latest_task.created_at
            response_data['task_updated_at'] = latest_task.updated_at
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get document status: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def document_content(request, document_id):
    """
    Get the extracted content of a processed document
    """
    try:
        document = get_object_or_404(PDFDocument, id=document_id)
        
        if document.processing_status != 'completed':
            return Response(
                {'error': 'Document processing not completed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'document_id': str(document.id),
            'title': document.title,
            'extracted_text': document.extracted_text,
            'page_count': document.page_count,
            'metadata': document.metadata,
            'processing_completed_at': document.processing_completed_at
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get document content: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def document_list(request):
    """
    List all documents with their status
    """
    try:
        documents = PDFDocument.objects.all()
        
        document_list = []
        for doc in documents:
            latest_task = doc.tasks.order_by('-created_at').first()
            
            document_data = {
                'document_id': str(doc.id),
                'title': doc.title,
                'processing_status': doc.processing_status,
                'upload_date': doc.upload_date,
                'file_size': doc.file_size,
                'page_count': doc.page_count,
                'error_message': doc.error_message,
            }
            
            if latest_task:
                document_data['task_id'] = latest_task.task_id
                document_data['task_status'] = latest_task.status
            
            document_list.append(document_data)
        
        return Response({
            'documents': document_list,
            'total_count': len(document_list)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to list documents: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_document(request, document_id):
    """
    Delete a document and its associated file
    """
    try:
        document = get_object_or_404(PDFDocument, id=document_id)
        
        # Delete the file from filesystem
        if document.file and os.path.exists(document.file.path):
            os.remove(document.file.path)
        
        # Delete the database record
        document.delete()
        
        return Response({
            'message': 'Document deleted successfully'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to delete document: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def task_status(request, task_id):
    """
    Get the status of a specific Celery task
    """
    try:
        task_record = get_object_or_404(ProcessingTask, task_id=task_id)
        
        return Response({
            'task_id': task_record.task_id,
            'task_name': task_record.task_name,
            'status': task_record.status,
            'created_at': task_record.created_at,
            'updated_at': task_record.updated_at,
            'result': task_record.result,
            'error': task_record.error,
            'document_id': str(task_record.document.id),
            'document_title': task_record.document.title
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get task status: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
