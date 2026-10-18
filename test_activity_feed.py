#!/usr/bin/env python
"""
Test the activity feed AJAX endpoint to ensure predictions show up.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from activities.models import Activity, Environment
import json

def test_activity_feed():
    """Test that get_activities AJAX endpoint returns saved predictions"""
    print("\n" + "="*60)
    print("Testing Activity Feed AJAX Endpoint")
    print("="*60)
    
    # Use the test user we created earlier
    print("\n1. Getting test user...")
    CustomUser = get_user_model()
    user = CustomUser.objects.get(username='test_camera_user')
    print(f"   ✓ Found user: {user.username}")
    
    # Check activities in DB
    print("\n2. Checking activities in database...")
    activities = Activity.objects.filter(user=user).order_by('-timestamp')
    print(f"   Total activities: {activities.count()}")
    for activity in activities:
        print(f"   - {activity.activity_type} ({activity.confidence_score}%) @ {activity.location}")
    
    # Test AJAX endpoint
    print("\n3. Testing GET /activities/api/activities/ endpoint...")
    client = Client()
    client.force_login(user)
    
    response = client.get(
        '/activities/api/activities/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"   Response Status: {response.status_code}")
    data = json.loads(response.content)
    print(f"   Activities in response: {len(data['activities'])}")
    
    if data['activities']:
        print("   ✓ Activities returned by AJAX endpoint:")
        for activity in data['activities']:
            print(f"      - {activity['activity_type']} ({activity['confidence_score']}%) @ {activity['location']}")
    else:
        print("   ✗ No activities returned!")
        return False
    
    print("\n" + "="*60)
    print("✓ TEST PASSED: Activity feed AJAX is working!")
    print("="*60)
    return True

if __name__ == '__main__':
    try:
        success = test_activity_feed()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
