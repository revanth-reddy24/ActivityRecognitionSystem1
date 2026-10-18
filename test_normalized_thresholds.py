#!/usr/bin/env python
"""
More careful sitting vs standing pose comparison
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import AIActivityClassifier, Keypoint

classifier = AIActivityClassifier()

print("=" * 80)
print("DETAILED POSE COMPARISON WITH NORMALIZED THRESHOLDS")
print("=" * 80)

# REALISTIC SITTING: Person at desk, back against chair
# Shoulders around y=200, Hips around y=280 (only 80 pixels apart)
# Height overall about 280 pixels
sitting_pose_kps = [
    Keypoint('nose', 320, 100, 0.95),
    Keypoint('leftShoulder', 280, 200, 0.93),
    Keypoint('rightShoulder', 360, 200, 0.93),
    Keypoint('leftHip', 290, 280, 0.90),
    Keypoint('rightHip', 350, 280, 0.90),
    Keypoint('leftKnee', 285, 330, 0.88),
    Keypoint('rightKnee', 355, 330, 0.88),
    Keypoint('leftAnkle', 285, 380, 0.85),
    Keypoint('rightAnkle', 355, 380, 0.85),
]

# REALISTIC STANDING: Person standing upright
# Shoulders around y=150, Hips around y=320 (170 pixels apart)
# Height overall about 420 pixels
standing_pose_kps = [
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

sitting_metrics = classifier.pose_analyzer.extract_metrics(sitting_pose_kps)
standing_metrics = classifier.pose_analyzer.extract_metrics(standing_pose_kps)

print("\nSITTING POSE METRICS:")
print(f"  Height: {sitting_metrics.height:.2f} pixels")
print(f"  Shoulder-Hip Distance: {sitting_metrics.shoulder_hip_distance:.2f} pixels")
print(f"  Hip-Knee Distance: {sitting_metrics.hip_knee_distance:.2f} pixels")
print(f"  Normalized (SH/Height): {sitting_metrics.shoulder_hip_distance / sitting_metrics.height:.3f}")
print(f"  Normalized (HK/Height): {sitting_metrics.hip_knee_distance / sitting_metrics.height:.3f}")

print("\nSTANDING POSE METRICS:")
print(f"  Height: {standing_metrics.height:.2f} pixels")
print(f"  Shoulder-Hip Distance: {standing_metrics.shoulder_hip_distance:.2f} pixels")
print(f"  Hip-Knee Distance: {standing_metrics.hip_knee_distance:.2f} pixels")
print(f"  Normalized (SH/Height): {standing_metrics.shoulder_hip_distance / standing_metrics.height:.3f}")
print(f"  Normalized (HK/Height): {standing_metrics.hip_knee_distance / standing_metrics.height:.3f}")

print("\n" + "=" * 80)
print("CLASSIFIER THRESHOLDS:")
print("=" * 80)
print("SITTING: 0.05 < norm_sh_distance < 0.30")
print("STANDING: norm_sh_distance > 0.32 AND norm_hk_distance > 0.35")

sh_norm_sitting = sitting_metrics.shoulder_hip_distance / sitting_metrics.height
hk_norm_sitting = sitting_metrics.hip_knee_distance / sitting_metrics.height
sh_norm_standing = standing_metrics.shoulder_hip_distance / standing_metrics.height
hk_norm_standing = standing_metrics.hip_knee_distance / standing_metrics.height

print(f"\nSitting check: {0.05 < sh_norm_sitting < 0.30} (norm_sh={sh_norm_sitting:.3f})")
print(f"Standing check: {sh_norm_standing > 0.32 and hk_norm_standing > 0.35} (norm_sh={sh_norm_standing:.3f}, norm_hk={hk_norm_standing:.3f})")

# Test predictions
sitting_pred, sitting_conf = classifier.classify(sitting_pose_kps)
standing_pred, standing_conf = classifier.classify(standing_pose_kps)

print(f"\n" + "=" * 80)
print(f"PREDICTION RESULTS:")
print(f"=" * 80)
print(f"  Sitting  → {sitting_pred.upper()} ({sitting_conf}%)")
print(f"  Standing → {standing_pred.upper()} ({standing_conf}%)")
print(f"\nStatus: {'✓ PASS' if sitting_pred == 'sitting' and standing_pred == 'standing' else '✗ FAIL'}")
