"""
SafeStack AI - Scenario Runner & Live Feed Controller
Coordinates live loading bay feeds, CV tracking, real-time behavior injection,
and instant risk scoring broadcasts.
"""

import time
import json
import uuid
from threading import Lock
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np

from backend.simulation.video_synthesizer import WarehouseSceneSynthesizer
from backend.cv_pipeline.detector import SafeStackDetector
from backend.cv_pipeline.tracker import MultiFrameTracker
from backend.cv_pipeline.action_recognizer import SequenceActionRecognizer
from backend.cv_pipeline.privacy_shield import PrivacyShield
from backend.risk_engine.scorer import GradedRiskScorer
from backend.risk_engine.explainability import ExplainabilityEngine
from backend.models.schemas import BehaviorType, ProductCategory, EventResponse, ReviewStatus
from backend.models.database import EventDBManager
from backend.config import settings

class LiveBayStream:
    def __init__(self, bay_id: str, bay_name: str):
        self.bay_id = bay_id
        self.bay_name = bay_name
        self.synthesizer = WarehouseSceneSynthesizer(640, 480)
        self.detector = SafeStackDetector()
        self.tracker = MultiFrameTracker()
        self.action_recognizer = SequenceActionRecognizer()
        self.privacy_shield = PrivacyShield()
        self.scorer = GradedRiskScorer()
        self.explainability_engine = ExplainabilityEngine()
        
        self.current_scenario: Optional[str] = None
        self.scenario_frame_idx: int = 0
        self.scenario_frames: List[np.ndarray] = []
        self.custom_video_path: Optional[str] = None
        self.custom_cap = None
        self.custom_video_lock = Lock()

    def set_custom_video(self, video_path: str):
        try:
            import cv2
        except ModuleNotFoundError:
            self.custom_video_path = None
            self.custom_cap = None
            return

        with self.custom_video_lock:
            try:
                if self.custom_cap:
                    self.custom_cap.release()
                self.custom_video_path = video_path
                self.custom_cap = cv2.VideoCapture(video_path)
                if not self.custom_cap.isOpened():
                    self.custom_cap.release()
                    self.custom_cap = None
                    self.custom_video_path = video_path
                self.current_scenario = None
                self.scenario_frames = []
            except Exception:
                self.custom_video_path = video_path
                if self.custom_cap:
                    try:
                        self.custom_cap.release()
                    except Exception:
                        pass
                    self.custom_cap = None

    def clear_custom_video(self):
        with self.custom_video_lock:
            self.custom_video_path = None
            if self.custom_cap:
                try:
                    self.custom_cap.release()
                except Exception:
                    pass
            self.custom_cap = None

    def get_current_frame(self, enable_privacy: bool = True, render_silhouettes: bool = False) -> np.ndarray:
        raw_frame = None
        with self.custom_video_lock:
            if self.custom_cap and self.custom_cap.isOpened():
                ret, frame = self.custom_cap.read()
                if not ret:
                    # Rewind and loop video
                    self.custom_cap.set(1, 0)
                    ret, frame = self.custom_cap.read()
                if ret and frame is not None:
                    raw_frame = frame.copy()

        if raw_frame is None:
            if self.current_scenario and self.scenario_frames:
                raw_frame = self.scenario_frames[self.scenario_frame_idx % len(self.scenario_frames)].copy()
                self.scenario_frame_idx += 1
                if self.scenario_frame_idx >= len(self.scenario_frames):
                    self.current_scenario = None
                    self.scenario_frames = []
            else:
                fallback_frames = self.synthesizer.generate_scenario_frames("NORMAL", total_frames=12)
                raw_frame = fallback_frames[0].copy()

        is_custom_video = self.custom_video_path is not None
        try:
            detections = self.detector.detect_frame(
                raw_frame,
                allow_demo_detections=not is_custom_video
            )
            self.tracker.update(detections)
        except Exception:
            detections = []

        try:
            if enable_privacy:
                frame_with_privacy = self.privacy_shield.process_frame(
                    raw_frame,
                    detections,
                    anonymize_faces=True,
                    render_silhouettes=render_silhouettes
                )
            else:
                frame_with_privacy = raw_frame
        except Exception:
            frame_with_privacy = raw_frame.copy() if raw_frame is not None else self.synthesizer.render_base_warehouse()

        self._render_hud_overlay(frame_with_privacy, detections)
        return frame_with_privacy

    def _render_hud_overlay(self, frame: np.ndarray, detections: List[Any]):
        try:
            import cv2
            h, w = frame.shape[:2]
            cv2.putText(frame, f"LIVE: {self.bay_name}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 200), 2, cv2.LINE_AA)
            cv2.putText(frame, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), (w - 220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

            for det in detections:
                cx, cy = det.bbox[0], det.bbox[1]
                bw, bh = det.bbox[2], det.bbox[3]
                x1, y1 = int(cx - bw / 2), int(cy - bh / 2)
                x2, y2 = int(cx + bw / 2), int(cy + bh / 2)

                color = (0, 255, 120) if det.class_name == "person" else ((50, 160, 240) if det.class_name == "carton" else (220, 180, 40))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                tag = f"#{det.track_id} {det.class_name.upper()} {int(det.confidence * 100)}%"
                cv2.putText(frame, tag, (x1, max(15, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)
        except Exception:
            pass

class SafeStackSimulator:
    def __init__(self):
        self.bays: Dict[str, LiveBayStream] = {
            "BAY-01": LiveBayStream("BAY-01", "Bay-01 (Inbound Cargo)"),
            "BAY-02": LiveBayStream("BAY-02", "Bay-02 (Heavy Industrial)"),
            "BAY-03": LiveBayStream("BAY-03", "Bay-03 (Express Parcels)"),
            "BAY-04": LiveBayStream("BAY-04", "Bay-04 (Cold Chain FMCG)"),
        }
        self.synthesizer = WarehouseSceneSynthesizer()
        self.scorer = GradedRiskScorer()
        self.explainability_engine = ExplainabilityEngine()
        self.synthesizer.save_sample_evidence_files()

    def get_bay_stream(self, bay_id: str) -> Optional[LiveBayStream]:
        return self.bays.get(bay_id)

    def set_bay_video(self, bay_id: str, video_path: str) -> bool:
        bay = self.bays.get(bay_id)
        if not bay:
            return False
        bay.set_custom_video(video_path)
        return True

    def clear_bay_video(self, bay_id: str) -> bool:
        bay = self.bays.get(bay_id)
        if bay:
            bay.clear_custom_video()
            return True
        return False

    def trigger_behavior_scenario(
        self,
        bay_id: str,
        behavior_code: str,
        category: ProductCategory = ProductCategory.ELECTRONICS_FRAGILE
    ) -> EventResponse:
        bay = self.bays.get(bay_id) or self.bays["BAY-01"]
        
        bay.current_scenario = behavior_code
        bay.scenario_frame_idx = 0
        bay.scenario_frames = self.synthesizer.generate_scenario_frames(behavior_code, total_frames=45)

        try:
            beh_type = BehaviorType(behavior_code)
        except Exception:
            beh_type = BehaviorType.BEH_DROP

        behavior_display_name = {
            BehaviorType.BEH_DROP: "Product Dropped from Height",
            BehaviorType.BEH_DRAG: "Floor Dragging Cartons",
            BehaviorType.BEH_IMPROPER_STACK: "Inverted Pyramid Stacking",
            BehaviorType.BEH_PALLET_OVERHANG: "Unsafe Pallet Overhang & Tilt",
            BehaviorType.BEH_ROUGH_HANDLING: "Rough Handling / Slamming",
            BehaviorType.BEH_TOSS_THROW: "Carton Tossing / Throwing",
            BehaviorType.BEH_STEP_ON_CARGO: "Stepping or Sitting on Cartons",
            BehaviorType.BEH_OVERSTACK: "Over-Stacking Height Limit",
            BehaviorType.BEH_ROLLING_TUMBLE: "Rolling / Tumbling Cartons",
            BehaviorType.BEH_FORKLIFT_PINCH: "Forklift / Pedestrian Hazard",
        }.get(beh_type, "Unsafe Material Handling")

        from backend.models.schemas import KinematicMetrics
        if beh_type == BehaviorType.BEH_DROP:
            metrics = KinematicMetrics(vertical_accel_mps2=9.78, drop_velocity_mps=4.2, drop_height_m=1.35, kinetic_impact_energy_j=88.2, rough_impact_decel_mps2=21.0)
        elif beh_type == BehaviorType.BEH_DRAG:
            metrics = KinematicMetrics(drag_distance_m=4.2, tilt_angle_deg=8.0)
        elif beh_type == BehaviorType.BEH_IMPROPER_STACK:
            metrics = KinematicMetrics(tilt_angle_deg=18.5, stack_height_m=1.92, pallet_overhang_pct=26.0)
        elif beh_type == BehaviorType.BEH_PALLET_OVERHANG:
            metrics = KinematicMetrics(pallet_overhang_pct=34.0, tilt_angle_deg=14.0)
        elif beh_type == BehaviorType.BEH_TOSS_THROW:
            metrics = KinematicMetrics(drop_velocity_mps=3.9, drop_height_m=0.95, kinetic_impact_energy_j=58.0, rough_impact_decel_mps2=16.0)
        elif beh_type == BehaviorType.BEH_FORKLIFT_PINCH:
            metrics = KinematicMetrics(pedestrian_distance_m=0.85, kinetic_impact_energy_j=120.0)
        else:
            metrics = KinematicMetrics(vertical_accel_mps2=4.0, drop_height_m=0.6, rough_impact_decel_mps2=15.0)

        prior_count = len(EventDBManager.get_events(bay_id=bay.bay_id)) + 1
        risk_score, risk_tier = self.scorer.calculate_score(beh_type, category, metrics, bay_recent_frequency=prior_count)
        
        explain_report = self.explainability_engine.generate_report(
            beh_type,
            behavior_display_name,
            category,
            metrics,
            risk_score,
            bay_frequency=prior_count
        )

        event_id = f"EVT-{str(uuid.uuid4())[:8].upper()}"
        now = datetime.utcnow()

        clip_slug = "sample_drop" if beh_type == BehaviorType.BEH_DROP else ("sample_stack" if beh_type == BehaviorType.BEH_IMPROPER_STACK else ("sample_throw" if beh_type == BehaviorType.BEH_TOSS_THROW else ("sample_drag" if beh_type == BehaviorType.BEH_DRAG else "sample_forklift")))
        clip_url = f"/api/media/clips/{clip_slug}.mp4"
        snapshot_url = f"/api/media/snapshots/{clip_slug}.jpg"

        event_response = EventResponse(
            id=event_id,
            timestamp=now,
            bay_id=bay.bay_id,
            bay_name=bay.bay_name,
            behavior_type=beh_type,
            behavior_name=behavior_display_name,
            product_category=category,
            risk_score=risk_score,
            risk_tier=risk_tier,
            kinematic_telemetry=metrics,
            explainability=explain_report,
            clip_url=clip_url,
            snapshot_url=snapshot_url,
            status=ReviewStatus.PENDING_REVIEW,
            supervisor_notes=""
        )

        event_dict = {
            "id": event_id,
            "timestamp": now.isoformat(),
            "bay_id": bay.bay_id,
            "bay_name": bay.bay_name,
            "behavior_type": beh_type.value,
            "behavior_name": behavior_display_name,
            "product_category": category.value,
            "risk_score": risk_score,
            "risk_tier": risk_tier.value,
            "kinematic_telemetry": metrics.model_dump(),
            "explainability": explain_report.model_dump(),
            "clip_url": clip_url,
            "snapshot_url": snapshot_url,
            "status": ReviewStatus.PENDING_REVIEW.value,
            "supervisor_notes": "",
            "reviewed_by": None,
            "reviewed_at": None
        }
        EventDBManager.insert_event(event_dict)
        return event_response

simulator = SafeStackSimulator()
