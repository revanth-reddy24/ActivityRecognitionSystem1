#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Test the classifier directly without the Django request/response cycle

def _classify_pose_from_keypoints(keypoints):
    """Basic heuristic classifier for a single-frame pose."""
    kp = {k['part']: k for k in keypoints}
    scores = [k.get('score', 0) for k in keypoints]
    avg_score = sum(scores) / (len(scores) or 1)

    if avg_score < 0.35:
        return 'unusual', int(avg_score * 100)

    def _y(p):
        return kp.get(p, {}).get('position', {}).get('y', 0)

    def _x(p):
        return kp.get(p, {}).get('position', {}).get('x', 0)

    xs = [k.get('position', {}).get('x', 0) for k in keypoints if k.get('position')]
    ys = [k.get('position', {}).get('y', 0) for k in keypoints if k.get('position')]
    min_x, max_x = (min(xs), max(xs)) if xs else (0, 0)
    min_y, max_y = (min(ys), max(ys)) if ys else (0, 0)
    width = max_x - min_x
    height = max_y - min_y

    nose_y = _y('nose')
    left_shoulder_y = _y('leftShoulder')
    right_shoulder_y = _y('rightShoulder')
    left_hip_y = _y('leftHip')
    right_hip_y = _y('rightHip')
    left_knee_y = _y('leftKnee')
    right_knee_y = _y('rightKnee')

    shoulders_y = (left_shoulder_y + right_shoulder_y) / 2 if left_shoulder_y and right_shoulder_y else None
    hips_y = (left_hip_y + right_hip_y) / 2 if left_hip_y and right_hip_y else None
    knees_y = (left_knee_y + right_knee_y) / 2 if left_knee_y and right_knee_y else None

    print(f"  DEBUG: width={width}, height={height}, aspect_ratio={width/height if height > 0 else 0:.2f}")
    print(f"  DEBUG: shoulders_y={shoulders_y}, hips_y={hips_y}, knees_y={knees_y}")
    if shoulders_y and hips_y:
        print(f"  DEBUG: shoulder_hip_gap={abs(shoulders_y - hips_y)}")

    try:
        if height > 0 and width > 0:
            aspect_ratio = width / height if height > 0 else 0
            
            if shoulders_y and hips_y:
                shoulder_hip_gap = abs(shoulders_y - hips_y)
                
                if aspect_ratio > 1.5:
                    return 'sleeping', min(99, int(avg_score * 100 + 20))
                
                if shoulder_hip_gap < 15 and height < 100:
                    return 'sleeping', min(98, int(avg_score * 100 + 18))
                
                if nose_y and hips_y and nose_y > hips_y + 40:
                    return 'falling', min(95, int(avg_score * 100 + 10))
                
                if shoulder_hip_gap < 25 and knees_y:
                    knee_hip_gap = abs(knees_y - hips_y)
                    if knee_hip_gap < 50:
                        return 'sitting', min(95, int(avg_score * 100 + 12))
                
                if shoulder_hip_gap > 35 and knees_y and knees_y > hips_y + 25:
                    return 'standing', min(95, int(avg_score * 100 + 8))
        
    except Exception as e:
        print(f"  ERROR: {e}")

    return 'walking', int(avg_score * 100 * 0.9)

# Test cases
print("=" * 80)
print("Debug: Analyzing Pose Geometry")
print("=" * 80)

print("\n[Test 2] Lying on side:")
sleeping_pose_2 = [
    {'part': 'nose', 'position': {'x': 100, 'y': 150}, 'score': 0.9},
    {'part': 'leftShoulder', 'position': {'x': 80, 'y': 140}, 'score': 0.85},
    {'part': 'rightShoulder', 'position': {'x': 120, 'y': 160}, 'score': 0.85},
    {'part': 'leftHip', 'position': {'x': 85, 'y': 170}, 'score': 0.8},
    {'part': 'rightHip', 'position': {'x': 115, 'y': 180}, 'score': 0.8},
    {'part': 'leftKnee', 'position': {'x': 90, 'y': 200}, 'score': 0.75},
    {'part': 'rightKnee', 'position': {'x': 110, 'y': 210}, 'score': 0.75},
]
result = _classify_pose_from_keypoints(sleeping_pose_2)
print(f"  Result: {result}")

print("\n[Test 3] Fetal position:")
sleeping_pose_3 = [
    {'part': 'nose', 'position': {'x': 100, 'y': 180}, 'score': 0.9},
    {'part': 'leftShoulder', 'position': {'x': 85, 'y': 185}, 'score': 0.85},
    {'part': 'rightShoulder', 'position': {'x': 115, 'y': 185}, 'score': 0.85},
    {'part': 'leftHip', 'position': {'x': 80, 'y': 200}, 'score': 0.8},
    {'part': 'rightHip', 'position': {'x': 120, 'y': 200}, 'score': 0.8},
    {'part': 'leftKnee', 'position': {'x': 75, 'y': 215}, 'score': 0.75},
    {'part': 'rightKnee', 'position': {'x': 125, 'y': 215}, 'score': 0.75},
]
result = _classify_pose_from_keypoints(sleeping_pose_3)
print(f"  Result: {result}")
