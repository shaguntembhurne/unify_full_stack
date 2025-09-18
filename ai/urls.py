from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('chat/', views.chat_assistant, name='chat'),
    path('news/summary/today/', views.news_summary_today, name='news_summary_today'),
    path('news/qa/today/', views.news_qa_today, name='news_qa_today'),
]