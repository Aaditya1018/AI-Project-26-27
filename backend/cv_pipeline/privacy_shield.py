"""
SafeStack AI - Responsible AI Privacy Shield
Performs data minimisation, real-time face blurring, and anonymous silhouette rendering at the edge.
Ensures zero indiscriminate employee surveillance while retaining posture kinematics.
"""

from typing import List, Dict, Any, Tuple
import numpy as np

class PrivacyShield:
    def __init__(self, blur_kernel_size: int = 31, silhouette_color: Tuple[int, int, int] = (16, 185, 129)):
        self.blur_ksize = blur_kernel_size
        self.silhouette_color = silhouette_color  # Emerald green ergonomic avatar

    def apply_face_blur(self, frame: np.ndarray, person_bbox: List[float]) -> np.ndarray:
        """
        Applies privacy-preserving Gaussian blur over the head/face region of a worker.
        person_bbox: [center_x, center_y, width, height]
        """
        if frame is None or len(person_bbox) < 4:
            return frame

        h_img, w_img = frame.shape[:2]
        cx, cy, bw, bh = person_bbox
        
        # Upper 28% of person bounding box corresponds to head/face
        x1 = max(0, int(cx - bw / 2))
        x2 = min(w_img, int(cx + bw / 2))
        y1 = max(0, int(cy - bh / 2))
        y2 = min(h_img, int(cy - bh / 2 + bh * 0.28))

        if x2 > x1 and y2 > y1:
            try:
                import cv2
                face_roi = frame[y1:y2, x1:x2]
                k = self.blur_ksize if self.blur_ksize % 2 == 1 else self.blur_ksize + 1
                blurred = cv2.GaussianBlur(face_roi, (k, k), 30)
                frame[y1:y2, x1:x2] = blurred
            except Exception:
                # Array pixelation fallback if OpenCV blur is unavailable
                step = 10
                for y in range(y1, y2, step):
                    for x in range(x1, x2, step):
                        frame[y:y+step, x:x+step] = frame[y, x]

        return frame

    def render_silhouette(self, frame: np.ndarray, person_bbox: List[float], alpha: float = 0.65) -> np.ndarray:
        """
        Renders an anonymous digital silhouette over the worker to prevent facial/identifying surveillance
        while preserving ergonomic posture and material handling kinematics.
        """
        if frame is None or len(person_bbox) < 4:
            return frame

        h_img, w_img = frame.shape[:2]
        cx, cy, bw, bh = person_bbox
        
        x1 = max(0, int(cx - bw * 0.45))
        x2 = min(w_img, int(cx + bw * 0.45))
        y1 = max(0, int(cy - bh * 0.48))
        y2 = min(h_img, int(cy + bh * 0.48))

        if x2 > x1 and y2 > y1:
            sub = frame[y1:y2, x1:x2].astype(np.float32)
            color_overlay = np.full_like(sub, self.silhouette_color, dtype=np.float32)
            blended = (1.0 - alpha) * sub + alpha * color_overlay
            frame[y1:y2, x1:x2] = blended.astype(np.uint8)

        return frame

    def process_frame(self, frame: np.ndarray, detections: List[Any], anonymize_faces: bool = True, render_silhouettes: bool = False) -> np.ndarray:
        """
        Processes full frame through privacy shield policies.
        """
        if frame is None:
            return frame

        out_frame = frame.copy()
        for det in detections:
            # Handle both dicts and Detection objects
            cls_name = getattr(det, "class_name", det.get("class_name", "") if isinstance(det, dict) else "")
            bbox = getattr(det, "bbox", [det.get("x", 0), det.get("y", 0), det.get("w", 0), det.get("h", 0)] if isinstance(det, dict) else [])
            
            if cls_name == "person" and len(bbox) >= 4:
                if render_silhouettes:
                    out_frame = self.render_silhouette(out_frame, bbox)
                elif anonymize_faces:
                    out_frame = self.apply_face_blur(out_frame, bbox)

        return out_frame
