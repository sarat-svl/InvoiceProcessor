from django.urls import path
from . import views

urlpatterns = [
    # UI Routes
    path("", views.home, name="home"),
    path("document/<uuid:document_id>/", views.document_detail, name="document_detail"),
    # API Routes
    path("api/pdf/upload/", views.upload_pdf, name="upload_pdf"),
    path("api/pdf/documents/", views.document_list, name="document_list"),
    path(
        "api/pdf/documents/<uuid:document_id>/status/",
        views.document_status,
        name="document_status",
    ),
    path(
        "api/pdf/documents/<uuid:document_id>/content/",
        views.document_content,
        name="document_content",
    ),
    path(
        "api/pdf/documents/<uuid:document_id>/delete/",
        views.delete_document,
        name="delete_document",
    ),
    path("api/pdf/tasks/<str:task_id>/status/", views.task_status, name="task_status"),
]
