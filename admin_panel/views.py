from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
from users.models import CustomUser, UserProfile, Feedback
from activities.models import Activity, Environment
from notifications.models import Notification, NotificationRule
from .models import SystemConfig, ActivityModel, AuditLog, SystemPerformance
from .forms import (SystemConfigForm, ActivityModelForm, 
                   NotificationRuleForm, UserManagementForm, EnvironmentForm)

def admin_required(view_func):
    """Decorator to ensure user is admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Allow users who are marked as admin in user_type OR Django staff/superuser
        if not request.user.is_authenticated or not (
            getattr(request.user, 'user_type', None) == 'admin' or
            request.user.is_staff or
            request.user.is_superuser
        ):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('users:login')
        return view_func(request, *args, **kwargs)

    return wrapper

@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    # Basic statistics
    total_users = CustomUser.objects.filter(user_type='user').count()
    total_admins = CustomUser.objects.filter(user_type='admin').count()
    total_activities = Activity.objects.count()
    total_feedbacks = Feedback.objects.count()
    
    # Recent activities
    recent_activities = Activity.objects.select_related('user', 'environment').order_by('-timestamp')[:10]
    
    # System performance (mock data - in real app, this would come from monitoring)
    system_performance = {
        'cpu_usage': 45.2,
        'memory_usage': 67.8,
        'disk_usage': 23.4,
        'active_users': CustomUser.objects.filter(last_login__gte=datetime.now() - timedelta(hours=1)).count(),
    }
    
    # Activity distribution
    activity_distribution = Activity.objects.values('activity_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_users': total_users,
        'total_admins': total_admins,
        'total_activities': total_activities,
        'total_feedbacks': total_feedbacks,
        'recent_activities': recent_activities,
        'system_performance': system_performance,
        'activity_distribution': activity_distribution,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@admin_required
def user_management(request):
    """User management view for admins"""
    users = CustomUser.objects.all().order_by('-date_joined')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(CustomUser, id=user_id)
        
        if action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f'User {user.username} has been deactivated.')
        elif action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f'User {user.username} has been activated.')
        elif action == 'delete':
            username = user.username
            user.delete()
            messages.success(request, f'User {username} has been deleted.')
        
        return redirect('admin_panel:user_management')
    
    return render(request, 'admin_panel/user_management.html', {'users': users})

@login_required
@admin_required
def user_detail(request, user_id):
    """Detailed view of a specific user"""
    user = get_object_or_404(CustomUser, id=user_id)
    user_activities = Activity.objects.filter(user=user).order_by('-timestamp')[:20]
    user_feedbacks = Feedback.objects.filter(user=user).order_by('-created_at')[:10]
    
    context = {
        'user_detail': user,
        'user_activities': user_activities,
        'user_feedbacks': user_feedbacks,
    }
    return render(request, 'admin_panel/user_detail.html', context)

@login_required
@admin_required
def activity_reports(request):
    """Activity reports and analytics"""
    # Date range filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    activities = Activity.objects.all()
    
    if start_date:
        activities = activities.filter(timestamp__gte=start_date)
    if end_date:
        activities = activities.filter(timestamp__lte=end_date)
    
    # Statistics
    total_activities = activities.count()
    unique_users = activities.values('user').distinct().count()
    activity_by_type = activities.values('activity_type').annotate(count=Count('id'))
    
    # Time-based analytics
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    monthly_activities = Activity.objects.filter(
        timestamp__gte=week_ago
    ).extra({'date': "date(timestamp)"}).values('date').annotate(count=Count('id'))
    
    context = {
        'total_activities': total_activities,
        'unique_users': unique_users,
        'activity_by_type': activity_by_type,
        'monthly_activities': monthly_activities,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin_panel/activity_reports.html', context)

@login_required
@admin_required
def system_config(request):
    """System configuration management"""
    configs = SystemConfig.objects.all()
    
    if request.method == 'POST':
        form = SystemConfigForm(request.POST)
        if form.is_valid():
            config = form.save(commit=False)
            config.updated_by = request.user
            config.save()
            messages.success(request, 'Configuration updated successfully.')
            return redirect('admin_panel:system_config')
    else:
        form = SystemConfigForm()
    
    context = {
        'configs': configs,
        'form': form,
    }
    return render(request, 'admin_panel/system_config.html', context)

@login_required
@admin_required
def model_management(request):
    """Activity recognition model management"""
    models = ActivityModel.objects.all()
    
    if request.method == 'POST':
        form = ActivityModelForm(request.POST, request.FILES)
        if form.is_valid():
            model = form.save()
            messages.success(request, f'Model {model.name} has been added.')
            return redirect('admin_panel:model_management')
    else:
        form = ActivityModelForm()
    
    context = {
        'models': models,
        'form': form,
    }
    return render(request, 'admin_panel/model_management.html', context)

@login_required
@admin_required
def environment_management(request):
    """Environment management"""
    environments = Environment.objects.all()
    
    if request.method == 'POST':
        form = EnvironmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Environment added successfully.')
            return redirect('admin_panel:environment_management')
    else:
        form = EnvironmentForm()
    
    context = {
        'environments': environments,
        'form': form,
    }
    return render(request, 'admin_panel/environment_management.html', context)

@login_required
@admin_required
def audit_logs(request):
    """System audit logs"""
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:100]
    return render(request, 'admin_panel/audit_logs.html', {'logs': logs})