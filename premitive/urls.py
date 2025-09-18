from django.urls import path
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'premitive'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('auth/', views.auth_page, name='auth'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('notifications/dropdown/', views.notifications_dropdown, name='notifications_dropdown'),
    path('notifications/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),
    path('calendar/', TemplateView.as_view(template_name='unify_calender.html'), name='calendar'),
    path('analytics/teachers/', TemplateView.as_view(template_name='teachers_analytics.html'), name='teachers_analytics'),
    path('signup/', RedirectView.as_view(pattern_name='premitive:auth', permanent=False), name='signup'),
    path('login/', RedirectView.as_view(pattern_name='premitive:auth', permanent=False), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
