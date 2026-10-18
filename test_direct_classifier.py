#!/usr/bin/env python
"""
Direct test without Django HTTP - verify the fix works
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import Keypoint, AIActivityClassifier

classifier = AIActivityClassifier()

test_cases = {
    'Office Worker': [
        Keypoint('nose', 320, 72, 0.95),
        Keypoint('leftShoulder', 256, 120, 0.93),
        Keypoint('rightShoulder', 384, 120, 0.93),
        Keypoint('leftHip', 269, 154, 0.90),
        Keypoint('rightHip', 371, 154, 0.90),
        Keypoint('leftElbow', 224, 130, 0.88),
        Keypoint('rightElbow', 416, 130, 0.88),
    ],
    'Cross-Legged': [
        Keypoint('nose', 320, 67, 0.95),
        Keypoint('leftShoulder', 269, 115, 0.93),
        Keypoint('rightShoulder', 371, 115, 0.93),
        Keypoint('leftHip', 282, 158, 0.90),
        Keypoint('rightHip', 358, 158, 0.90),
        Keypoint('leftKnee', 307, 201, 0.88),
        Keypoint('rightKnee', 333, 201, 0.88),
    ],
}

print("="*70)
print("DIRECT CLASSIFIER TEST")
print("="*70)

for name, kps in test_cases.items():
    activity, confidence = classifier.classify(kps)
    expected = 'SITTING'
    got = activity.upper()
    status = '✓' if got == expected else '✗'
    print(f"{status} {name:20} → {got:12} ({confidence}%) [expected {expected}]")

print("="*70)
