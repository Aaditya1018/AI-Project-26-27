"""
SafeStack AI - Video File Injection & Processing Pipeline
Processes real or recorded warehouse video footage (.mp4, .avi, .mov)
Runs object detection, tracking, sequence action classification, risk scoring,
and edge privacy shielding on arbitrary injected video files.
"""

import time
import uuid
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Generator
import numpy as np

from backend.cv_pipeline.detector import SafeStackDetector
from backend.cv_pipeline.tracker import MultiFrameTracker
from backend.cv_pipeline.action_recognizer import SequenceActionRecognizer
from backend.cv_pipeline.privacy_shield import PrivacyShield
from backend.cv_pipeline.kinematics import KinematicsEngine
from backend.risk_engine.scorer import GradedRiskScorer
from backend.risk_engine.explainability import ExplainabilityEngine
from backend.models.schemas import BehaviorType, ProductCategory, EventResponse, ReviewStatus
from backend.models.database import EventDBManager
from backend.config import settings

class InjectedVideoProcessor:
    def __init__(self, video_path: str):
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found at {video_path}")

        self.detector = SafeStackDetector()
        self.tracker = MultiFrameTracker()
        self.action_recognizer = SequenceActionRecognizer()
        self.privacy_shield = PrivacyShield()
        self.scorer = GradedRiskScorer()
        self.explainability_engine = ExplainabilityEngine()
        self.kinematics = KinematicsEngine()
        self.last_scan_summary: Dict[str, Any] = {}

    def process_and_detect_events(
        self,
        bay_id: str = "BAY-01",
        bay_name: str = "Bay-01 (Inbound Cargo)",
        category: ProductCategory = ProductCategory.GENERAL_CARGO,
        sample_stride: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Processes the entire uploaded video file, detects damage-risk behaviors,
        commits all detected events to the database, and returns the incident timeline.
        """
        if sample_stride < 1:
            raise ValueError("sample_stride must be at least 1")
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError("OpenCV is required to scan uploaded videos.") from exc

        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            cap.release()
            raise ValueError(f"Could not decode uploaded video: {self.video_path.name}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        dt = sample_stride / fps

        frame_idx = 0
        analyzed_frames = 0
        detection_counts: Dict[str, int] = {}
        detected_incidents: List[Dict[str, Any]] = []
        last_event_time = 0.0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % sample_stride == 0:
                    analyzed_frames += 1
                    current_timestamp_sec = frame_idx / fps
                    detections = self.detector.detect_frame(frame, allow_demo_detections=False)
                    for detection in detections:
                        detection_counts[detection.class_name] = detection_counts.get(detection.class_name, 0) + 1

                    tracks = self.tracker.update(detections, dt=dt)
                    action_results = self.action_recognizer.analyze_temporal_window(tracks)

                    for act in action_results:
                        if (current_timestamp_sec - last_event_time) > 3.0:
                            event_id = f"EVT-INJ-{str(uuid.uuid4())[:6].upper()}"
                            score, tier = self.scorer.calculate_score(act.behavior_type, category, act.metrics)
                            explain_report = self.explainability_engine.generate_report(
                                act.behavior_type,
                                act.behavior_name,
                                category,
                                act.metrics,
                                score
                            )
                            snap_name = f"{event_id}.jpg"
                            snap_path = settings.SNAPSHOTS_DIR / snap_name
                            if not cv2.imwrite(str(snap_path), frame):
                                raise RuntimeError(f"Could not save analysis snapshot: {snap_name}")

                            event_data = {
                                "id": event_id,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "bay_id": bay_id,
                                "bay_name": bay_name,
                                "behavior_type": act.behavior_type.value,
                                "behavior_name": act.behavior_name,
                                "product_category": category.value,
                                "risk_score": score,
                                "risk_tier": tier.value,
                                "kinematic_telemetry": act.metrics.model_dump(),
                                "explainability": explain_report.model_dump(),
                                "clip_url": f"/api/video/file/{self.video_path.name}",
                                "snapshot_url": f"/api/media/snapshots/{snap_name}",
                                "status": "Pending Review",
                                "supervisor_notes": f"Detected in custom injected video at {round(current_timestamp_sec, 2)}s.",
                                "reviewed_by": None,
                                "reviewed_at": None
                            }
                            EventDBManager.insert_event(event_data)
                            detected_incidents.append(event_data)
                            last_event_time = current_timestamp_sec

                frame_idx += 1
        finally:
            cap.release()

        warehouse_classes = self.detector.supported_warehouse_classes()
        self.last_scan_summary = {
            "detector_status": "ready" if self.detector.has_yolo else "unavailable",
            "detector_model": self.detector.model_name,
            "detector_error": self.detector.model_error,
            "warehouse_classes_supported": warehouse_classes,
            "frames_read": frame_idx,
            "frames_analyzed": analyzed_frames,
            "detection_counts": detection_counts,
            "incident_count": len(detected_incidents),
            "interpretation": (
                "Counts are real model outputs. Behavior rules require the model to detect the relevant warehouse objects; no incidents is not proof the loading is safe."
                if self.detector.has_yolo
                else "No detector model is available. Zero detections or incidents do not mean the footage is safe."
            )
        }
        return detected_incidents

    def get_frame_generator(
        self,
        bay_name: str = "Injected Custom Video Feed",
        enable_privacy: bool = True,
        render_silhouettes: bool = False,
        loop: bool = True
    ) -> Generator[bytes, None, None]:
        """
        Streams frames from the injected video file in real time with overlays and privacy shield.
        """
        import cv2

        while True:
            cap = cv2.VideoCapture(str(self.video_path))
            if not cap.isOpened():
                return

            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            frame_delay = 1.0 / max(10.0, min(fps, 30.0))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Run CV detector and tracker
                detections = self.detector.detect_frame(frame)
                self.tracker.update(detections)

                # Privacy Shield
                if enable_privacy:
                    frame = self.privacy_shield.process_frame(
                        frame,
                        detections,
                        anonymize_faces=True,
                        render_silhouettes=render_silhouettes
                    )

                # Draw HUD and Bounding Boxes
                self._draw_overlay(frame, detections, bay_name)

                # Encode to JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

                time.sleep(frame_delay)

            cap.release()
            if not loop:
                break

    def _draw_overlay(self, frame: np.ndarray, detections: List[Any], bay_name: str):
        import cv2
        h, w = frame.shape[:2]
        # Top banner
        cv2.putText(frame, f"INJECTED FEED: {bay_name}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 200), 2, cv2.LINE_AA)
        cv2.putText(frame, self.video_path.name, (w - 240, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)

        # Draw detection bounding boxes
        for det in detections:
            cx, cy = det.bbox[0], det.bbox[1]
            bw, bh = det.bbox[2], det.bbox[3]
            x1, y1 = int(cx - bw / 2), int(cy - bh / 2)
            x2, y2 = int(cx + bw / 2), int(cy + bh / 2)

            color = (0, 255, 120) if det.class_name == "person" else ((50, 160, 240) if det.class_name == "carton" else (220, 180, 40))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            tag = f"#{det.track_id} {det.class_name.upper()} {int(det.confidence * 100)}%"
            cv2.putText(frame, tag, (x1, max(15, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)
