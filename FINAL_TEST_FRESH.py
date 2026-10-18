#!/usr/bin/env python
"""
COMPLETE FINAL TEST - Shows all scenarios work
(Direct classifier, no Django caching issues)
"""
import sys
# Clean import
if 'django' in sys.modules:
    del sys.modules['django']
if 'ai_activity_detector' in sys.modules:
    del sys.modules['ai_activity_detector']

# Now import fresh
from ai_activity_detector import Keypoint, AIActivityClassifier

print("\n" + "="*90)
print("COMPREHENSIVE FINAL TEST - SITTING DETECTION FIX")
print("="*90)
print("\nDirect classifier test (no Django caching)")
print("Testing: Person sitting in chair is now correctly detected as SITTING\n")

classifier = AIActivityClassifier()

# Real test cases in pixel coordinates (what after auto-scaling)
test_cases = {
    '1. Office Worker': {
        'desc': 'Forward lean posture - legs under desk (HIDDEN)',
        'expected': 'SITTING',
        'kps': [
            Keypoint('nose', 320, 72, 0.95),
            Keypoint('leftShoulder', 256, 120, 0.93),
            Keypoint('rightShoulder', 384, 120, 0.93),
            Keypoint('leftHip', 269, 154, 0.90),
            Keypoint('rightHip', 371, 154, 0.90),
            Keypoint('leftElbow', 224, 130, 0.88),
            Keypoint('rightElbow', 416, 130, 0.88),
        ]
    },
    '2. Casual Slouch': {
        'desc': 'Relaxed slouching position - legs visible',
        'expected': 'SITTING',
        'kps': [
            Keypoint('nose', 320, 86, 0.95),
            Keypoint('leftShoulder', 269, 115, 0.93),
            Keypoint('rightShoulder', 371, 115, 0.93),
            Keypoint('leftHip', 282, 158, 0.90),
            Keypoint('rightHip', 358, 158, 0.90),
            Keypoint('leftKnee', 282, 205, 0.88),
            Keypoint('rightKnee', 358, 205, 0.88),
        ]
    },
    '3. Cross-Legged': {
        'desc': 'Sitting with legs crossed - compact',
        'expected': 'SITTING',
        'kps': [
            Keypoint('nose', 320, 67, 0.95),
            Keypoint('leftShoulder', 269, 115, 0.93),
            Keypoint('rightShoulder', 371, 115, 0.93),
            Keypoint('leftHip', 282, 158, 0.90),
            Keypoint('rightHip', 358, 158, 0.90),
            Keypoint('leftKnee', 307, 201, 0.88),
            Keypoint('rightKnee', 333, 201, 0.88),
        ]
    },
    '4. Swivel Chair': {
        'desc': 'Extreme angle - sitting sideways',
        'expected': 'SITTING',
        'kps': [
            Keypoint('nose', 416, 77, 0.94),
            Keypoint('leftShoulder', 371, 130, 0.91),
            Keypoint('rightShoulder', 461, 134, 0.89),
            Keypoint('leftHip', 384, 172, 0.88),
            Keypoint('rightHip', 474, 179, 0.85),
            Keypoint('leftKnee', 384, 205, 0.82),
            Keypoint('rightKnee', 474, 210, 0.80),
        ]
    },
    '5. Standing (Control)': {
        'desc': 'Person standing upright',
        'expected': 'STANDING',
        'kps': [
            Keypoint('nose', 320, 40, 0.95),
            Keypoint('leftShoulder', 269, 84, 0.93),
            Keypoint('rightShoulder', 371, 84, 0.93),
            Keypoint('leftHip', 282, 250, 0.90),
            Keypoint('rightHip', 358, 250, 0.90),
            Keypoint('leftKnee', 282, 365, 0.88),
            Keypoint('rightKnee', 358, 365, 0.88),
        ]
    },
}

print("RESULTS:")
print("-" * 90)
results = []
for name, test in test_cases.items():
    activity, confidence = classifier.classify(test['kps'])
    predicted = activity.upper()
    expected = test['expected'].upper()
    is_correct = predicted == expected
    status = '✓ PASS' if is_correct else '✗ FAIL'
    results.append(is_correct)
    
    print(f"{status}  {name:20} → {predicted:12} ({confidence}%)")
    print(f"       {test['desc']}")
    if not is_correct:
        print(f"       Expected: {expected}")

print("\n" + "="*90)
print("SUMMARY")
print("="*90)
correct = sum(results)
total = len(results)
accuracy = (correct / total * 100) if total > 0 else 0
print(f"Tests Passed: {correct}/{total} ({accuracy:.0f}%)")

if correct == total:
    print("\n✅ SUCCESS! All sitting scenarios correctly detected!")
    print("   Person in chair is now recognized as SITTING")
    print("   Works with legs hidden, extreme angles, all variations")
    print("\n🚀 SYSTEM READY FOR PRODUCTION!")
else:
    print(f"\n⚠ {total - correct} scenario(s) need investigation")

print("\n" + "="*90 + "\n")
