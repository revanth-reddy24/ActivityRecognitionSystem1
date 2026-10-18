#!/usr/bin/env python
"""
Compare sitting vs standing poses to understand the real metric differences
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import AIActivityClassifier, Keypoint

classifier = AIActivityClassifier()

print("=" * 80)
print("POSE COMPARISON: Sitting vs Standing")
print("=" * 80)

# SITTING POSE (as before)
sitting_pose_kps = [
    Keypoint('nose', 320, 140, 0.95),
    Keypoint('leftShoulder', 280, 200, 0.93),
    Keypoint('rightShoulder', 360, 200, 0.93),
    Keypoint('leftElbow', 250, 280, 0.91),
    Keypoint('rightElbow', 390, 280, 0.91),
    Keypoint('leftWrist', 220, 340, 0.88),
    Keypoint('rightWrist', 420, 340, 0.88),
    Keypoint('leftHip', 290, 310, 0.90),
    Keypoint('rightHip', 350, 310, 0.90),
    Keypoint('leftKnee', 285, 380, 0.88),
    Keypoint('rightKnee', 355, 380, 0.88),
    Keypoint('leftAnkle', 285, 450, 0.85),
    Keypoint('rightAnkle', 355, 450, 0.85),
]

# STANDING POSE
standing_pose_kps = [
    Keypoint('nose', 320, 80, 0.95),
    Keypoint('leftShoulder', 280, 180, 0.93),
    Keypoint('rightShoulder', 360, 180, 0.93),
    Keypoint('leftElbow', 250, 260, 0.91),
    Keypoint('rightElbow', 390, 260, 0.91),
    Keypoint('leftWrist', 220, 340, 0.88),
    Keypoint('rightWrist', 420, 340, 0.88),
    Keypoint('leftHip', 290, 340, 0.90),
    Keypoint('rightHip', 350, 340, 0.90),
    Keypoint('leftKnee', 285, 480, 0.88),
    Keypoint('rightKnee', 355, 480, 0.88),
    Keypoint('leftAnkle', 285, 600, 0.85),
    Keypoint('rightAnkle', 355, 600, 0.85),
]

sitting_metrics = classifier.pose_analyzer.extract_metrics(sitting_pose_kps)
standing_metrics = classifier.pose_analyzer.extract_metrics(standing_pose_kps)

print("\nSITTING POSE:")
print(f"  Height: {sitting_metrics.height:.2f} pixels")
print(f"  Shoulder-Hip Distance: {sitting_metrics.shoulder_hip_distance:.2f} pixels")
print(f"  Hip-Knee Distance: {sitting_metrics.hip_knee_distance:.2f} pixels")
print(f"  Ratio (SH/Height): {sitting_metrics.shoulder_hip_distance / sitting_metrics.height:.3f}")

print("\nSTANDING POSE:")
print(f"  Height: {standing_metrics.height:.2f} pixels")
print(f"  Shoulder-Hip Distance: {standing_metrics.shoulder_hip_distance:.2f} pixels")
print(f"  Hip-Knee Distance: {standing_metrics.hip_knee_distance:.2f} pixels")
print(f"  Ratio (SH/Height): {standing_metrics.shoulder_hip_distance / standing_metrics.height:.3f}")

print("\n" + "=" * 80)
print("KEY INSIGHT:")
print("=" * 80)
print("When sitting: shoulders and hips are CLOSE together (small distance)")
print("When standing: shoulders are FAR above hips (large distance relative to height)")
print("\nThe REAL distinguishing metric should be:")
print("  - Hip_Y position relative to Shoulder_Y")
print("  - When sitting: Hips barely below shoulders (10-15% of body height)")
print("  - When standing: Hips well below shoulders (40-50% of body height)")
print("\nBUT the current threshold (< 28 pixels) is TOO STRICT")
print("because it doesn't account for person distance from camera")
print("=" * 80)

# Test predictions
sitting_pred, sitting_conf = classifier.classify(sitting_pose_kps)
standing_pred, standing_conf = classifier.classify(standing_pose_kps)

print(f"\nPREDICTION TEST:")
print(f"  Sitting → {sitting_pred.upper()} ({sitting_conf}%)")
print(f"  Standing → {standing_pred.upper()} ({standing_conf}%)")
