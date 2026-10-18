#!/usr/bin/env python
"""
TEST CHALLENGING REAL-WORLD SCENARIOS
====================================
These are the tricky cases where sitting might be misclassified:
- Partial occlusion (someone in front)
- Extreme camera angles
- Missing body parts
- Side-sitting
- Hunched over
- Legs hidden under table
"""

import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_activity_detector import Keypoint, AIActivityClassifier, PoseAnalyzer

analyzer = PoseAnalyzer()
classifier = AIActivityClassifier()

challenging_poses = {
    'partial_occlusion_legs_hidden': {
        'description': 'Legs completely hidden under table (common office)',
        'keypoints': [
            Keypoint('nose', 320, 110, 0.95),
            Keypoint('leftShoulder', 260, 160, 0.93),
            Keypoint('rightShoulder', 380, 160, 0.93),
            Keypoint('leftHip', 270, 220, 0.90),
            Keypoint('rightHip', 370, 220, 0.90),
            # Knees and ankles are MISSING/NOT DETECTED
            Keypoint('leftEye', 300, 95, 0.92),
            Keypoint('rightEye', 340, 95, 0.92),
        ]
    },
    'extreme_angle_side_sitting': {
        'description': 'Extreme angle - person rotated, sitting sideways to camera',
        'keypoints': [
            Keypoint('nose', 400, 120, 0.94),         # Nose off to side
            Keypoint('leftShoulder', 380, 165, 0.91), # Only one shoulder visible
            Keypoint('rightShoulder', 400, 168, 0.89),# Other shoulder partially visible
            Keypoint('leftHip', 390, 230, 0.88),      # Hip also to side
            Keypoint('rightHip', 405, 235, 0.85),
            Keypoint('leftKnee', 390, 310, 0.82),
            Keypoint('rightKnee', 405, 315, 0.80),
            Keypoint('leftElbow', 350, 190, 0.88),
            Keypoint('rightElbow', 410, 185, 0.86),
        ]
    },
    'hunched_extreme_forward': {
        'description': 'Extreme forward hunch - face near table, back very bent',
        'keypoints': [
            Keypoint('nose', 300, 180, 0.93),         # Face way down
            Keypoint('leftShoulder', 280, 170, 0.92),
            Keypoint('rightShoulder', 320, 172, 0.92),
            Keypoint('leftHip', 290, 190, 0.90),      # Hip VERY close to shoulder
            Keypoint('rightHip', 310, 192, 0.90),
            Keypoint('leftKnee', 290, 250, 0.85),
            Keypoint('rightKnee', 310, 252, 0.85),
            Keypoint('leftElbow', 260, 175, 0.88),    # Elbows on table
            Keypoint('rightElbow', 340, 175, 0.88),
        ]
    },
    'one_leg_extended_sitting': {
        'description': 'One leg extended (relaxed sitting, stretching)',
        'keypoints': [
            Keypoint('nose', 320, 100, 0.95),
            Keypoint('leftShoulder', 260, 150, 0.93),
            Keypoint('rightShoulder', 380, 150, 0.93),
            Keypoint('leftHip', 270, 210, 0.90),
            Keypoint('rightHip', 370, 210, 0.90),
            Keypoint('leftKnee', 270, 280, 0.88),     # Left leg bent, normal
            Keypoint('rightKnee', 450, 300, 0.87),    # Right leg EXTENDED far
            Keypoint('rightAnkle', 500, 350, 0.85),
        ]
    },
    'very_low_camera_angle': {
        'description': 'Camera very low - looking up at person sitting (distorted)',
        'keypoints': [
            Keypoint('nose', 320, 350, 0.92),         # Nose very low in frame
            Keypoint('leftShoulder', 270, 280, 0.91),
            Keypoint('rightShoulder', 370, 280, 0.91),
            Keypoint('leftHip', 280, 240, 0.89),      # Hip ABOVE shoulder (perspective!)
            Keypoint('rightHip', 360, 240, 0.89),
            Keypoint('leftKnee', 280, 150, 0.85),     # Knees way up
            Keypoint('rightKnee', 360, 150, 0.85),
            Keypoint('leftAnkle', 280, 50, 0.80),
            Keypoint('rightAnkle', 360, 50, 0.80),
        ]
    },
    'swivel_chair_reclined_high': {
        'description': 'In swivel chair, reclined back, feet up on table',
        'keypoints': [
            Keypoint('nose', 320, 140, 0.94),
            Keypoint('leftShoulder', 270, 190, 0.92),
            Keypoint('rightShoulder', 370, 190, 0.92),
            Keypoint('leftHip', 280, 280, 0.90),      # Hip FAR below shoulder
            Keypoint('rightHip', 360, 280, 0.90),
            Keypoint('leftKnee', 280, 320, 0.88),     # Knees high
            Keypoint('rightKnee', 360, 320, 0.88),
            Keypoint('leftAnkle', 280, 240, 0.85),    # Ankles UP on table
            Keypoint('rightAnkle', 360, 240, 0.85),
        ]
    },
}

print("="*90)
print("TESTING CHALLENGING REAL-WORLD SCENARIOS")
print("="*90)

challenging_correct = 0
challenging_total = len(challenging_poses)

print("\nCHALLENGING POSES:")
print("-"*90)
for pose_name, pose_data in challenging_poses.items():
    kps = pose_data['keypoints']
    try:
        activity, confidence = classifier.classify(kps)
        
        is_sitting = activity.lower() in ['sitting']
        if is_sitting:
            challenging_correct += 1
            status = '✓ PASS'
        else:
            status = f'✗ FAIL (got {activity})'
        
        print(f"{status:12} {pose_name:35}")
        print(f"              {pose_data['description']}")
        print(f"              Prediction: {activity} ({confidence}%)")
    except Exception as e:
        print(f"✗ ERROR  {pose_name:35}")
        print(f"         {str(e)[:60]}")

print("\n" + "="*90)
print("RESULTS")
print("="*90)
print(f"Challenging scenarios: {challenging_correct}/{challenging_total} correct")

if challenging_correct == challenging_total:
    print("✓ ALL CHALLENGING CASES HANDLED!")
else:
    missing = challenging_total - challenging_correct
    print(f"⚠ {missing} challenging cases NOT recognized as sitting")
    print("\nThese cases need special handling:")
    print("  1. Detect when keypoints are missing (legs hidden)")
    print("  2. Use shoulders and hips alone when legs unavailable")
    print("  3. Handle extreme camera angles better")
    print("  4. Consider torso angle, not just distances")

print("="*90)
