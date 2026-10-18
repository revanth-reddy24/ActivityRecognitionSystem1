#!/usr/bin/env python
"""Quick test of updated thresholds"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import AIActivityClassifier, Keypoint

classifier = AIActivityClassifier()

# SITTING
sitting = [
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

# STANDING
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

s_pred, s_conf = classifier.classify(sitting)
st_pred, st_conf = classifier.classify(standing)

print(f'Sitting: {s_pred.upper()} ({s_conf}%)')
print(f'Standing: {st_pred.upper()} ({st_conf}%)')
status = 'PASS' if s_pred == 'sitting' and st_pred == 'standing' else 'FAIL'
print(f'Status: {status}')
