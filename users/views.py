from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from .models import CustomUser, UserProfile, Feedback
from .forms import (CustomUserCreationForm, CustomAuthenticationForm, 
                   UserProfileForm, UserUpdateForm, FeedbackForm, ActivityFilterForm)
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from activities.models import Activity, ActivitySession, MultiPersonActivity, Environment


def home(request):
    """Home page view - redirects to appropriate dashboard based on authentication"""
    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            return redirect('admin_panel:dashboard')
        else:
            return redirect('users:dashboard')
    else:
        return redirect('users:login')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'user'
            user.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('users:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                if user.user_type == 'admin':
                    return redirect('admin_panel:dashboard')
                else:
                    return redirect('users:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')

@login_required
def dashboard(request):
    if request.user.user_type == 'admin':
        return redirect('admin_panel:dashboard')
    
    # Get recent activities for the user
    recent_activities = request.user.activities.all()[:5]
    recent_notifications = request.user.notifications.filter(is_read=False)[:5]
    today_activities = request.user.activities.filter(timestamp__date=timezone.now().date())
    unread_notifications_count = request.user.notifications.filter(is_read=False).count()
    active_sessions = request.user.activitysession_set.filter(end_time__isnull=True)
    
    context = {
        'recent_activities': recent_activities,
        'recent_notifications': recent_notifications,
        'today_activities': today_activities,
        'unread_notifications_count': unread_notifications_count,
        'active_sessions': active_sessions,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'users/profile.html', {'profile': user_profile})

@login_required
def profile_update(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile_update.html', context)

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/password_change.html', {'form': form})

@login_required
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback_obj = form.save(commit=False)
            feedback_obj.user = request.user
            feedback_obj.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('users:dashboard')
    else:
        form = FeedbackForm()
    
    return render(request, 'users/feedback.html', {'form': form})




# ... existing views ...

@login_required
def activity_history(request):
    """Historical activity data view with filtering"""
    activities = Activity.objects.filter(user=request.user).order_by('-timestamp')
    
    form = ActivityFilterForm(request.GET or None)
    
    if form.is_valid():
        activity_type = form.cleaned_data.get('activity_type')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        environment = form.cleaned_data.get('environment')
        
        if activity_type:
            activities = activities.filter(activity_type=activity_type)
        if start_date:
            activities = activities.filter(timestamp__gte=start_date)
        if end_date:
            activities = activities.filter(timestamp__lte=end_date)
        if environment:
            activities = activities.filter(environment=environment)
    else:
        # Default: last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        activities = activities.filter(timestamp__gte=week_ago)
    
    # Pagination
    paginator = Paginator(activities, 20)  # 20 activities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'activities': page_obj,
        'page_obj': page_obj,
        'form': form,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'activities/history.html', context)

@login_required
def multi_person_view(request):
    """View for monitoring multiple people simultaneously"""
    environments = Environment.objects.filter(is_active=True)
    multi_activities = MultiPersonActivity.objects.filter(
        environment__in=environments,
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).order_by('-timestamp')
    
    context = {
        'environments': environments,
        'multi_activities': multi_activities,
    }
    return render(request, 'activities/multi_person.html', context)

@login_required
def activity_detail(request, activity_id):
    """Detailed view of a specific activity"""
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    
    # Get similar activities
    similar_activities = Activity.objects.filter(
        user=request.user,
        activity_type=activity.activity_type
    ).exclude(id=activity.id).order_by('-timestamp')[:5]
    
    context = {
        'activity': activity,
        'similar_activities': similar_activities,
    }
    return render(request, 'activities/activity_detail.html', context)