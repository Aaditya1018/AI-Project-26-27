"""
SafeStack AI - Multi-Frame Object Tracker (DeepSORT / ByteTrack Logic)
Maintains tracking IDs, trajectory histories, velocities, and accelerations across frames.
"""

from typing import List, Dict, Any, Tuple
import math
from collections import deque
from backend.cv_pipeline.detector import Detection

class Track:
    def __init__(self, track_id: int, class_name: str, bbox: List[float], max_history: int = 60):
        self.track_id = track_id
        self.class_name = class_name
        self.bbox = bbox  # [x, y, w, h] (center_x, center_y, width, height)
        self.history = deque(maxlen=max_history)  # [(x, y, w, h, timestamp)]
        self.velocities = deque(maxlen=max_history) # [(vx, vy)]
        self.accelerations = deque(maxlen=max_history) # [(ax, ay)]
        self.age = 0
        self.hits = 1
        self.time_since_update = 0

    def update(self, bbox: List[float], dt: float = 1.0 / 30.0):
        # Calculate instantaneous velocity (px/s or normalized/s)
        prev_x, prev_y = self.bbox[0], self.bbox[1]
        new_x, new_y = bbox[0], bbox[1]
        
        vx = (new_x - prev_x) / dt
        vy = (new_y - prev_y) / dt
        
        if len(self.velocities) > 0:
            prev_vx, prev_vy = self.velocities[-1]
            ax = (vx - prev_vx) / dt
            ay = (vy - prev_vy) / dt
            self.accelerations.append((ax, ay))
        else:
            self.accelerations.append((0.0, 0.0))

        self.velocities.append((vx, vy))
        self.history.append((new_x, new_y, bbox[2], bbox[3]))
        self.bbox = bbox
        self.hits += 1
        self.time_since_update = 0

    def get_last_velocity(self) -> Tuple[float, float]:
        if self.velocities:
            return self.velocities[-1]
        return (0.0, 0.0)

    def get_last_acceleration(self) -> Tuple[float, float]:
        if self.accelerations:
            return self.accelerations[-1]
        return (0.0, 0.0)

class MultiFrameTracker:
    def __init__(self, iou_threshold: float = 0.3, max_lost_frames: int = 15):
        self.iou_threshold = iou_threshold
        self.max_lost_frames = max_lost_frames
        self.tracks: Dict[int, Track] = {}
        self.next_track_id = 1

    @staticmethod
    def compute_iou(boxA: List[float], boxB: List[float]) -> float:
        # box: [center_x, center_y, w, h]
        xA1, yA1 = boxA[0] - boxA[2] / 2, boxA[1] - boxA[3] / 2
        xA2, yA2 = boxA[0] + boxA[2] / 2, boxA[1] + boxA[3] / 2

        xB1, yB1 = boxB[0] - boxB[2] / 2, boxB[1] - boxB[3] / 2
        xB2, yB2 = boxB[0] + boxB[2] / 2, boxB[1] + boxB[3] / 2

        inter_x1 = max(xA1, xB1)
        inter_y1 = max(yA1, yB1)
        inter_x2 = min(xA2, xB2)
        inter_y2 = min(yA2, yB2)

        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
        areaA = boxA[2] * boxA[3]
        areaB = boxB[2] * boxB[3]

        union_area = areaA + areaB - inter_area
        if union_area <= 0:
            return 0.0
        return inter_area / union_area

    def update(self, detections: List[Detection], dt: float = 1.0 / 30.0) -> List[Track]:
        # Increment time_since_update for all active tracks
        for track in self.tracks.values():
            track.time_since_update += 1
            track.age += 1

        matched_tracks = set()
        matched_detections = set()

        # If detections already have track_id assigned (from simulator)
        for i, det in enumerate(detections):
            if det.track_id > 0 and det.track_id in self.tracks:
                self.tracks[det.track_id].update(det.bbox, dt)
                matched_tracks.add(det.track_id)
                matched_detections.add(i)

        # Match remaining detections using IoU
        remaining_dets = [i for i in range(len(detections)) if i not in matched_detections]
        unmatched_tracks = [t_id for t_id in self.tracks.keys() if t_id not in matched_tracks]

        for det_idx in remaining_dets:
            det = detections[det_idx]
            best_iou = self.iou_threshold
            best_track_id = None

            for t_id in unmatched_tracks:
                if self.tracks[t_id].class_name == det.class_name:
                    iou = self.compute_iou(self.tracks[t_id].bbox, det.bbox)
                    if iou > best_iou:
                        best_iou = iou
                        best_track_id = t_id

            if best_track_id is not None:
                self.tracks[best_track_id].update(det.bbox, dt)
                matched_tracks.add(best_track_id)
                unmatched_tracks.remove(best_track_id)
                det.track_id = best_track_id
            else:
                # Create new track
                new_id = det.track_id if det.track_id > 0 else self.next_track_id
                self.next_track_id = max(self.next_track_id + 1, new_id + 1)
                new_track = Track(new_id, det.class_name, det.bbox)
                self.tracks[new_id] = new_track
                det.track_id = new_id

        # Clean up stale tracks
        expired = [t_id for t_id, track in self.tracks.items() if track.time_since_update > self.max_lost_frames]
        for t_id in expired:
            del self.tracks[t_id]

        return list(self.tracks.values())
