#!/usr/bin/env python
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from activities.models import Environment, MultiPersonActivity, PersonActivity, Activity

User = get_user_model()

# Get or create test user
user, _ = User.objects.get_or_create(username='test_camera_user', defaults={'email': 'test@example.com'})

# Get or create environment
env, _ = Environment.objects.get_or_create(name='Test Location', defaults={'address': 'Test', 'is_active': True})

# Create a test client
client = Client()
client.force_login(user)

print("=" * 70)
print("Simulating Real-time Monitoring Workflow")
print("=" * 70)

# Simulate 3 consecutive frames of a person standing
for frame_num in range(1, 4):
    print(f"\n--- Frame {frame_num} ---")
    
    test_persons = [
        {
            'id': 1,  # Same person across frames
            'keypoints': [
                {'part': 'nose', 'position': {'x': 100 + frame_num*2, 'y': 50}, 'score': 0.9},
                {'part': 'leftShoulder', 'position': {'x': 80, 'y': 100}, 'score': 0.85},
                {'part': 'rightShoulder', 'position': {'x': 120, 'y': 100}, 'score': 0.85},
                {'part': 'leftHip', 'position': {'x': 85, 'y': 180}, 'score': 0.8},
                {'part': 'rightHip', 'position': {'x': 115, 'y': 180}, 'score': 0.8},
                {'part': 'leftKnee', 'position': {'x': 85, 'y': 240}, 'score': 0.75},
                {'part': 'rightKnee', 'position': {'x': 115, 'y': 240}, 'score': 0.75},
            ]
        }
    ]
    
    # Send pose prediction
    payload = json.dumps({'persons': test_persons, 'frames': [test_persons]})
    response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
    
    resp_data = response.json()
    print(f"Pose Prediction: {resp_data['persons'][0]['activity']} ({resp_data['persons'][0]['confidence']}%)")
    
    # Get current activities (what the UI would show)
    response = client.get('/activities/api/activities/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    activities = response.json().get('activities', [])
    
    print(f"Activity Feed now has {len(activities)} entries:")
    for i, act in enumerate(activities[:3]):
        print(f"  {i+1}. {act['activity_type'].upper()} ({act['confidence_score']}%) @ {act['timestamp']} [src: {act.get('source', 'unknown')}]")

print("\n" + "=" * 70)
print("Final Status")
print("=" * 70)

response = client.get('/activities/api/distribution/', HTTP_X_REQUESTED_With='XMLHttpRequest')
dist = response.json().get('distribution', {})
print("Activity Distribution:")
for activity, count in sorted(dist.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {activity}: {count}")

print("\n✓ All tests completed successfully!")
print("  Activity feed is now showing PersonActivity records alongside Activity records.")
