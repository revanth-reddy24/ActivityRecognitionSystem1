#!/usr/bin/env python
"""Debug standing pose detection"""
from ai_activity_detector import Keypoint, PoseAnalyzer, AIActivityClassifier

standing_kps = [
    Keypoint('nose', 320, 48, 0.95),
    Keypoint('leftShoulder', 269, 84, 0.93),
    Keypoint('rightShoulder', 371, 84, 0.93),
    Keypoint('leftHip', 282, 259, 0.90),
    Keypoint('rightHip', 358, 259, 0.90),
    Keypoint('leftKnee', 282, 290, 0.88),
    Keypoint('rightKnee', 358, 290, 0.88),
]

analyzer = PoseAnalyzer()
metrics = analyzer.extract_metrics(standing_kps)

print(f"Standing pose metrics:")
print(f"  Height: {metrics.height:.1f}px")
print(f"  Shoulder-hip distance: {metrics.shoulder_hip_distance:.1f}px")
print(f"  Hip-knee distance: {metrics.hip_knee_distance:.1f}px")

ratio_sh = metrics.shoulder_hip_distance / metrics.height if metrics.height > 0 else 0
ratio_hk = metrics.hip_knee_distance / metrics.height if metrics.height > 0 else 0

print(f"\nRatios:")
print(f"  Shoulder-hip ratio: {ratio_sh:.3f}")
print(f"  Hip-knee ratio: {ratio_hk:.3f}")

print(f"\nChecks:")
print(f"  0.05 < {ratio_sh:.3f} < 0.30? {0.05 < ratio_sh < 0.30} (sitting)")
print(f"  {ratio_sh:.3f} > 0.30? {ratio_sh > 0.30} (standing)")
print(f"  {ratio_hk:.3f} > 0.15? {ratio_hk > 0.15}")

classifier = AIActivityClassifier()
activity, conf = classifier.classify(standing_kps)
print(f"\nClassification: {activity.upper()} ({conf}%)")
