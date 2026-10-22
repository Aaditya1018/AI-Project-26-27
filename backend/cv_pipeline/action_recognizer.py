"""
SafeStack AI - Sequence-Level Action Recognizer
Identifies 10 Predefined Damage-Risk Behaviors across multi-frame temporal windows:
1.  BEH_DROP: Product Dropped from Height
2.  BEH_DRAG: Floor Dragging Cartons
3.  BEH_IMPROPER_STACK: Inverted Pyramid Stacking
4.  BEH_PALLET_OVERHANG: Unsafe Pallet Overhang & Tilt
5.  BEH_ROUGH_HANDLING: Rough Handling / Slamming
6.  BEH_TOSS_THROW: Carton Tossing / Throwing
7.  BEH_STEP_ON_CARGO: Stepping or Sitting on Cartons
8.  BEH_OVERSTACK: Over-Stacking Height Limit
9.  BEH_ROLLING_TUMBLE: Rolling / Tumbling Cartons
10. BEH_FORKLIFT_PINCH: Forklift / Pedestrian Pinch Hazard
"""

from typing import List, Dict, Any, Optional
from collections import deque
from backend.cv_pipeline.tracker import Track
from backend.cv_pipeline.kinematics import KinematicsEngine
from backend.models.schemas import BehaviorType, KinematicMetrics

class ActionRecognitionResult:
    def __init__(self, behavior_type: BehaviorType, behavior_name: str, confidence: float, metrics: KinematicMetrics, track_ids: List[int]):
        self.behavior_type = behavior_type
        self.behavior_name = behavior_name
        self.confidence = confidence
        self.metrics = metrics
        self.track_ids = track_ids

