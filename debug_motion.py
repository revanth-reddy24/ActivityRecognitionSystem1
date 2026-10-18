#!/usr/bin/env python
"""Debug motion analysis"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import AIActivityClassifier, Keypoint

classifier = AIActivityClassifier()

standing = [
    Keypoint('nose', 320, 50, 0.95),
    Keypoint('leftShoulder', 280, 150, 0.93),
    Keypoint('rightShoulder', 360, 150, 0.93),
    Keypoint('leftHip', 290, 320, 0.90),
    Keypoint('rightHip', 350, 320, 0.90),
    Keypoint('leftKnee', 285, 420, 0.88),
    Keypoint('rightKnee', 355, 420, 0.88),
    Keypoint('leftAnkle', 285, 500, 0.85),
    Keypoint('rightAnkle', 355, 500, 0.85),
]

metrics = classifier.pose_analyzer.extract_metrics(standing)
motion = classifier.motion_analyzer.analyze()

print(f"Metrics:")
print(f"  Height: {metrics.height}")
print(f"  SH Distance: {metrics.shoulder_hip_distance}")
print(f"  HK Distance: {metrics.hip_knee_distance}")
print(f"  Norm SH: {metrics.shoulder_hip_distance / metrics.height}")
print(f"  Norm HK: {metrics.hip_knee_distance / metrics.height}")

print(f"\nMotion:")
print(f"  Motion Type: '{motion.motion_type}'")
print(f"  Motion Variance: {motion.motion_variance}")
print(f"  Frame Displacement: {motion.frame_displacement}")

print(f"\nCondition checks:")
print(f"  norm_sh > 0.30: {metrics.shoulder_hip_distance / metrics.height > 0.30}")
print(f"  norm_hk > 0.15: {metrics.hip_knee_distance / metrics.height > 0.15}")
print(f"  motion_type == 'static': {motion.motion_type == 'static'}")
print(f"  motion_variance < 5: {motion.motion_variance < 5}")
