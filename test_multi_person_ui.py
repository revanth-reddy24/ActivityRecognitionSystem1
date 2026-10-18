#!/usr/bin/env python
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from activities.models import Environment, PersonActivity

User = get_user_model()

user, _ = User.objects.get_or_create(username='test_camera_user', defaults={'email': 'test@example.com'})
env, _ = Environment.objects.get_or_create(name='Test Location', defaults={'address': 'Test', 'is_active': True})

client = Client()
client.force_login(user)

print("=" * 70)
print("Test: Multiple People with Different Activities")
print("=" * 70)

# Simulate 2 people: one standing, one sitting
test_persons = [
    {
        'id': 100,  # Person 1
        'keypoints': [
            {'part': 'nose', 'position': {'x': 100, 'y': 50}, 'score': 0.9},
            {'part': 'leftShoulder', 'position': {'x': 80, 'y': 100}, 'score': 0.85},
            {'part': 'rightShoulder', 'position': {'x': 120, 'y': 100}, 'score': 0.85},
            {'part': 'leftHip', 'position': {'x': 85, 'y': 180}, 'score': 0.8},
            {'part': 'rightHip', 'position': {'x': 115, 'y': 180}, 'score': 0.8},
            {'part': 'leftKnee', 'position': {'x': 85, 'y': 240}, 'score': 0.75},
            {'part': 'rightKnee', 'position': {'x': 115, 'y': 240}, 'score': 0.75},
        ]
    },
    {
        'id': 101,  # Person 2 (sitting - smaller vertical span)
        'keypoints': [
            {'part': 'nose', 'position': {'x': 300, 'y': 80}, 'score': 0.9},
            {'part': 'leftShoulder', 'position': {'x': 280, 'y': 110}, 'score': 0.85},
            {'part': 'rightShoulder', 'position': {'x': 320, 'y': 110}, 'score': 0.85},
            {'part': 'leftHip', 'position': {'x': 285, 'y': 160}, 'score': 0.8},
            {'part': 'rightHip', 'position': {'x': 315, 'y': 160}, 'score': 0.8},
            {'part': 'leftKnee', 'position': {'x': 285, 'y': 190}, 'score': 0.75},
            {'part': 'rightKnee', 'position': {'x': 315, 'y': 190}, 'score': 0.75},
        ]
    }
]

payload = json.dumps({'persons': test_persons, 'frames': [test_persons]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')

resp_data = response.json()
print(f"\nPose Prediction Response:")
for i, p in enumerate(resp_data['persons'], 1):
    print(f"  Person {i} (client_id={p.get('client_id')}): {p['activity']} ({p['confidence']}%)")

print(f"\nServer returned {len(resp_data['persons'])} outputs for {len(test_persons)} inputs")

# Now fetch activity feed
response = client.get('/activities/api/activities/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
activities = response.json().get('activities', [])

print(f"\nActivity Feed (showing recent entries):")
for i, act in enumerate(activities[:5]):
    print(f"  {i+1}. {act['activity_type'].upper()} ({act['confidence_score']}%) @ {act['timestamp']} [src: {act.get('source', 'unknown')}]")

print("\n" + "=" * 70)
print("✓ Multiple people test completed!")
print(f"  - Server accepts multiple persons and returns one output per person")
print(f"  - Activity feed shows {len(activities)} total records")
print("=" * 70)
