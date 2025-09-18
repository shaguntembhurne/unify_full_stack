from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='list'),
    path('create/', views.news_create, name='create'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('polls/create/', views.poll_create, name='poll_create'),
    path('polls/<int:poll_id>/vote/', views.poll_vote, name='poll_vote'),
    path('posts/<int:post_id>/like/', views.post_like, name='post_like'),
    path('posts/<int:post_id>/comments/', views.post_comment_list, name='post_comment_list'),
    path('posts/<int:post_id>/comments/create/', views.post_comment_create, name='post_comment_create'),
    path('posts/<int:post_id>/share/', views.post_share, name='post_share'),
]
