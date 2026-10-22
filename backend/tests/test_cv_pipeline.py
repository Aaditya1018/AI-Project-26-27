"""
SafeStack AI - CV Pipeline & Kinematics Unit Tests
"""

import pytest
from backend.cv_pipeline.kinematics import KinematicsEngine
from backend.cv_pipeline.tracker import Track, MultiFrameTracker
from backend.cv_pipeline.action_recognizer import SequenceActionRecognizer
from backend.cv_pipeline.detector import Detection
from backend.models.schemas import BehaviorType

def test_kinematics_freefall():
    ke = KinematicsEngine(pixels_per_meter=100.0, default_package_mass_kg=12.0)
    # 5 m/s drop velocity -> kinetic energy = 0.5 * 12 * 25 = 150 J
    ke_energy = ke.calculate_kinetic_impact_energy(5.0)
    assert ke_energy == 150.0

    # Deceleration with 0.05s impact duration
    decel = ke.calculate_landing_deceleration(5.0, 0.05)
    assert decel == 100.0

def test_pallet_overhang_calculation():
    ke = KinematicsEngine(pixels_per_meter=100.0)
    # Box [x, y, w, h] = [150, 200, 100, 80], Pallet = [100, 250, 100, 30]
    # Box left: 100, right: 200. Pallet left: 50, right: 150.
    # Overhang on right side = 200 - 150 = 50px (50% of 100px box width)
    overhang = ke.calculate_pallet_overhang([150, 200, 100, 80], [100, 250, 100, 30])
    assert overhang == 50.0

def test_tilt_angle_calculation():
    ke = KinematicsEngine()
    # 45 degree tilt: dx == dy
    angle = ke.calculate_tilt_angle((100, 100), (50, 150))
    assert pytest.approx(angle, 0.1) == 45.0

def test_multi_frame_tracker_iou():
    tracker = MultiFrameTracker()
    boxA = [100, 100, 50, 50]
    boxB = [100, 100, 50, 50]
    iou_exact = tracker.compute_iou(boxA, boxB)
    assert iou_exact == 1.0

    boxC = [200, 200, 50, 50]
    iou_disjoint = tracker.compute_iou(boxA, boxC)
    assert iou_disjoint == 0.0

def test_sequence_action_recognizer_drop():
    recognizer = SequenceActionRecognizer()
    track = Track(track_id=1, class_name="carton", bbox=[200, 300, 50, 50])
    
    # Simulate downward acceleration over sequential frames
    for i in range(15):
        y = 100 + (i * 20)  # dropping downwards
        track.update([200, y, 50, 50], dt=1.0/30.0)

    results = recognizer.analyze_temporal_window([track])
    # Expect drop detection
    drop_results = [r for r in results if r.behavior_type == BehaviorType.BEH_DROP]
    assert len(drop_results) >= 1
    assert drop_results[0].metrics.drop_height_m > 0
