#!/usr/bin/env python
"""
Debug keypoint ranges and scales being received
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from activities.models import Environment, PersonActivity
import json

User = get_user_model()
user, _ = User.objects.get_or_create(username='test_camera_user', defaults={'email': 'test@example.com'})
env, _ = Environment.objects.get_or_create(name='Test Location', defaults={'address': 'Test', 'is_active': True})

client = Client()
client.force_login(user)

print("=" * 80)
print("KEYPOINT SCALE ANALYSIS - What scales are real poses using?")
print("=" * 80)

# Test pose: person standing, normal camera frame (typically 640x480 or 1280x720)
# PoseNet typically outputs coordinates in the frame's pixel space
standing_realistic = {
    'id': 1,
    'keypoints': [
        # Nose at top-middle
        {'part': 'nose', 'position': {'x': 320, 'y': 120}, 'score': 0.95},
        # Shoulders around y=200
        {'part': 'leftShoulder', 'position': {'x': 250, 'y': 200}, 'score': 0.93},
        {'part': 'rightShoulder', 'position': {'x': 390, 'y': 200}, 'score': 0.93},
        # Hips around y=350
        {'part': 'leftHip', 'position': {'x': 270, 'y': 350}, 'score': 0.90},
        {'part': 'rightHip', 'position': {'x': 370, 'y': 350}, 'score': 0.90},
        # Knees around y=480
        {'part': 'leftKnee', 'position': {'x': 270, 'y': 480}, 'score': 0.88},
        {'part': 'rightKnee', 'position': {'x': 370, 'y': 480}, 'score': 0.88},
    ]
}

payload = json.dumps({'persons': [standing_realistic]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
result = response.json()

print("\nTest 1: Standing pose in 640x480 frame")
print(f"Keypoints Y range: 120 to 480 (frame height ~380)")
print(f"Response: {result['persons'][0]}")

# Now test with scaled-up coordinates (like 1280x720 frame)
standing_large_frame = {
    'id': 2,
    'keypoints': [
        {'part': 'nose', 'position': {'x': 640, 'y': 240}, 'score': 0.95},
        {'part': 'leftShoulder', 'position': {'x': 500, 'y': 400}, 'score': 0.93},
        {'part': 'rightShoulder', 'position': {'x': 780, 'y': 400}, 'score': 0.93},
        {'part': 'leftHip', 'position': {'x': 540, 'y': 700}, 'score': 0.90},
        {'part': 'rightHip', 'position': {'x': 740, 'y': 700}, 'score': 0.90},
        {'part': 'leftKnee', 'position': {'x': 540, 'y': 960}, 'score': 0.88},
        {'part': 'rightKnee', 'position': {'x': 740, 'y': 960}, 'score': 0.88},
    ]
}

payload = json.dumps({'persons': [standing_large_frame]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
result = response.json()

print("\nTest 2: Same standing pose but in 1280x720 frame (2x scale)")
print(f"Keypoints Y range: 240 to 960 (frame height ~760)")
print(f"Response: {result['persons'][0]}")

# Test with tiny coordinates (like normalized 0-1 range from some pose models)
standing_normalized = {
    'id': 3,
    'keypoints': [
        {'part': 'nose', 'position': {'x': 0.5, 'y': 0.25}, 'score': 0.95},
        {'part': 'leftShoulder', 'position': {'x': 0.4, 'y': 0.42}, 'score': 0.93},
        {'part': 'rightShoulder', 'position': {'x': 0.6, 'y': 0.42}, 'score': 0.93},
        {'part': 'leftHip', 'position': {'x': 0.42, 'y': 0.73}, 'score': 0.90},
        {'part': 'rightHip', 'position': {'x': 0.58, 'y': 0.73}, 'score': 0.90},
        {'part': 'leftKnee', 'position': {'x': 0.42, 'y': 1.0}, 'score': 0.88},
        {'part': 'rightKnee', 'position': {'x': 0.58, 'y': 1.0}, 'score': 0.88},
    ]
}

payload = json.dumps({'persons': [standing_normalized]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
result = response.json()

print("\nTest 3: Same standing pose but in normalized 0-1 range (tiny numbers)")
print(f"Keypoints Y range: 0.25 to 1.0 (normalized scale)")
print(f"Response: {result['persons'][0]}")

print("\n" + "=" * 80)
print("KEY INSIGHT:")
print("=" * 80)
print("The classifier fails when keypoint coordinates are:")
print("  - Extremely small (0.0-1.0 range): height becomes ~0.75, all distances tiny")
print("  - Extremely large (>2000): height becomes huge, ratios change")
print("  - Inconsistent scale: threshold ratios (0.30, etc.) don't work")
print("\nSOLUTION: Auto-detect and scale keypoints to standard 640x480 range")
print("=" * 80)
