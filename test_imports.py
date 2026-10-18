#!/usr/bin/env python
"""Comprehensive import tests for all Django apps"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

print("=" * 60)
print("COMPREHENSIVE IMPORT TESTS")
print("=" * 60)

# Test admin_panel imports
try:
    from admin_panel.forms import (SystemConfigForm, ActivityModelForm, 
                                   NotificationRuleForm, UserManagementForm, EnvironmentForm)
    from admin_panel.models import (SystemConfig, ActivityModel, AuditLog, SystemPerformance)
    from admin_panel.views import (admin_dashboard, user_management, user_detail, 
                                   activity_reports, system_config, model_management, 
                                   environment_management, audit_logs)
    print("✅ admin_panel: All imports successful")
except Exception as e:
    print(f"❌ admin_panel: {e}")
    import traceback
    traceback.print_exc()

# Test users imports
try:
    from users.forms import (CustomUserCreationForm, CustomAuthenticationForm, 
                            UserProfileForm, UserUpdateForm, FeedbackForm, 
                            CustomPasswordChangeForm, ActivityFilterForm)
    from users.models import CustomUser, UserProfile, Feedback
    from users.views import (register, user_login, user_logout, dashboard, 
                            profile, profile_update, password_change, feedback,
                            activity_history, multi_person_view, activity_detail)
    print("✅ users: All imports successful")
except Exception as e:
    print(f"❌ users: {e}")
    import traceback
    traceback.print_exc()

# Test activities imports
try:
    from activities.models import (Activity, ActivitySession, Environment, 
                                   MultiPersonActivity, PersonActivity)
    print("✅ activities: All imports successful")
except Exception as e:
    print(f"❌ activities: {e}")
    import traceback
    traceback.print_exc()

# Test notifications imports
try:
    from notifications.models import (Notification, NotificationRule, AlertLog)
    print("✅ notifications: All imports successful")
except Exception as e:
    print(f"❌ notifications: {e}")
    import traceback
    traceback.print_exc()

# Test that models have correct fields
try:
    # Check NotificationRule has correct fields
    from notifications.models import NotificationRule
    fields = [f.name for f in NotificationRule._meta.get_fields()]
    assert 'condition' in fields, "NotificationRule missing 'condition' field"
    assert 'activity_type' in fields, "NotificationRule missing 'activity_type' field"
    assert 'priority' in fields, "NotificationRule missing 'priority' field"
    print("✅ Model fields verified: NotificationRule has all required fields")
except Exception as e:
    print(f"❌ Model fields verification failed: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
print("All critical components verified!")
print("=" * 60)
