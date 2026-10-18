#!/usr/bin/env python
"""
Realistic sleeping poses for better testing.
Key insight: when lying down, the person's bounding box should be WIDE (many keypoints spread horizontally)
and SHORT (not many keypoints vertically spread).
"""

# Sleeping pose 1: Lying flat on back (classic sleeping)
# Nose at one end, feet at other (horizontally separated)
sleeping_back = [
    {'part': 'nose', 'position': {'x': 50, 'y': 100}, 'score': 0.9},
    {'part': 'leftShoulder', 'position': {'x': 60, 'y': 110}, 'score': 0.85},
    {'part': 'rightShoulder', 'position': {'x': 80, 'y': 110}, 'score': 0.85},
    {'part': 'leftHip', 'position': {'x': 70, 'y': 115}, 'score': 0.8},
    {'part': 'rightHip', 'position': {'x': 90, 'y': 115}, 'score': 0.8},
    {'part': 'leftKnee', 'position': {'x': 100, 'y': 120}, 'score': 0.75},
    {'part': 'rightKnee', 'position': {'x': 120, 'y': 120}, 'score': 0.75},
]

# Sleeping pose 2: Lying on side
# Body stretched horizontally, all Y values similar
sleeping_side = [
    {'part': 'nose', 'position': {'x': 40, 'y': 120}, 'score': 0.9},
    {'part': 'leftShoulder', 'position': {'x': 60, 'y': 115}, 'score': 0.85},
    {'part': 'rightShoulder', 'position': {'x': 80, 'y': 125}, 'score': 0.85},
    {'part': 'leftHip', 'position': {'x': 100, 'y': 120}, 'score': 0.8},
    {'part': 'rightHip', 'position': {'x': 120, 'y': 120}, 'score': 0.8},
    {'part': 'leftKnee', 'position': {'x': 140, 'y': 125}, 'score': 0.75},
    {'part': 'rightKnee', 'position': {'x': 160, 'y': 115}, 'score': 0.75},
]

# Sleeping pose 3: Fetal position (curled up)
# Compact, with all points close together
sleeping_fetal = [
    {'part': 'nose', 'position': {'x': 100, 'y': 100}, 'score': 0.9},
    {'part': 'leftShoulder', 'position': {'x': 95, 'y': 105}, 'score': 0.85},
    {'part': 'rightShoulder', 'position': {'x': 105, 'y': 105}, 'score': 0.85},
    {'part': 'leftHip', 'position': {'x': 100, 'y': 115}, 'score': 0.8},
    {'part': 'rightHip', 'position': {'x': 110, 'y': 115}, 'score': 0.8},
    {'part': 'leftKnee', 'position': {'x': 95, 'y': 125}, 'score': 0.75},
    {'part': 'rightKnee', 'position': {'x': 105, 'y': 125}, 'score': 0.75},
]

print("Pose 1 (lying flat on back):")
xs = [k['position']['x'] for k in sleeping_back]
ys = [k['position']['y'] for k in sleeping_back]
w = max(xs) - min(xs)
h = max(ys) - min(ys)
print(f"  Width: {w}, Height: {h}, Aspect: {w/h:.2f}")
print(f"  X range: {min(xs)} to {max(xs)}")
print(f"  Y range: {min(ys)} to {max(ys)}")

print("\nPose 2 (lying on side):")
xs = [k['position']['x'] for k in sleeping_side]
ys = [k['position']['y'] for k in sleeping_side]
w = max(xs) - min(xs)
h = max(ys) - min(ys)
print(f"  Width: {w}, Height: {h}, Aspect: {w/h:.2f}")
print(f"  X range: {min(xs)} to {max(xs)}")
print(f"  Y range: {min(ys)} to {max(ys)}")

print("\nPose 3 (fetal):")
xs = [k['position']['x'] for k in sleeping_fetal]
ys = [k['position']['y'] for k in sleeping_fetal]
w = max(xs) - min(xs)
h = max(ys) - min(ys)
print(f"  Width: {w}, Height: {h}, Aspect: {w/h:.2f}")
print(f"  X range: {min(xs)} to {max(xs)}")
print(f"  Y range: {min(ys)} to {max(ys)}")
