#!/usr/bin/env python
"""
Diagnostic script to analyze why sitting is being misclassified as standing.
Runs real prediction and logs metrics.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from activities.models import Environment
import json

from ai_activity_detector import AIActivityClassifier, Keypoint

User = get_user_model()
user, _ = User.objects.get_or_create(username='test_camera_user', defaults={'email': 'test@example.com'})
env, _ = Environment.objects.get_or_create(name='Test Location', defaults={'address': 'Test', 'is_active': True})

classifier = AIActivityClassifier()

print("=" * 80)
print("DIAGNOSTIC: Sitting Detection Analysis")
print("=" * 80)

# Based on the real camera screenshot, person is sitting at desk with feet on ground
# Realistic sitting: shoulders high, hips at chair level, knees lower
sitting_pose = {
    'id': 1,
    'keypoints': [
        {'part': 'nose', 'position': {'x': 320, 'y': 140}, 'score': 0.95},
        {'part': 'leftEye', 'position': {'x': 305, 'y': 130}, 'score': 0.94},
        {'part': 'rightEye', 'position': {'x': 335, 'y': 130}, 'score': 0.94},
        {'part': 'leftShoulder', 'position': {'x': 280, 'y': 200}, 'score': 0.93},
        {'part': 'rightShoulder', 'position': {'x': 360, 'y': 200}, 'score': 0.93},
        {'part': 'leftElbow', 'position': {'x': 250, 'y': 280}, 'score': 0.91},
        {'part': 'rightElbow', 'position': {'x': 390, 'y': 280}, 'score': 0.91},
        {'part': 'leftWrist', 'position': {'x': 220, 'y': 340}, 'score': 0.88},
        {'part': 'rightWrist', 'position': {'x': 420, 'y': 340}, 'score': 0.88},
        # SITTING: Hips are LOWER than shoulders (more than 100 pixels below)
        {'part': 'leftHip', 'position': {'x': 290, 'y': 310}, 'score': 0.90},
        {'part': 'rightHip', 'position': {'x': 350, 'y': 310}, 'score': 0.90},
        # Knees bend downward
        {'part': 'leftKnee', 'position': {'x': 285, 'y': 380}, 'score': 0.88},
        {'part': 'rightKnee', 'position': {'x': 355, 'y': 380}, 'score': 0.88},
        # Feet on ground
        {'part': 'leftAnkle', 'position': {'x': 285, 'y': 450}, 'score': 0.85},
        {'part': 'rightAnkle', 'position': {'x': 355, 'y': 450}, 'score': 0.85},
    ]
}

# Convert to AI format
keypoints = [
    Keypoint(
        part=kp['part'],
        x=kp['position']['x'],
        y=kp['position']['y'],
        score=kp['score']
    )
    for kp in sitting_pose['keypoints']
]

# Get metrics
metrics = classifier.pose_analyzer.extract_metrics(keypoints)

print("\n[1] BODY METRICS EXTRACTED:")
print(f"    Height (pixels): {metrics.height:.2f}")
print(f"    Width (pixels): {metrics.width:.2f}")
print(f"    Aspect Ratio: {metrics.aspect_ratio:.3f}")
print(f"    Shoulder-Hip Distance: {metrics.shoulder_hip_distance:.2f}")
print(f"    Hip-Knee Distance: {metrics.hip_knee_distance:.2f}")
print(f"    Knee-Ankle Distance: {metrics.knee_ankle_distance:.2f}")
print(f"    Arm Spread: {metrics.arm_spread:.2f}")
print(f"    Leg Spread: {metrics.leg_spread:.2f}")
print(f"    Body Angle: {metrics.body_angle:.2f}°")
print(f"    Avg Confidence: {metrics.avg_keypoint_confidence:.3f}")

print("\n[2] CLASSIFICATION LOGIC CHECK:")
print(f"    Aspect Ratio > 1.3 (sleeping check): {metrics.aspect_ratio > 1.3}")
print(f"    Shoulder-Hip < 15 AND height < 120 (sleeping check): {metrics.shoulder_hip_distance < 15 and metrics.height < 120}")
print(f"    Shoulder-Hip < 28 (sitting check): {metrics.shoulder_hip_distance < 28}")
print(f"    Shoulder-Hip > 40 (standing check): {metrics.shoulder_hip_distance > 40}")

print("\n[3] MOTION ANALYSIS:")
motion = classifier.motion_analyzer.analyze()
print(f"    Motion Type: {motion.motion_type}")
print(f"    Motion Variance: {motion.motion_variance:.2f}")
print(f"    Motion Direction: {motion.motion_direction}")
print(f"    Frame Displacement: {motion.frame_displacement:.2f}")

print("\n[4] PREDICTION:")
activity, confidence = classifier.classify(keypoints)
print(f"    Predicted Activity: {activity.upper()}")
print(f"    Confidence: {confidence}%")

print("\n[5] PROBLEM ANALYSIS:")
print(f"    ✗ Issue: Sitting threshold (< 28) but got shoulder_hip_distance = {metrics.shoulder_hip_distance:.2f}")
if metrics.shoulder_hip_distance > 28:
    print(f"    → Likely classified as STANDING because {metrics.shoulder_hip_distance:.2f} > 28")
    print(f"    → Root cause: Thresholds are not normalized to body size")
    print(f"    → Person sitting WITH RELAXED POSTURE has large shoulder-hip gap")
    print(f"    → Need to normalize by HEIGHT or use RATIO instead of absolute pixels")

print("\n[6] SOLUTION:")
print(f"    Current: absolute pixel thresholds (28 for sitting, 40 for standing)")
print(f"    Better: use ratio = shoulder_hip_distance / height")
ratio = metrics.shoulder_hip_distance / metrics.height if metrics.height > 0 else 0
print(f"    Ratio = {metrics.shoulder_hip_distance:.2f} / {metrics.height:.2f} = {ratio:.3f}")
print(f"    Expected sitting ratio: ~0.3-0.5 (hips 30-50% below shoulders)")
print(f"    Expected standing ratio: ~0.8-1.2 (hips 80-120% below shoulders)")

print("\n" + "=" * 80)
