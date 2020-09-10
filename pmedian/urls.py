from django.urls import path

from . import views

urlpatterns = [
    path('extract-csv', views.extract_csv, name='csv_extraction'),
    path('create-task', views.create_task, name='create_task'),
    path('get-task', views.get_task, name='get_task'),
    path('get-all-tasks', views.get_all_tasks, name='get_all_tasks')
    ]
