#!/usr/bin/env python
"""
Verify sitting pose with more realistic keypoint spacing
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import Keypoint, PoseAnalyzer, AIActivityClassifier
import json

# **Real sitting pose** - shoulders and hips should be CLOSE together
# When sitting, your hips are lower than shoulders by a SMALL amount
# So ratio should be small (0.05-0.30)

sitting_kps_normalized = [
    Keypoint('nose', 0.5, 0.25, 0.95),
    Keypoint('leftShoulder', 0.4, 0.42, 0.93),  # Shoulder at y=0.42
    Keypoint('rightShoulder', 0.6, 0.42, 0.93),  # Shoulder at y=0.42
    Keypoint('leftHip', 0.42, 0.48, 0.90),       # Hip at y=0.48 (only 0.06 below shoulders!)
    Keypoint('rightHip', 0.58, 0.48, 0.90),      # Hip at y=0.48
    Keypoint('leftKnee', 0.42, 0.70, 0.88),      # Knee at y=0.70
    Keypoint('rightKnee', 0.58, 0.70, 0.88),     # Knee at y=0.70
]

analyzer = PoseAnalyzer()

# Manually trace through the classification
print("="*70)
print("SITTING POSE ANALYSIS (NORMALIZED 0-1)")
print("="*70)

# Check auto-scaling
print("\n1. Auto-scaling check:")
max_x = max(kp.x for kp in sitting_kps_normalized)
max_y = max(kp.y for kp in sitting_kps_normalized)
print(f"   Max X: {max_x:.3f}, Max Y: {max_y:.3f}")
print(f"   → Should scale to 640x480? {max_x <= 1.0 and max_y <= 1.0}")

# Scale manually
sitting_kps_scaled = [
    Keypoint(kp.part, kp.x * 640, kp.y * 480, kp.score)
    for kp in sitting_kps_normalized
]
print(f"   After scaling: Y values = {[kp.y for kp in sitting_kps_scaled][:5]}")

# Extract metrics
metrics = analyzer.extract_metrics(sitting_kps_normalized)
print(f"\n2. Extracted metrics:")
print(f"   Shoulder-hip distance: {metrics.shoulder_hip_distance:.2f}px")
print(f"   Height: {metrics.height:.2f}px")
ratio = metrics.shoulder_hip_distance / metrics.height if metrics.height > 0 else 0
print(f"   Ratio: {ratio:.3f}")
print(f"   Hip-knee ratio: {metrics.hip_knee_distance / metrics.height if metrics.height > 0 else 0:.3f}")

# Check thresholds
print(f"\n3. Threshold checks:")
ratio = metrics.shoulder_hip_distance / metrics.height if metrics.height > 0 else 0
print(f"   Ratio = {ratio:.3f}")
print(f"   Sitting range: 0.05 < ratio < 0.30? {0.05 < ratio < 0.30}")
print(f"   Standing range: ratio >= 0.30? {ratio >= 0.30}")

# Classify
classifier = AIActivityClassifier()
result = classifier.classify(sitting_kps_normalized)
print(f"\n4. Classification result:")
activity, confidence = result
print(f"   Activity: {activity.upper()}")
print(f"   Confidence: {confidence}%")

# Now let's check with MORE DISTANCE (original test which predicted STANDING)
print("\n" + "="*70)
print("STANDING POSE ANALYSIS (NORMALIZED 0-1)")
print("="*70)

standing_kps_normalized = [
    Keypoint('nose', 0.5, 0.15, 0.95),
    Keypoint('leftShoulder', 0.4, 0.30, 0.93),  # Shoulder at y=0.30
    Keypoint('rightShoulder', 0.6, 0.30, 0.93), # Shoulder at y=0.30
    Keypoint('leftHip', 0.42, 0.65, 0.90),      # Hip at y=0.65 (0.35 below!)
    Keypoint('rightHip', 0.58, 0.65, 0.90),     # Hip at y=0.65
    Keypoint('leftKnee', 0.42, 0.92, 0.88),     # Knee at y=0.92
    Keypoint('rightKnee', 0.58, 0.92, 0.88),    # Knee at y=0.92
]

metrics_standing = analyzer.extract_metrics(standing_kps_normalized)
print(f"\n1. Extracted metrics:")
print(f"   Shoulder-hip distance: {metrics_standing.shoulder_hip_distance:.2f}px")
print(f"   Height: {metrics_standing.height:.2f}px")
ratio_standing = metrics_standing.shoulder_hip_distance / metrics_standing.height if metrics_standing.height > 0 else 0
print(f"   Ratio: {ratio_standing:.3f}")
print(f"   Hip-knee ratio: {metrics_standing.hip_knee_distance / metrics_standing.height if metrics_standing.height > 0 else 0:.3f}")

result_standing = classifier.classify(standing_kps_normalized)
print(f"\n2. Classification result:")
activity_s, confidence_s = result_standing
print(f"   Activity: {activity_s.upper()}")
print(f"   Confidence: {confidence_s}%")

print("\n" + "="*70)
print("KEY INSIGHT")
print("="*70)
print("For sitting: hip-shoulder distance should be SMALL (close together)")
print("For standing: hip-shoulder distance should be LARGE (far apart)")
print("The previous 'sitting' test had hips only 0.16 units below shoulders")
print("which is TOO CLOSE - need hips to be ~0.22+ units below shoulders")
print("="*70)
