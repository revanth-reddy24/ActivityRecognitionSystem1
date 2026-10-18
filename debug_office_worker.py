#!/usr/bin/env python
"""
Debug: Why is office worker (legs hidden) predicting SLEEPING?
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import Keypoint, AIActivityClassifier, PoseAnalyzer

# Office worker (legs hidden) - normalized coordinates
office_kps = [
    Keypoint('nose', 320, 72, 0.95),
    Keypoint('leftShoulder', 256, 120, 0.93),
    Keypoint('rightShoulder', 384, 120, 0.93),
    Keypoint('leftHip', 269, 154, 0.90),
    Keypoint('rightHip', 371, 154, 0.90),
    Keypoint('leftElbow', 224, 130, 0.88),
    Keypoint('rightElbow', 416, 130, 0.88),
]

analyzer = PoseAnalyzer()
classifier = AIActivityClassifier()

print("="*70)
print("DEBUGGING: Office Worker (Legs Hidden)")
print("="*70)

metrics = analyzer.extract_metrics(office_kps)
print(f"\nMetrics:")
print(f"  Width: {metrics.width:.1f}px")
print(f"  Height: {metrics.height:.1f}px")
print(f"  Aspect ratio: {metrics.aspect_ratio:.3f}")
print(f"  Shoulder-hip distance: {metrics.shoulder_hip_distance:.1f}px")

# Check what triggers SLEEPING
print(f"\nSLEEPING checks:")
print(f"  Aspect ratio > 1.3? {metrics.aspect_ratio} > 1.3 = {metrics.aspect_ratio > 1.3}")
print(f"  Shoulder-hip < 15 AND height < 120?")
print(f"    - Shoulder-hip: {metrics.shoulder_hip_distance:.1f} < 15 = {metrics.shoulder_hip_distance < 15}")
print(f"    - Height: {metrics.height:.1f} < 120 = {metrics.height < 120}")
print(f"    - Both true? {metrics.shoulder_hip_distance < 15 and metrics.height < 120}")

result = classifier.classify(office_kps)
print(f"\nClassification: {result[0].upper()} ({result[1]}%)")

print("\n" + "="*70)
print("ISSUE: Aspect ratio > 1.3 triggers SLEEPING incorrectly!")
print("REASON: When legs hidden, width is large relative to height")
print("="*70)
