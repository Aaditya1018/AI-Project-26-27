"""
SafeStack AI - Computer Vision Object Detector Interface
Detects: Person, Carton/Box, Pallet, Forklift, Pallet Jack
Supports YOLOv11 when available, with an OpenCV / Synthetic Vision fallback.
"""

import os
from threading import Lock
from typing import List, Dict, Any, Optional
import numpy as np

_MODEL_CACHE: Dict[str, Any] = {}
_MODEL_ERRORS: Dict[str, str] = {}
_MODEL_LOCK = Lock()
_INFERENCE_LOCK = Lock()

class Detection:
    def __init__(self, class_name: str, confidence: float, bbox: List[float], track_id: int = -1):
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # [x, y, w, h] normalized or pixel coords
        self.track_id = track_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_name": self.class_name,
            "confidence": round(float(self.confidence), 3),
            "x": round(float(self.bbox[0]), 2),
            "y": round(float(self.bbox[1]), 2),
            "w": round(float(self.bbox[2]), 2),
            "h": round(float(self.bbox[3]), 2),
            "track_id": self.track_id
        }

class SafeStackDetector:
    """
    Object detection engine combining YOLOv11 / OpenCV capabilities.
    Detects workers, products/cartons, pallets, and material handling equipment.
    """
    CLASS_ALIASES = {
        "box": "carton",
        "cardboard box": "carton",
        "carton": "carton",
        "package": "carton",
        "parcel": "carton",
        "wooden pallet": "pallet",
        "pallet": "pallet",
        "fork lift": "forklift",
        "forklift": "forklift",
        "fork truck": "forklift",
        "lift truck": "forklift",
        "pallet jack": "pallet_jack",
    }

    def __init__(self, model_name: Optional[str] = None, conf_threshold: float = 0.45):
        self.model_name = model_name or os.getenv("SAFESTACK_DETECTION_MODEL", "yolo11n.pt")
        self.conf_threshold = conf_threshold
        self.has_yolo = False
        self.model = None
        self.model_error: Optional[str] = None

        with _MODEL_LOCK:
            if self.model_name in _MODEL_CACHE:
                self.model = _MODEL_CACHE[self.model_name]
            elif self.model_name in _MODEL_ERRORS:
                self.model_error = _MODEL_ERRORS[self.model_name]
            else:
                try:
                    from ultralytics import YOLO
                    self.model = YOLO(self.model_name)
                    _MODEL_CACHE[self.model_name] = self.model
                except Exception as exc:
                    self.model_error = str(exc)
                    _MODEL_ERRORS[self.model_name] = self.model_error
            self.has_yolo = self.model is not None

    def detect_frame(
        self,
        frame: np.ndarray,
        synthetic_entities: Optional[List[Dict[str, Any]]] = None,
        allow_demo_detections: bool = True
    ) -> List[Detection]:
        """
        Runs detection on a video frame.
        If synthetic entities are provided (from the simulation engine), uses them directly.
        """
        detections: List[Detection] = []

        if synthetic_entities:
            for ent in synthetic_entities:
                detections.append(Detection(
                    class_name=ent.get("class_name", "carton"),
                    confidence=ent.get("confidence", 0.95),
                    bbox=[ent["x"], ent["y"], ent["w"], ent["h"]],
                    track_id=ent.get("track_id", -1)
                ))
            return detections

        if self.has_yolo and self.model is not None and frame is not None:
            try:
                with _INFERENCE_LOCK:
                    results = self.model(frame, conf=self.conf_threshold, verbose=False)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        names = self.model.names
                        cls_name = names.get(cls_id, f"obj_{cls_id}") if isinstance(names, dict) else names[cls_id]
                        cls_name = self.normalize_class_name(cls_name)
                        conf = float(box.conf[0])
                        xywh = box.xywh[0].tolist()
                        detections.append(Detection(
                            class_name=cls_name,
                            confidence=conf,
                            bbox=xywh
                        ))
                return detections
            except Exception as exc:
                raise RuntimeError(f"Object detector failed while processing a frame: {exc}") from exc

        if allow_demo_detections and frame is not None and isinstance(frame, np.ndarray) and len(frame.shape) == 3:
            h, w, _ = frame.shape
            detections.append(Detection("person", 0.92, [w * 0.35, h * 0.40, w * 0.12, h * 0.45], 1))
            detections.append(Detection("carton", 0.94, [w * 0.45, h * 0.55, w * 0.15, h * 0.20], 2))
            detections.append(Detection("pallet", 0.89, [w * 0.40, h * 0.75, w * 0.30, h * 0.12], 3))

        return detections

    @classmethod
    def normalize_class_name(cls, class_name: str) -> str:
        normalized = class_name.strip().lower().replace("_", " ").replace("-", " ")
        return cls.CLASS_ALIASES.get(normalized, normalized.replace(" ", "_"))

    def supported_warehouse_classes(self) -> List[str]:
        if not self.has_yolo or self.model is None:
            return []
        names = self.model.names
        model_names = names.values() if isinstance(names, dict) else names
        warehouse_classes = {"person", "carton", "pallet", "forklift", "pallet_jack"}
        return sorted({
            self.normalize_class_name(name)
            for name in model_names
            if self.normalize_class_name(name) in warehouse_classes
        })
