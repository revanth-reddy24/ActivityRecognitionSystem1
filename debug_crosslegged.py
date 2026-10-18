#!/usr/bin/env python
"""
Debug: Cross-legged sitting - why is it predicting STANDING?
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import Keypoint, AIActivityClassifier, PoseAnalyzer

# Cross-legged sitting - normalized coordinates (0-1 range)
crosslegged_kps = [
    Keypoint('nose', 320, 67, 0.95),
    Keypoint('leftShoulder', 269, 115, 0.93),
    Keypoint('rightShoulder', 371, 115, 0.93),
    Keypoint('leftHip', 282, 158, 0.90),
    Keypoint('rightHip', 358, 158, 0.90),
    Keypoint('leftKnee', 307, 201, 0.88),
    Keypoint('rightKnee', 333, 201, 0.88),
]

analyzer = PoseAnalyzer()
classifier = AIActivityClassifier()

print("="*70)
print("DEBUGGING: Cross-Legged Sitting")
print("="*70)

metrics = analyzer.extract_metrics(crosslegged_kps)
print(f"\nMetrics:")
print(f"  Width: {metrics.width:.1f}px")
print(f"  Height: {metrics.height:.1f}px")
print(f"  Aspect ratio: {metrics.aspect_ratio:.3f}")
print(f"  Shoulder-hip distance: {metrics.shoulder_hip_distance:.1f}px")
print(f"  Hip-knee distance: {metrics.hip_knee_distance:.1f}px")

# Check what triggers
ratio_sh = metrics.shoulder_hip_distance / metrics.height if metrics.height > 0 else 0
ratio_hk = metrics.hip_knee_distance / metrics.height if metrics.height > 0 else 0
print(f"\nRatios:")
print(f"  Shoulder-hip ratio: {ratio_sh:.3f}")
print(f"  Hip-knee ratio: {ratio_hk:.3f}")

print(f"\nSitting check:")
print(f"  0.05 < {ratio_sh:.3f} < 0.30? {0.05 < ratio_sh < 0.30}")

print(f"\nStanding check:")
print(f"  {ratio_sh:.3f} > 0.30? {ratio_sh > 0.30}")
print(f"  {ratio_hk:.3f} > 0.15? {ratio_hk > 0.15}")
print(f"  Both true? {ratio_sh > 0.30 and ratio_hk > 0.15}")

result = classifier.classify(crosslegged_kps)
print(f"\nClassification: {result[0].upper()} ({result[1]}%)")

print("\n" + "="*70)
print("ANALYSIS:")
if result[0].lower() == 'sitting':
    print("✓ Correct! Cross-legged sitting recognized")
else:
    print("Issue: Ratio too high for cross-legged sitting")
    print(f"Shoulder-hip ratio = {ratio_sh:.3f}")
    print(f"For cross-legged, this should still be < 0.30")
    print(f"But actually it's {ratio_sh:.3f}")
print("="*70)
