from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/<uuid:document_id>/status/', views.document_status, name='document_status'),
    path('documents/<uuid:document_id>/content/', views.document_content, name='document_content'),
    path('documents/<uuid:document_id>/delete/', views.delete_document, name='delete_document'),
    path('tasks/<str:task_id>/status/', views.task_status, name='task_status'),
]

