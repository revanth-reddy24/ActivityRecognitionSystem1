"""
Enhanced Activity Detection System
Uses pose keypoints + body measurements + motion patterns for accurate classification
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ActivityType(Enum):
    """Activity classification types"""
    WALKING = 'walking'
    RUNNING = 'running'
    SITTING = 'sitting'
    STANDING = 'standing'
    FALLING = 'falling'
    UNUSUAL = 'unusual'
    COOKING = 'cooking'
    SLEEPING = 'sleeping'
    EXERCISING = 'exercising'


@dataclass
class Keypoint:
    """Single body keypoint"""
    part: str
    x: float
    y: float
    score: float

    @classmethod
    def from_dict(cls, data: dict):
        position = data.get('position', {})
        return cls(
            part=data.get('part', ''),
            x=position.get('x', 0),
            y=position.get('y', 0),
            score=data.get('score', 0)
        )


@dataclass
class BodyMetrics:
    """Body measurements for activity classification"""
    # Vertical measurements
    height: float  # pixel distance from top to bottom
    width: float  # pixel width of body
    shoulder_to_hip: float  # distance from shoulders to hips
    hip_to_knee: float  # distance from hips to knees
    knee_to_ankle: float  # distance from knees to ankles
    
    # Angles and aspect ratios
    aspect_ratio: float  # width / height
    body_angle: float  # tilt of body (0=upright, 90=horizontal)
    arm_spread: float  # distance between wrists
    leg_spread: float  # distance between ankles
    
    # Confidence
    avg_confidence: float  # average keypoint confidence


class PoseAnalyzer:
    """Analyze pose keypoints to extract body metrics"""

    # Standard keypoint names
    KEYPOINTS = {
        'nose', 'neck', 'rightShoulder', 'rightElbow', 'rightWrist',
        'leftShoulder', 'leftElbow', 'leftWrist', 'rightHip', 'rightKnee',
        'rightAnkle', 'leftHip', 'leftKnee', 'leftAnkle'
    }

    def __init__(self, keypoints_list: List[dict]):
        """Initialize with list of keypoint dicts"""
        self.keypoints: Dict[str, Keypoint] = {}
        for kp_dict in keypoints_list:
            kp = Keypoint.from_dict(kp_dict)
            if kp.part:
                self.keypoints[kp.part] = kp

    def get_point(self, name: str) -> Optional[Keypoint]:
        """Get a keypoint by name, return None if not found or low confidence"""
        kp = self.keypoints.get(name)
        if kp and kp.score > 0.1:  # minimum confidence threshold
            return kp
        return None

    def distance(self, p1_name: str, p2_name: str) -> float:
        """Distance between two keypoints"""
        p1 = self.get_point(p1_name)
        p2 = self.get_point(p2_name)
        if not p1 or not p2:
            return 0
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return (dx*dx + dy*dy) ** 0.5

    def vertical_distance(self, p1_name: str, p2_name: str) -> float:
        """Vertical distance between two points (Y-axis only)"""
        p1 = self.get_point(p1_name)
        p2 = self.get_point(p2_name)
        if not p1 or not p2:
            return 0
        return abs(p1.y - p2.y)

    def angle_between(self, p1_name: str, p2_name: str, p3_name: str) -> float:
        """Calculate angle at p2 formed by p1-p2-p3 (in degrees)"""
        p1 = self.get_point(p1_name)
        p2 = self.get_point(p2_name)
        p3 = self.get_point(p3_name)
        
        if not all([p1, p2, p3]):
            return 0

        # Vectors from p2 to p1 and p2 to p3
        v1 = (p1.x - p2.x, p1.y - p2.y)
        v2 = (p3.x - p2.x, p3.y - p2.y)

        # Dot product and magnitudes
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        mag1 = (v1[0]**2 + v1[1]**2) ** 0.5
        mag2 = (v2[0]**2 + v2[1]**2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0

        cos_angle = dot / (mag1 * mag2)
        cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
        
        import math
        angle_rad = math.acos(cos_angle)
        return math.degrees(angle_rad)

    def extract_metrics(self) -> BodyMetrics:
        """Extract all body metrics from keypoints"""
        # Get all visible points
        visible_points = [kp for kp in self.keypoints.values() if kp.score > 0.1]
        
        if not visible_points:
            return BodyMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        # Bounding box
        xs = [p.x for p in visible_points]
        ys = [p.y for p in visible_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x
        height = max_y - min_y

        # Vertical measurements
        shoulder_to_hip = self.vertical_distance('neck', 'rightHip')
        if shoulder_to_hip == 0:
            shoulder_to_hip = self.vertical_distance('rightShoulder', 'rightHip')

        hip_to_knee = self.vertical_distance('rightHip', 'rightKnee')
        if hip_to_knee == 0:
            hip_to_knee = self.vertical_distance('leftHip', 'leftKnee')

        knee_to_ankle = self.vertical_distance('rightKnee', 'rightAnkle')
        if knee_to_ankle == 0:
            knee_to_ankle = self.vertical_distance('leftKnee', 'leftAnkle')

        # Arm and leg spread
        arm_spread = self.distance('rightWrist', 'leftWrist')
        leg_spread = self.distance('rightAnkle', 'leftAnkle')

        # Aspect ratio and body angle
        aspect_ratio = width / height if height > 0 else 0
        
        # Body angle: check if body is more horizontal than vertical
        # If width/height > 1.2, person is likely lying down
        if aspect_ratio > 1.2:
            body_angle = 90  # Horizontal
        elif aspect_ratio < 0.6:
            body_angle = 0  # Vertical/upright
        else:
            body_angle = 45  # Intermediate angle

        # Average confidence
        scores = [kp.score for kp in visible_points]
        avg_confidence = sum(scores) / len(scores) if scores else 0

        return BodyMetrics(
            height=height,
            width=width,
            shoulder_to_hip=shoulder_to_hip,
            hip_to_knee=hip_to_knee,
            knee_to_ankle=knee_to_ankle,
            aspect_ratio=aspect_ratio,
            body_angle=body_angle,
            arm_spread=arm_spread,
            leg_spread=leg_spread,
            avg_confidence=avg_confidence
        )


class MotionAnalyzer:
    """Analyze motion patterns from pose history"""

    def __init__(self, history: List[List[dict]]):
        """Initialize with list of pose frames"""
        self.analyzers = [PoseAnalyzer(frame) for frame in history]
        self.history = history

    def calculate_displacement(self, point_name: str) -> float:
        """Calculate vertical displacement of a point across frames"""
        if len(self.analyzers) < 2:
            return 0

        first_y = None
        last_y = None

        for analyzer in self.analyzers:
            kp = analyzer.get_point(point_name)
            if kp:
                if first_y is None:
                    first_y = kp.y
                last_y = kp.y

        if first_y is None or last_y is None:
            return 0
        
        return abs(last_y - first_y)

    def has_consistent_motion(self) -> bool:
        """Check if there's consistent motion across frames"""
        hip_displacement = self.calculate_displacement('rightHip')
        return hip_displacement > 5  # More than 5 pixels movement

    def calculate_motion_variance(self) -> float:
        """Calculate variance in hip position across frames"""
        hip_ys = []
        for analyzer in self.analyzers:
            kp = analyzer.get_point('rightHip')
            if kp:
                hip_ys.append(kp.y)

        if len(hip_ys) < 2:
            return 0

        mean = sum(hip_ys) / len(hip_ys)
        variance = sum((y - mean) ** 2 for y in hip_ys) / len(hip_ys)
        return variance ** 0.5  # Standard deviation


