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

# Log in
client.force_login(user)

print("=" * 60)
print("Test 1: Standing person (client id=1)")
print("=" * 60)

# Simulate a pose prediction request with client ids (like the JS client sends)
test_persons = [
    {
        'id': 1,
        'keypoints': [
            {'part': 'nose', 'position': {'x': 100, 'y': 50}, 'score': 0.9},
            {'part': 'leftShoulder', 'position': {'x': 80, 'y': 100}, 'score': 0.85},
            {'part': 'rightShoulder', 'position': {'x': 120, 'y': 100}, 'score': 0.85},
            {'part': 'leftHip', 'position': {'x': 85, 'y': 180}, 'score': 0.8},
            {'part': 'rightHip', 'position': {'x': 115, 'y': 180}, 'score': 0.8},
            {'part': 'leftKnee', 'position': {'x': 85, 'y': 240}, 'score': 0.75},
            {'part': 'rightKnee', 'position': {'x': 115, 'y': 240}, 'score': 0.75},
        ]
    }
]

payload = json.dumps({'persons': test_persons, 'frames': [test_persons]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')

print(f"Response Status: {response.status_code}")
resp_data = response.json() if response.status_code == 200 else {}
print(f"Response Data: {resp_data}")

# Check database
print(f"\nPersonActivity count after request: {PersonActivity.objects.count()}")
recent = PersonActivity.objects.all().order_by('-id').first()
if recent:
    print(f"Recent PersonActivity: {recent.activity_type} @ {recent.timestamp} (confidence: {recent.confidence_score})")
    print(f"Client ID in pose: {recent.pose.get('client_id', 'N/A')}")

print("\n" + "=" * 60)
print("Test 2: Check /api/activities/ endpoint")
print("=" * 60)

response = client.get('/activities/api/activities/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
print(f"Response Status: {response.status_code}")
data = response.json() if response.status_code == 200 else {}
print(f"Activities returned: {len(data.get('activities', []))}")
if data.get('activities'):
    for act in data['activities'][:3]:
        print(f"  - {act['activity_type']} ({act['confidence_score']}%) @ {act['timestamp']}")

print("\n" + "=" * 60)
print("Test 3: Check /api/distribution/ endpoint")
print("=" * 60)

response = client.get('/activities/api/distribution/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
print(f"Response Status: {response.status_code}")
data = response.json() if response.status_code == 200 else {}
print(f"Distribution data: {data.get('distribution', {})}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print(f"Total Activity records: {Activity.objects.count()}")
print(f"Total PersonActivity records: {PersonActivity.objects.count()}")
print(f"Total MultiPersonActivity records: {MultiPersonActivity.objects.count()}")
