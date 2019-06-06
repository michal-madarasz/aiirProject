from django.urls import path

from . import views

urlpatterns = [
    path('task/', views.task, name='task'),
    path('document/', views.document, name='document'),
    path('document/delete/<int:delete_id>', views.documentDelete, name='documentDelete'),
]