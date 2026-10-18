#!/usr/bin/env python
"""
Quick test script to verify the prediction endpoint saves activities correctly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from activities.models import Activity, Environment
from users.models import CustomUser
import json

def test_prediction_endpoint():
    """Test that predict_activity endpoint saves activities to DB"""
    print("\n" + "="*60)
    print("Testing Prediction Endpoint")
    print("="*60)
    
    # Create a test user
    print("\n1. Creating test user...")
    user, created = CustomUser.objects.get_or_create(
        username='test_camera_user',
        defaults={'email': 'test@test.com', 'user_type': 'user'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"   ✓ Created user: {user.username}")
    else:
        print(f"   ✓ User exists: {user.username}")
    
    # Create a test environment
    print("\n2. Creating test environment...")
    env, created = Environment.objects.get_or_create(
        name='Test Location',
        defaults={'address': '123 Test St', 'is_active': True}
    )
    print(f"   ✓ Environment: {env.name} (Active: {env.is_active})")
    
    # Get initial activity count
    print("\n3. Checking initial activity count...")
    initial_count = Activity.objects.filter(user=user).count()
    print(f"   Initial activities for user: {initial_count}")
    
    # Make test request to prediction endpoint
    print("\n4. Testing prediction endpoint...")
    client = Client()
    client.force_login(user)
    
    # Create a small base64 image (1x1 pixel JPEG)
    test_image = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k='
    
    response = client.post(
        '/activities/stream-predict/',
        {'image': test_image},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"   Response Status: {response.status_code}")
    data = json.loads(response.content)
    print(f"   Response Data: {data}")
    
    # Check final activity count
    print("\n5. Checking final activity count...")
    final_count = Activity.objects.filter(user=user).count()
    print(f"   Final activities for user: {final_count}")
    
    # Verify prediction was saved
    print("\n6. Verifying predictions were saved...")
    if final_count > initial_count:
        new_activities = Activity.objects.filter(user=user).order_by('-timestamp')[:final_count - initial_count]
        for i, activity in enumerate(new_activities, 1):
            print(f"   ✓ Activity {i}:")
            print(f"      - Type: {activity.activity_type}")
            print(f"      - Confidence: {activity.confidence_score}%")
            print(f"      - Location: {activity.location}")
            print(f"      - Timestamp: {activity.timestamp}")
    else:
        print("   ✗ No new activities saved!")
        return False
    
    print("\n" + "="*60)
    print("✓ TEST PASSED: Predictions are being saved correctly!")
    print("="*60)
    return True

if __name__ == '__main__':
    try:
        success = test_prediction_endpoint()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
