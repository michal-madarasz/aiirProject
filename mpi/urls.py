from django.urls import path

from . import views

urlpatterns = [
    path('task/', views.task, name='task'),
    path('document/', views.document, name='document'),
    path('document/delete/(?P<delete_id>\d+)/$', views.documentDelete, name='documentDelete'),
]