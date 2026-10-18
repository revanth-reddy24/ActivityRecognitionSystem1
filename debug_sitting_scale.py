#!/usr/bin/env python
"""
Debug: Why is sitting still detecting as standing?
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import PoseAnalyzer

# Sitting pose (normalized 0-1) - from comprehensive test
sitting_keypoints = [
    {'part': 'nose', 'position': {'x': 0.5, 'y': 0.25}, 'score': 0.95},
    {'part': 'leftShoulder', 'position': {'x': 0.4, 'y': 0.42}, 'score': 0.93},
    {'part': 'rightShoulder', 'position': {'x': 0.6, 'y': 0.42}, 'score': 0.93},
    {'part': 'leftHip', 'position': {'x': 0.42, 'y': 0.58}, 'score': 0.90},  # Only 0.16 below shoulders
    {'part': 'rightHip', 'position': {'x': 0.58, 'y': 0.58}, 'score': 0.90},
    {'part': 'leftKnee', 'position': {'x': 0.42, 'y': 0.75}, 'score': 0.88},
    {'part': 'rightKnee', 'position': {'x': 0.58, 'y': 0.75}, 'score': 0.88},
]

# Convert to raw format for PoseAnalyzer
kps = []
for kp in sitting_keypoints:
    kps.append({
        'x': kp['position']['x'],
        'y': kp['position']['y'],
        'score': kp['score']
    })

analyzer = PoseAnalyzer()

# Step 1: Check auto-scaling
print("Step 1: Auto-scaling check")
print(f"  Max X: {max(kp['x'] for kp in kps):.3f}")
print(f"  Max Y: {max(kp['y'] for kp in kps):.3f}")
scaled = analyzer._auto_scale_keypoints(kps)
print(f"  After scaling - X: {[kp['x'] for kp in scaled][:3]}")
print(f"  After scaling - Y: {[kp['y'] for kp in scaled][:3]}")

# Step 2: Extract metrics
print("\nStep 2: Extract metrics")
metrics = analyzer.extract_metrics(kps, motion_type='')
print(f"  Shoulder-hip distance: {metrics.get('shoulder_hip_distance', 0):.2f}px")
print(f"  Height: {metrics.get('height', 0):.2f}px")
print(f"  Ratio: {metrics.get('ratio', 0):.3f}")
print(f"  Hip-knee ratio: {metrics.get('hip_knee_ratio', 0):.3f}")

# Step 3: Check thresholds
print("\nStep 3: Threshold comparison")
ratio = metrics.get('ratio', 0)
print(f"  Ratio {ratio:.3f}")
print(f"  Sitting threshold: 0.05 < ratio < 0.30")
print(f"  Standing threshold: ratio >= 0.30")
print(f"  Is ratio in sitting range? {0.05 < ratio < 0.30}")
print(f"  Is ratio in standing range? {ratio >= 0.30}")

# Step 4: Full classification
print("\nStep 4: Full classification")
activity = analyzer.classify(kps, motion_type='')
print(f"  Predicted: {activity['activity']} ({activity['confidence']}%)")

print("\n" + "="*60)
print("EXPECTED: SITTING should have ratio 0.05-0.30")
print("ACTUAL: Currently predicting as STANDING (ratio >= 0.30)")
print("="*60)
