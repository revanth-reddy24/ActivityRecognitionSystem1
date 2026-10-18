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

print("=" * 80)
print("Testing Sleeping Pose Detection")
print("=" * 80)

# Test Case 1: Person lying down horizontally (classic sleeping pose)
print("\n[Test 1] Sleeping - Person lying on back (horizontal)")
print("-" * 80)

sleeping_pose_1 = {
    'id': 200,
    'keypoints': [
        # Person is lying down horizontally - nose at head, feet at other end
        # All Y values cluster together (similar vertical position)
        {'part': 'nose', 'position': {'x': 50, 'y': 100}, 'score': 0.9},
        {'part': 'leftShoulder', 'position': {'x': 60, 'y': 110}, 'score': 0.85},
        {'part': 'rightShoulder', 'position': {'x': 80, 'y': 110}, 'score': 0.85},
        {'part': 'leftHip', 'position': {'x': 70, 'y': 115}, 'score': 0.8},
        {'part': 'rightHip', 'position': {'x': 90, 'y': 115}, 'score': 0.8},
        {'part': 'leftKnee', 'position': {'x': 100, 'y': 120}, 'score': 0.75},
        {'part': 'rightKnee', 'position': {'x': 120, 'y': 120}, 'score': 0.75},
    ]
}

payload = json.dumps({'persons': [sleeping_pose_1], 'frames': [[sleeping_pose_1]]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
result = response.json()['persons'][0]
print(f"Input: Person lying down horizontally (width >> height)")
print(f"Expected: sleeping (high confidence)")
print(f"Got: {result['activity'].upper()} ({result['confidence']}%)")
print(f"Status: {'✓ PASS' if result['activity'] == 'sleeping' else '✗ FAIL'}")

# Test Case 2: Person lying down with different body orientation
print("\n[Test 2] Sleeping - Person lying on side")
print("-" * 80)

sleeping_pose_2 = {
    'id': 201,
    'keypoints': [
        # Person lying on side - very flat and stretched horizontally
        {'part': 'nose', 'position': {'x': 40, 'y': 120}, 'score': 0.9},
        {'part': 'leftShoulder', 'position': {'x': 60, 'y': 115}, 'score': 0.85},
        {'part': 'rightShoulder', 'position': {'x': 80, 'y': 125}, 'score': 0.85},
        {'part': 'leftHip', 'position': {'x': 100, 'y': 120}, 'score': 0.8},
        {'part': 'rightHip', 'position': {'x': 120, 'y': 120}, 'score': 0.8},
        {'part': 'leftKnee', 'position': {'x': 140, 'y': 125}, 'score': 0.75},
        {'part': 'rightKnee', 'position': {'x': 160, 'y': 115}, 'score': 0.75},
    ]
}

payload = json.dumps({'persons': [sleeping_pose_2], 'frames': [[sleeping_pose_2]]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
result = response.json()['persons'][0]
print(f"Input: Person lying on side")
print(f"Expected: sleeping (high confidence)")
print(f"Got: {result['activity'].upper()} ({result['confidence']}%)")
print(f"Status: {'✓ PASS' if result['activity'] == 'sleeping' else '✗ FAIL'}")

# Test Case 3: Lying down but with legs bent (fetal position)
print("\n[Test 3] Sleeping - Fetal position (legs bent)")
print("-" * 80)

sleeping_pose_3 = {
    'id': 202,
    'keypoints': [
        # Fetal position - compact, all points close together
        {'part': 'nose', 'position': {'x': 100, 'y': 100}, 'score': 0.9},
        {'part': 'leftShoulder', 'position': {'x': 95, 'y': 105}, 'score': 0.85},
        {'part': 'rightShoulder', 'position': {'x': 105, 'y': 105}, 'score': 0.85},
        {'part': 'leftHip', 'position': {'x': 100, 'y': 115}, 'score': 0.8},
        {'part': 'rightHip', 'position': {'x': 110, 'y': 115}, 'score': 0.8},
        {'part': 'leftKnee', 'position': {'x': 95, 'y': 125}, 'score': 0.75},
        {'part': 'rightKnee', 'position': {'x': 105, 'y': 125}, 'score': 0.75},
    ]
}

payload = json.dumps({'persons': [sleeping_pose_3], 'frames': [[sleeping_pose_3]]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
result = response.json()['persons'][0]
print(f"Input: Person in fetal position (compact, low vertical span)")
print(f"Expected: sleeping (high confidence)")
print(f"Got: {result['activity'].upper()} ({result['confidence']}%)")
print(f"Status: {'✓ PASS' if result['activity'] == 'sleeping' else '✗ FAIL'}")

# Test Case 4: Standing (should NOT be sleeping)
print("\n[Test 4] Standing - Control test (should NOT be sleeping)")
print("-" * 80)

standing_pose = {
    'id': 203,
    'keypoints': [
        # Normal standing - large vertical span
        {'part': 'nose', 'position': {'x': 100, 'y': 50}, 'score': 0.9},
        {'part': 'leftShoulder', 'position': {'x': 80, 'y': 100}, 'score': 0.85},
        {'part': 'rightShoulder', 'position': {'x': 120, 'y': 100}, 'score': 0.85},
        {'part': 'leftHip', 'position': {'x': 85, 'y': 180}, 'score': 0.8},
        {'part': 'rightHip', 'position': {'x': 115, 'y': 180}, 'score': 0.8},
        {'part': 'leftKnee', 'position': {'x': 85, 'y': 240}, 'score': 0.75},
        {'part': 'rightKnee', 'position': {'x': 115, 'y': 240}, 'score': 0.75},
    ]
}

payload = json.dumps({'persons': [standing_pose], 'frames': [[standing_pose]]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
result = response.json()['persons'][0]
print(f"Input: Person standing upright")
print(f"Expected: NOT sleeping (should be standing/running)")
print(f"Got: {result['activity'].upper()} ({result['confidence']}%)")
print(f"Status: {'✓ PASS' if result['activity'] != 'sleeping' else '✗ FAIL'}")

# Test Case 5: Sitting (should NOT be sleeping)
print("\n[Test 5] Sitting - Control test (should NOT be sleeping)")
print("-" * 80)

sitting_pose = {
    'id': 204,
    'keypoints': [
        # Person sitting - small shoulder-hip gap, moderate vertical span
        {'part': 'nose', 'position': {'x': 100, 'y': 80}, 'score': 0.9},
        {'part': 'leftShoulder', 'position': {'x': 80, 'y': 105}, 'score': 0.85},
        {'part': 'rightShoulder', 'position': {'x': 120, 'y': 105}, 'score': 0.85},
        {'part': 'leftHip', 'position': {'x': 85, 'y': 125}, 'score': 0.8},
        {'part': 'rightHip', 'position': {'x': 115, 'y': 125}, 'score': 0.8},
        {'part': 'leftKnee', 'position': {'x': 85, 'y': 155}, 'score': 0.75},
        {'part': 'rightKnee', 'position': {'x': 115, 'y': 155}, 'score': 0.75},
    ]
}

payload = json.dumps({'persons': [sitting_pose], 'frames': [[sitting_pose]]})
response = client.post('/activities/pose-predict/', data=payload, content_type='application/json')
result = response.json()['persons'][0]
print(f"Input: Person sitting upright")
print(f"Expected: NOT sleeping (should be sitting)")
print(f"Got: {result['activity'].upper()} ({result['confidence']}%)")
print(f"Status: {'✓ PASS' if result['activity'] == 'sitting' else '✗ FAIL'}")

print("\n" + "=" * 80)
print("Sleeping Detection Test Summary")
print("=" * 80)
