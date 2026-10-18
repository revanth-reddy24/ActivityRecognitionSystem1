from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('reports/', views.activity_reports, name='activity_reports'),
    path('system-config/', views.system_config, name='system_config'),
    path('model-management/', views.model_management, name='model_management'),
    path('environments/', views.environment_management, name='environment_management'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
]