#!/usr/bin/env python
"""
Test using the actual Django HTTP endpoint
Force reimport of classifier to get latest code
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Force reimport
if 'ai_activity_detector' in sys.modules:
    del sys.modules['ai_activity_detector']
if 'activities.views' in sys.modules:
    del sys.modules['activities.views']

from django.test import Client
from django.contrib.auth import get_user_model
from activities.models import Environment
import json
import importlib

# Reload modules
import ai_activity_detector
importlib.reload(ai_activity_detector)

User = get_user_model()
user, _ = User.objects.get_or_create(username='test_reload', defaults={'email': 'test@example.com'})
env, _ = Environment.objects.get_or_create(name='Test Location', defaults={'address': 'Test', 'is_active': True})

client = Client()
client.force_login(user)

# Test cases
test_cases = {
    'Office Worker (Legs Hidden)': {
        'keypoints': [
            {'part': 'nose', 'position': {'x': 0.5, 'y': 0.15}, 'score': 0.95},
            {'part': 'leftShoulder', 'position': {'x': 0.4, 'y': 0.25}, 'score': 0.93},
            {'part': 'rightShoulder', 'position': {'x': 0.6, 'y': 0.25}, 'score': 0.93},
            {'part': 'leftHip', 'position': {'x': 0.42, 'y': 0.32}, 'score': 0.90},
            {'part': 'rightHip', 'position': {'x': 0.58, 'y': 0.32}, 'score': 0.90},
            {'part': 'leftElbow', 'position': {'x': 0.35, 'y': 0.27}, 'score': 0.88},
            {'part': 'rightElbow', 'position': {'x': 0.65, 'y': 0.27}, 'score': 0.88},
        ]
    },
    'Cross-Legged': {
        'keypoints': [
            {'part': 'nose', 'position': {'x': 0.5, 'y': 0.105}, 'score': 0.95},
            {'part': 'leftShoulder', 'position': {'x': 0.42, 'y': 0.18}, 'score': 0.93},
            {'part': 'rightShoulder', 'position': {'x': 0.58, 'y': 0.18}, 'score': 0.93},
            {'part': 'leftHip', 'position': {'x': 0.44, 'y': 0.25}, 'score': 0.90},
            {'part': 'rightHip', 'position': {'x': 0.56, 'y': 0.25}, 'score': 0.90},
            {'part': 'leftKnee', 'position': {'x': 0.48, 'y': 0.315}, 'score': 0.88},
            {'part': 'rightKnee', 'position': {'x': 0.52, 'y': 0.315}, 'score': 0.88},
        ]
    },
}

print("="*70)
print("ENDPOINT TEST (with module reload)")
print("="*70)

for name, data in test_cases.items():
    payload = json.dumps({'persons': [{'id': 1, 'keypoints': data['keypoints']}]})
    response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
    
    if response.status_code == 200:
        result = response.json()['persons'][0]
        activity = result['activity'].upper()
        confidence = result['confidence']
        status = '✓' if activity == 'SITTING' else '✗'
        print(f"{status} {name:30} → {activity:12} ({confidence}%)")
    else:
        print(f"✗ {name:30} → ERROR {response.status_code}")

print("="*70)
