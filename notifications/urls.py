from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('mark-read/<int:pk>/', views.mark_read, name='mark_read'),
    path('settings/', views.notification_settings, name='settings'),
]