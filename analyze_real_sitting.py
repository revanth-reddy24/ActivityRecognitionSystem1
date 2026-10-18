#!/usr/bin/env python
"""
ANALYZE REAL SITTING POSTURES
============================
Study how humans actually sit:
- Forward lean (typing at desk)
- Slouch (relaxed in chair)
- Upright (formal sitting)
- Crossed legs
- Edge sitting
- Reclined

Goal: Understand what "sitting" really means beyond lab poses
"""

import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import Keypoint, AIActivityClassifier, PoseAnalyzer
import numpy as np

analyzer = PoseAnalyzer()
classifier = AIActivityClassifier()

# All poses normalized 0-1, scaled to 640x480 for analysis
sitting_poses = {
    'upright_formal': {
        'description': 'Formal upright sitting - back straight, chest open',
        'keypoints': [
            Keypoint('nose', 320, 100, 0.95),
            Keypoint('leftShoulder', 250, 150, 0.93),
            Keypoint('rightShoulder', 390, 150, 0.93),
            Keypoint('leftHip', 260, 220, 0.90),      # Hip slightly below shoulder (tight torso)
            Keypoint('rightHip', 380, 220, 0.90),
            Keypoint('leftKnee', 260, 320, 0.88),
            Keypoint('rightKnee', 380, 320, 0.88),
            Keypoint('leftAnkle', 260, 400, 0.85),
            Keypoint('rightAnkle', 380, 400, 0.85),
        ]
    },
    'forward_lean': {
        'description': 'Typing posture - lean forward, back bent',
        'keypoints': [
            Keypoint('nose', 320, 120, 0.95),
            Keypoint('leftShoulder', 240, 160, 0.93),  # Shoulders forward
            Keypoint('rightShoulder', 400, 160, 0.93),
            Keypoint('leftHip', 250, 210, 0.90),       # Hips close to shoulders (bent torso)
            Keypoint('rightHip', 390, 210, 0.90),
            Keypoint('leftKnee', 250, 310, 0.88),
            Keypoint('rightKnee', 390, 310, 0.88),
            Keypoint('leftAnkle', 250, 400, 0.85),
            Keypoint('rightAnkle', 390, 400, 0.85),
        ]
    },
    'slouch_relaxed': {
        'description': 'Slouching - relaxed, back curves, head forward',
        'keypoints': [
            Keypoint('nose', 320, 140, 0.95),          # Head lower, forward
            Keypoint('leftShoulder', 280, 170, 0.93),  # Shoulders hunched
            Keypoint('rightShoulder', 360, 170, 0.93),
            Keypoint('leftHip', 290, 215, 0.90),       # Hip close to shoulder (curved back)
            Keypoint('rightHip', 350, 215, 0.90),
            Keypoint('leftKnee', 290, 310, 0.88),
            Keypoint('rightKnee', 350, 310, 0.88),
            Keypoint('leftAnkle', 290, 400, 0.85),
            Keypoint('rightAnkle', 350, 400, 0.85),
        ]
    },
    'crossed_legs': {
        'description': 'Sitting with crossed legs - legs close together',
        'keypoints': [
            Keypoint('nose', 320, 110, 0.95),
            Keypoint('leftShoulder', 270, 160, 0.93),
            Keypoint('rightShoulder', 370, 160, 0.93),
            Keypoint('leftHip', 280, 220, 0.90),       # Hips compact
            Keypoint('rightHip', 360, 220, 0.90),
            Keypoint('leftKnee', 300, 290, 0.88),      # Knees close (crossed)
            Keypoint('rightKnee', 340, 290, 0.88),
            Keypoint('leftAnkle', 320, 350, 0.85),
            Keypoint('rightAnkle', 320, 350, 0.85),    # Ankles together
        ]
    },
    'edge_sitting': {
        'description': 'Sitting on edge of chair - dynamic, unstable',
        'keypoints': [
            Keypoint('nose', 320, 105, 0.95),
            Keypoint('leftShoulder', 260, 155, 0.93),
            Keypoint('rightShoulder', 380, 155, 0.93),
            Keypoint('leftHip', 265, 195, 0.90),       # Hip higher than formal (on edge)
            Keypoint('rightHip', 375, 195, 0.90),
            Keypoint('leftKnee', 265, 290, 0.88),
            Keypoint('rightKnee', 375, 290, 0.88),
            Keypoint('leftAnkle', 265, 370, 0.85),
            Keypoint('rightAnkle', 375, 370, 0.85),
        ]
    },
    'reclined_back': {
        'description': 'Leaning back in chair - relaxed, reclined',
        'keypoints': [
            Keypoint('nose', 320, 130, 0.95),          # Head back
            Keypoint('leftShoulder', 280, 180, 0.93),  # Shoulders back
            Keypoint('rightShoulder', 360, 180, 0.93),
            Keypoint('leftHip', 285, 240, 0.90),       # Hip far below shoulder (reclined)
            Keypoint('rightHip', 355, 240, 0.90),
            Keypoint('leftKnee', 285, 320, 0.88),      # Knees extended
            Keypoint('rightKnee', 355, 320, 0.88),
            Keypoint('leftAnkle', 285, 380, 0.85),
            Keypoint('rightAnkle', 355, 380, 0.85),
        ]
    },
}