class SequenceActionRecognizer:
    def __init__(self, window_size: int = 45):
        self.window_size = window_size
        self.kinematics = KinematicsEngine()
        self.BEHAVIOR_NAMES = {
            BehaviorType.BEH_DROP: "Product Dropped from Height",
            BehaviorType.BEH_DRAG: "Floor Dragging Cartons",
            BehaviorType.BEH_IMPROPER_STACK: "Inverted Pyramid Stacking",
            BehaviorType.BEH_PALLET_OVERHANG: "Unsafe Pallet Overhang & Tilt",
            BehaviorType.BEH_ROUGH_HANDLING: "Rough Handling / Slamming",
            BehaviorType.BEH_TOSS_THROW: "Carton Tossing / Throwing",
            BehaviorType.BEH_STEP_ON_CARGO: "Stepping or Sitting on Cartons",
            BehaviorType.BEH_OVERSTACK: "Over-Stacking Height Limit",
            BehaviorType.BEH_ROLLING_TUMBLE: "Rolling / Tumbling Cartons",
            BehaviorType.BEH_FORKLIFT_PINCH: "Forklift / Pedestrian Hazard"
        }

    def analyze_temporal_window(self, tracks: List[Track]) -> List[ActionRecognitionResult]:
        """
        Analyzes the multi-frame history of all active tracks to detect any of the 10 damage behaviors.
        """
        results: List[ActionRecognitionResult] = []

        carton_tracks = [t for t in tracks if t.class_name in ("carton", "box", "package")]
        person_tracks = [t for t in tracks if t.class_name == "person"]
        pallet_tracks = [t for t in tracks if t.class_name == "pallet"]
        forklift_tracks = [t for t in tracks if t.class_name in ("forklift", "pallet_jack", "vehicle")]

        # 1. BEH_DROP: Product Dropped from Height
        for c in carton_tracks:
            if len(c.history) >= 10:
                accel_y = self.kinematics.calculate_vertical_acceleration(c.accelerations)
                v_drop = self.kinematics.calculate_drop_velocity(c.velocities)
                h_drop = self.kinematics.px_to_meters(max(0, c.history[-1][1] - c.history[0][1]))
                energy = self.kinematics.calculate_kinetic_impact_energy(v_drop)
                decel = self.kinematics.calculate_landing_deceleration(v_drop)

                if (accel_y >= 8.0 or v_drop >= 3.2) and h_drop >= 0.5:
                    metrics = KinematicMetrics(
                        vertical_accel_mps2=round(accel_y, 2),
                        drop_velocity_mps=round(v_drop, 2),
                        drop_height_m=round(h_drop, 2),
                        kinetic_impact_energy_j=energy,
                        rough_impact_decel_mps2=decel
                    )
                    results.append(ActionRecognitionResult(
                        BehaviorType.BEH_DROP,
                        self.BEHAVIOR_NAMES[BehaviorType.BEH_DROP],
                        0.94,
                        metrics,
                        [c.track_id]
                    ))

        # 2. BEH_DRAG: Floor Dragging Cartons
        for c in carton_tracks:
            if len(c.history) >= 20:
                dx_total = abs(c.history[-1][0] - c.history[0][0])
                dy_total = abs(c.history[-1][1] - c.history[0][1])
                dist_m = self.kinematics.px_to_meters(dx_total)
                # Check if movement is mostly horizontal near floor level
                if dist_m >= 1.2 and dy_total < 40:
                    metrics = KinematicMetrics(drag_distance_m=round(dist_m, 2))
                    results.append(ActionRecognitionResult(
                        BehaviorType.BEH_DRAG,
                        self.BEHAVIOR_NAMES[BehaviorType.BEH_DRAG],
                        0.88,
                        metrics,
                        [c.track_id]
                    ))

        # 3. BEH_IMPROPER_STACK & 4. BEH_PALLET_OVERHANG
        for c in carton_tracks:
            # Overhang check against pallets
            for p in pallet_tracks:
                overhang_pct = self.kinematics.calculate_pallet_overhang(c.bbox, p.bbox)
                if overhang_pct >= 25.0:
                    metrics = KinematicMetrics(
                        pallet_overhang_pct=overhang_pct,
                        tilt_angle_deg=14.5
                    )
                    results.append(ActionRecognitionResult(
                        BehaviorType.BEH_PALLET_OVERHANG,
                        self.BEHAVIOR_NAMES[BehaviorType.BEH_PALLET_OVERHANG],
                        0.91,
                        metrics,
                        [c.track_id, p.track_id]
                    ))

            # Improper stack (inverted pyramid: larger box stacked on smaller box)
            for other_c in carton_tracks:
                if c.track_id != other_c.track_id:
                    # If c is above other_c
                    if c.bbox[1] < other_c.bbox[1]:
                        c_area = c.bbox[2] * c.bbox[3]
                        base_area = other_c.bbox[2] * other_c.bbox[3]
                        if c_area > base_area * 1.4:
                            metrics = KinematicMetrics(tilt_angle_deg=16.2, stack_height_m=1.85)
                            results.append(ActionRecognitionResult(
                                BehaviorType.BEH_IMPROPER_STACK,
                                self.BEHAVIOR_NAMES[BehaviorType.BEH_IMPROPER_STACK],
                                0.89,
                                metrics,
                                [c.track_id, other_c.track_id]
                            ))

        # 5. BEH_ROUGH_HANDLING: High landing deceleration
        for c in carton_tracks:
            if len(c.accelerations) >= 5:
                recent_decels = [abs(a[1]) for a in list(c.accelerations)[-5:]]
                max_decel_m = self.kinematics.px_to_meters(max(recent_decels, default=0.0))
                if max_decel_m >= 14.0:
                    metrics = KinematicMetrics(rough_impact_decel_mps2=round(max_decel_m, 2))
                    results.append(ActionRecognitionResult(
                        BehaviorType.BEH_ROUGH_HANDLING,
                        self.BEHAVIOR_NAMES[BehaviorType.BEH_ROUGH_HANDLING],
                        0.87,
                        metrics,
                        [c.track_id]
                    ))

        # 6. BEH_TOSS_THROW: Airborne parabolic trajectory
        for c in carton_tracks:
            if len(c.history) >= 15:
                # Check if carton had upward arc then downward arc
                y_positions = [h[1] for h in list(c.history)[-15:]]
                x_positions = [h[0] for h in list(c.history)[-15:]]
                horizontal_vel = abs(x_positions[-1] - x_positions[0])
                if min(y_positions) < y_positions[0] and min(y_positions) < y_positions[-1] and horizontal_vel > 60:
                    v_mps = self.kinematics.px_to_meters(horizontal_vel)
                    metrics = KinematicMetrics(drop_velocity_mps=round(v_mps, 2), drop_height_m=0.85)
                    results.append(ActionRecognitionResult(
                        BehaviorType.BEH_TOSS_THROW,
                        self.BEHAVIOR_NAMES[BehaviorType.BEH_TOSS_THROW],
                        0.93,
                        metrics,
                        [c.track_id]
                    ))

        # 7. BEH_STEP_ON_CARGO: Worker bounding box overlapping carton top
        for p in person_tracks:
            for c in carton_tracks:
                # Person bottom is near or above carton center/top
                p_bottom = p.bbox[1] + p.bbox[3] / 2
                c_top = c.bbox[1] - c.bbox[3] / 2
                overlap_x = abs(p.bbox[0] - c.bbox[0]) < (p.bbox[2] + c.bbox[2]) / 2
                if overlap_x and abs(p_bottom - c_top) < 25:
                    metrics = KinematicMetrics(tilt_angle_deg=22.0)
                    results.append(ActionRecognitionResult(
                        BehaviorType.BEH_STEP_ON_CARGO,
                        self.BEHAVIOR_NAMES[BehaviorType.BEH_STEP_ON_CARGO],
                        0.95,
                        metrics,
                        [p.track_id, c.track_id]
                    ))

        # 8. BEH_OVERSTACK: Stack height exceeds safe envelope
        for c in carton_tracks:
            stack_h = self.kinematics.px_to_meters(c.bbox[3])
            if stack_h >= 2.15:
                metrics = KinematicMetrics(stack_height_m=round(stack_h, 2))
                results.append(ActionRecognitionResult(
                    BehaviorType.BEH_OVERSTACK,
                    self.BEHAVIOR_NAMES[BehaviorType.BEH_OVERSTACK],
                    0.86,
                    metrics,
                    [c.track_id]
                ))

        # 9. BEH_ROLLING_TUMBLE: Tumbling carton
        for c in carton_tracks:
            if len(c.history) >= 12:
                w_changes = [abs(h[2] - h[3]) for h in list(c.history)[-10:]]
                if max(w_changes, default=0) > 30:
                    metrics = KinematicMetrics(tilt_angle_deg=45.0)
                    results.append(ActionRecognitionResult(
                        BehaviorType.BEH_ROLLING_TUMBLE,
                        self.BEHAVIOR_NAMES[BehaviorType.BEH_ROLLING_TUMBLE],
                        0.84,
                        metrics,
                        [c.track_id]
                    ))

        # 10. BEH_FORKLIFT_PINCH: Moving forklift within 1.5m of worker
        for f in forklift_tracks:
            for p in person_tracks:
                dist = self.kinematics.calculate_distance(f.bbox, p.bbox)
                if dist < 1.5:
                    metrics = KinematicMetrics(pedestrian_distance_m=dist)
                    results.append(ActionRecognitionResult(
                        BehaviorType.BEH_FORKLIFT_PINCH,
                        self.BEHAVIOR_NAMES[BehaviorType.BEH_FORKLIFT_PINCH],
                        0.96,
                        metrics,
                        [f.track_id, p.track_id]
                    ))

        return results
