from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.projects_home, name='home'),
    path('create/', views.project_create, name='create'),
    path('<int:project_id>/join/', views.project_join, name='join'),
]