# For comparison: standing pose
standing_pose = {
    'description': 'Standing upright',
    'keypoints': [
        Keypoint('nose', 320, 80, 0.95),
        Keypoint('leftShoulder', 270, 140, 0.93),
        Keypoint('rightShoulder', 370, 140, 0.93),
        Keypoint('leftHip', 280, 280, 0.90),          # Hip FAR below shoulder (standing)
        Keypoint('rightHip', 360, 280, 0.90),
        Keypoint('leftKnee', 280, 380, 0.88),
        Keypoint('rightKnee', 360, 380, 0.88),
        Keypoint('leftAnkle', 280, 460, 0.85),
        Keypoint('rightAnkle', 360, 460, 0.85),
    ]
}

print("="*90)
print("ANALYZING REAL SITTING POSTURES")
print("="*90)

results = []

print("\nSITTING VARIATIONS:")
print("-"*90)
for pose_name, pose_data in sitting_poses.items():
    kps = pose_data['keypoints']
    metrics = analyzer.extract_metrics(kps)
    activity, confidence = classifier.classify(kps)
    
    # Calculate key features
    sh_distance = metrics.shoulder_hip_distance
    height = metrics.height
    ratio = sh_distance / height if height > 0 else 0
    
    # Analyze back angle (from shoulder to hip to knee)
    ls_y = next((kp.y for kp in kps if kp.part == 'leftShoulder'), 0)
    lh_y = next((kp.y for kp in kps if kp.part == 'leftHip'), 0)
    lk_y = next((kp.y for kp in kps if kp.part == 'leftKnee'), 0)
    back_angle = abs(lh_y - ls_y) / abs(lk_y - lh_y) if (lk_y - lh_y) != 0 else 0
    
    results.append({
        'pose': pose_name,
        'description': pose_data['description'],
        'predicted': activity,
        'confidence': confidence,
        'sh_distance': sh_distance,
        'ratio': ratio,
        'back_angle': back_angle,
        'correct': activity.lower() == 'sitting'
    })
    
    status = '✓' if activity.lower() == 'sitting' else '✗'
    print(f"{status} {pose_name:20} → {activity:12} ({confidence}%)")
    print(f"   {pose_data['description']}")
    print(f"   Metrics: ratio={ratio:.3f}, back_angle={back_angle:.3f}, sh_dist={sh_distance:.1f}px")

print("\nSTANDING POSE (for comparison):")
print("-"*90)
kps = standing_pose['keypoints']
metrics = analyzer.extract_metrics(kps)
activity, confidence = classifier.classify(kps)
sh_distance = metrics.shoulder_hip_distance
height = metrics.height
ratio = sh_distance / height if height > 0 else 0
print(f"{'✓' if activity.lower() == 'standing' else '✗'} standing            → {activity:12} ({confidence}%)")
print(f"   {standing_pose['description']}")
print(f"   Metrics: ratio={ratio:.3f}, sh_dist={sh_distance:.1f}px")

# Summary
print("\n" + "="*90)
print("ANALYSIS SUMMARY")
print("="*90)
sitting_correct = sum(1 for r in results if r['correct'])
sitting_total = len(results)
print(f"Sitting accuracy: {sitting_correct}/{sitting_total} correct")
print(f"\nKey insight: Different sitting poses have different metrics:")
for r in results:
    print(f"  {r['pose']:20} ratio={r['ratio']:.3f}, back_angle={r['back_angle']:.3f}")

print("\n" + "="*90)
print("RECOMMENDATION")
print("="*90)
if sitting_correct < sitting_total:
    print(f"⚠ {sitting_total - sitting_correct} sitting poses NOT recognized as sitting!")
    print("ACTION: Expand sitting detection to handle more natural postures")
    print("        Look at: back angle, torso bend, hip-shoulder ratios")
else:
    print("✓ All sitting variations correctly recognized!")
print("="*90)