class ActivityClassifier:
    """Classify activities from pose analysis"""

    def __init__(self, pose_keypoints: List[dict], history: Optional[List[List[dict]]] = None):
        """
        Initialize classifier
        
        Args:
            pose_keypoints: Single frame pose keypoints
            history: Optional list of previous frames for motion analysis
        """
        self.analyzer = PoseAnalyzer(pose_keypoints)
        self.metrics = self.analyzer.extract_metrics()
        
        self.motion_analyzer = None
        if history and len(history) > 1:
            # Include current frame in history for analysis
            full_history = history + [pose_keypoints]
            self.motion_analyzer = MotionAnalyzer(full_history)

    def classify(self) -> Tuple[str, int]:
        """
        Classify activity and return (activity_type, confidence_score)
        
        Returns:
            Tuple of (activity_label, confidence_percentage)
        """
        # If detection quality is too low, mark as unusual
        if self.metrics.avg_confidence < 0.3:
            return ActivityType.UNUSUAL.value, int(self.metrics.avg_confidence * 100)

        # Priority-ordered classification logic
        
        # 1. SLEEPING - Person is lying down (wide aspect ratio or very compact)
        if self.metrics.aspect_ratio > 1.3:
            confidence = min(99, int(self.metrics.avg_confidence * 100 + 25))
            return ActivityType.SLEEPING.value, confidence

        # Very compact sleeping position (fetal)
        if self.metrics.shoulder_to_hip < 15 and self.metrics.height < 100:
            confidence = min(98, int(self.metrics.avg_confidence * 100 + 20))
            return ActivityType.SLEEPING.value, confidence

        # 2. FALLING - Nose well below hips or sudden downward motion
        if self.motion_analyzer:
            nose_disp = self.motion_analyzer.calculate_displacement('nose')
            if nose_disp > 30:
                confidence = min(95, int(self.metrics.avg_confidence * 100 + 15))
                return ActivityType.FALLING.value, confidence

        # 3. SITTING - Small shoulder-hip gap, knees at similar level
        if self.metrics.shoulder_to_hip < 25 and self.metrics.hip_to_knee > 0:
            # Check if knees are close to body (sitting)
            if self.metrics.knee_to_ankle < 80:
                if self.motion_analyzer:
                    motion = self.motion_analyzer.calculate_motion_variance()
                    if motion < 8:  # Low motion = sitting
                        confidence = min(96, int(self.metrics.avg_confidence * 100 + 12))
                        return ActivityType.SITTING.value, confidence

        # 4. STANDING - Tall posture, well-aligned body
        if (self.metrics.shoulder_to_hip > 35 and 
            self.metrics.hip_to_knee > 20 and 
            self.metrics.knee_to_ankle > 15):
            
            if self.motion_analyzer:
                motion = self.motion_analyzer.calculate_motion_variance()
                if motion < 10:  # Low motion = standing still
                    confidence = min(94, int(self.metrics.avg_confidence * 100 + 8))
                    return ActivityType.STANDING.value, confidence

        # 5. RUNNING - Large stride, high motion
        if self.motion_analyzer and self.motion_analyzer.has_consistent_motion():
            motion = self.motion_analyzer.calculate_motion_variance()
            if motion > 15:  # High motion variation
                confidence = min(92, int(self.metrics.avg_confidence * 100 + 10))
                return ActivityType.RUNNING.value, confidence

        # 6. WALKING - Moderate motion, good posture
        if self.motion_analyzer and self.motion_analyzer.has_consistent_motion():
            confidence = min(90, int(self.metrics.avg_confidence * 100 + 5))
            return ActivityType.WALKING.value, confidence

        # 7. EXERCISING - Large arm/leg spread, dynamic posture
        if (self.metrics.arm_spread > 100 or self.metrics.leg_spread > 80):
            confidence = min(88, int(self.metrics.avg_confidence * 100 + 8))
            return ActivityType.EXERCISING.value, confidence

        # Default: walking
        confidence = int(self.metrics.avg_confidence * 100 * 0.85)
        return ActivityType.WALKING.value, max(40, confidence)

    def get_activity_details(self) -> Dict:
        """Get detailed classification information"""
        activity, confidence = self.classify()
        
        return {
            'activity': activity,
            'confidence': confidence,
            'metrics': {
                'height': round(self.metrics.height, 1),
                'width': round(self.metrics.width, 1),
                'aspect_ratio': round(self.metrics.aspect_ratio, 2),
                'body_angle': round(self.metrics.body_angle, 1),
                'shoulder_to_hip': round(self.metrics.shoulder_to_hip, 1),
                'arm_spread': round(self.metrics.arm_spread, 1),
                'leg_spread': round(self.metrics.leg_spread, 1),
                'avg_keypoint_confidence': round(self.metrics.avg_confidence, 2),
            },
            'motion': {
                'has_motion': self.motion_analyzer.has_consistent_motion() if self.motion_analyzer else False,
                'motion_variance': round(self.motion_analyzer.calculate_motion_variance(), 2) if self.motion_analyzer else 0,
            }
        }


