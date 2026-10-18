from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('real-time/', views.real_time_monitoring, name='real_time'),
    path('stream-predict/', views.predict_activity, name='predict_activity'),
    path('history/', views.activity_history, name='history'),
    path('multi-person/', views.multi_person_view, name='multi_person'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('api/activities/', views.get_activities, name='get_activities'),
    path('api/distribution/', views.get_distribution, name='get_distribution'),
    path('pose-predict/', views.pose_predict, name='pose_predict'),
]