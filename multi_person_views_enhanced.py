"""
Improved Multi-Person Dashboard
Better output formatting and data organization
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from .models import MultiPersonActivity, PersonActivity, Activity, Environment
import json


@login_required
def multi_person_dashboard(request):
    """
    Enhanced multi-person dashboard with comprehensive activity data
    """
    environments = Environment.objects.filter(is_active=True)
    
    # Get multi-person activities from the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    multi_activities = MultiPersonActivity.objects.filter(
        timestamp__gte=one_hour_ago
    ).select_related('environment').prefetch_related('personactivity_set').order_by('-timestamp')
    
    # Get individual pose-based detections
    person_activities = PersonActivity.objects.filter(
        timestamp__gte=one_hour_ago
    ).select_related('user', 'multi_activity__environment').order_by('-timestamp')
    
    # Get activity distribution data
    activity_dist = {}
    for pa in person_activities:
        activity_dist[pa.activity_type] = activity_dist.get(pa.activity_type, 0) + 1
    
    # Group activities by environment
    env_activities = {}
    for env in environments:
        env_activities[env.id] = {
            'name': env.name,
            'multi_count': multi_activities.filter(environment=env).count(),
            'person_count': person_activities.filter(multi_activity__environment=env).count(),
        }
    
    # Get activity timeline data (last 12 hours)
    twelve_hours_ago = timezone.now() - timedelta(hours=12)
    recent_activities = Activity.objects.filter(
        timestamp__gte=twelve_hours_ago
    ).order_by('timestamp')
    
    # Aggregate timeline by hour
    timeline_data = {}
    for activity in recent_activities:
        hour_key = activity.timestamp.strftime('%H:%M')
        timeline_data[hour_key] = timeline_data.get(hour_key, 0) + 1
    
    context = {
        'environments': environments,
        'multi_activities': multi_activities,
        'person_activities': person_activities,
        'activity_distribution': json.dumps(activity_dist),
        'environment_activities': json.dumps(env_activities),
        'timeline_data': json.dumps(timeline_data),
        'total_multi_activities': multi_activities.count(),
        'total_persons_detected': person_activities.count(),
    }
    
    return render(request, 'activities/multi_person_dashboard.html', context)


@login_required
def get_activity_summary(request):
    """
    JSON API endpoint for activity summary statistics
    """
    # Time windows
    one_hour_ago = timezone.now() - timedelta(hours=1)
    one_day_ago = timezone.now() - timedelta(days=1)
    
    # Count multi-person activities
    multi_hour = MultiPersonActivity.objects.filter(timestamp__gte=one_hour_ago).count()
    multi_day = MultiPersonActivity.objects.filter(timestamp__gte=one_day_ago).count()
    
    # Count person activities by type
    person_activities = PersonActivity.objects.filter(timestamp__gte=one_hour_ago)
    activity_types = {}
    for pa in person_activities:
        activity_types[pa.activity_type] = activity_types.get(pa.activity_type, 0) + 1
    
    # Average confidence
    avg_confidence = 0
    if person_activities.exists():
        avg_confidence = round(
            sum(pa.confidence_score for pa in person_activities) / person_activities.count(),
            1
        )
    
    # High confidence (>85%) activities
    high_confidence = person_activities.filter(confidence_score__gt=85).count()
    
    return JsonResponse({
        'summary': {
            'multi_activities_last_hour': multi_hour,
            'multi_activities_last_day': multi_day,
            'person_activities_last_hour': person_activities.count(),
            'activity_types': activity_types,
            'average_confidence': avg_confidence,
            'high_confidence_detections': high_confidence,
        },
        'success': True
    })


@login_required
def get_detailed_activity(request, activity_id):
    """
    Get detailed information about a specific multi-person activity
    """
    try:
        multi_activity = MultiPersonActivity.objects.get(id=activity_id)
        persons = multi_activity.personactivity_set.all()
        
        # Build detailed response
        persons_data = []
        for person in persons:
            pose_data = person.pose if person.pose else {}
            
            person_info = {
                'id': person.id,
                'activity': person.activity_type,
                'confidence': person.confidence_score,
                'location': person.location,
                'user': {
                    'name': person.user.get_full_name() if person.user else 'Unidentified',
                    'username': person.user.username if person.user else 'Unknown',
                } if person.user else None,
                'pose_available': bool(pose_data.get('keypoints')),
                'timestamp': person.timestamp.isoformat(),
            }
            persons_data.append(person_info)
        
        return JsonResponse({
            'success': True,
            'activity': {
                'id': multi_activity.id,
                'environment': multi_activity.environment.name,
                'timestamp': multi_activity.timestamp.isoformat(),
                'persons_count': persons.count(),
                'persons': persons_data,
            }
        })
    except MultiPersonActivity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Activity not found'}, status=404)


@login_required
def export_activity_report(request):
    """
    Export activity data as JSON for external use
    """
    # Get filters from request
    hours = int(request.GET.get('hours', 24))
    activity_type = request.GET.get('type', None)
    
    # Build query
    time_window = timezone.now() - timedelta(hours=hours)
    query = PersonActivity.objects.filter(timestamp__gte=time_window)
    
    if activity_type:
        query = query.filter(activity_type=activity_type)
    
    # Group and aggregate
    activities_by_type = {}
    environments_data = {}
    
    for pa in query:
        # By type
        if pa.activity_type not in activities_by_type:
            activities_by_type[pa.activity_type] = {
                'count': 0,
                'avg_confidence': [],
                'total_confidence': 0,
            }
        activities_by_type[pa.activity_type]['count'] += 1
        activities_by_type[pa.activity_type]['avg_confidence'].append(pa.confidence_score)
        activities_by_type[pa.activity_type]['total_confidence'] += pa.confidence_score
        
        # By environment
        env_name = pa.multi_activity.environment.name if pa.multi_activity else 'Unknown'
        if env_name not in environments_data:
            environments_data[env_name] = {'count': 0, 'activities': {}}
        environments_data[env_name]['count'] += 1
        
        if pa.activity_type not in environments_data[env_name]['activities']:
            environments_data[env_name]['activities'][pa.activity_type] = 0
        environments_data[env_name]['activities'][pa.activity_type] += 1
    
    # Calculate averages
    for activity_type, data in activities_by_type.items():
        if data['avg_confidence']:
            data['average_confidence'] = round(
                data['total_confidence'] / len(data['avg_confidence']), 1
            )
        del data['avg_confidence']
        del data['total_confidence']
    
    return JsonResponse({
        'success': True,
        'report': {
            'time_window_hours': hours,
            'total_activities': query.count(),
            'by_activity_type': activities_by_type,
            'by_environment': environments_data,
            'generated_at': timezone.now().isoformat(),
        }
    })