# Example usage and testing
if __name__ == '__main__':
    # Example pose data
    example_pose = [
        {'part': 'nose', 'position': {'x': 100, 'y': 50}, 'score': 0.95},
        {'part': 'neck', 'position': {'x': 100, 'y': 70}, 'score': 0.92},
        {'part': 'rightShoulder', 'position': {'x': 80, 'y': 70}, 'score': 0.90},
        {'part': 'leftShoulder', 'position': {'x': 120, 'y': 70}, 'score': 0.91},
        {'part': 'rightHip', 'position': {'x': 85, 'y': 130}, 'score': 0.88},
        {'part': 'leftHip', 'position': {'x': 115, 'y': 130}, 'score': 0.89},
        {'part': 'rightKnee', 'position': {'x': 80, 'y': 180}, 'score': 0.85},
        {'part': 'leftKnee', 'position': {'x': 120, 'y': 180}, 'score': 0.86},
        {'part': 'rightAnkle', 'position': {'x': 80, 'y': 220}, 'score': 0.82},
        {'part': 'leftAnkle', 'position': {'x': 120, 'y': 220}, 'score': 0.83},
    ]

    classifier = ActivityClassifier(example_pose)
    activity, confidence = classifier.classify()
    details = classifier.get_activity_details()
    
    print(f"Activity: {activity}")
    print(f"Confidence: {confidence}%")
    print(f"Details: {json.dumps(details, indent=2)}")
