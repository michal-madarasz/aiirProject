from django.urls import path

from . import views

urlpatterns = [
    path('task/', views.task, name='task'),
    path('task/delete/<int:delete_id>', views.taskDelete, name='taskDelete'),
    path('document/', views.document, name='document'),
    path('document/delete/<int:delete_id>', views.documentDelete, name='documentDelete'),
    path('result/', views.resultDocument, name='resultDocument'),
    path('image/<int:id>', views.showimage, name='image'),
]