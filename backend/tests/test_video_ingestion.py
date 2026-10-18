from types import SimpleNamespace

import numpy as np
import pytest

from backend.cv_pipeline.detector import SafeStackDetector
from backend.cv_pipeline.video_processor import InjectedVideoProcessor


class FakeCapture:
    def __init__(self, frames=6, opened=True):
        self.frames = [np.zeros((48, 64, 3), dtype=np.uint8) for _ in range(frames)]
        self.opened = opened

    def isOpened(self):
        return self.opened

    def get(self, _property):
        return 25.0

    def read(self):
        if not self.frames:
            return False, None
        return True, self.frames.pop(0)

    def release(self):
        pass


def test_detector_does_not_substitute_demo_objects_for_uploaded_frames():
    detector = SafeStackDetector()
    detector.has_yolo = False
    detector.model = None

    detections = detector.detect_frame(
        np.zeros((48, 64, 3), dtype=np.uint8),
        allow_demo_detections=False
    )

    assert detections == []


def test_detector_returns_model_boxes_and_normalizes_warehouse_labels():
    detector = SafeStackDetector()
    detector.has_yolo = True
    detector.model = lambda *_args, **_kwargs: [
        SimpleNamespace(boxes=[
            SimpleNamespace(
                cls=np.array([0]),
                conf=np.array([0.91]),
                xywh=np.array([[120, 80, 40, 30]])
            )
        ])
    ]
    detector.model.names = {0: "cardboard box"}

    detections = detector.detect_frame(
        np.zeros((160, 160, 3), dtype=np.uint8),
        allow_demo_detections=False
    )

    assert len(detections) == 1
    assert detections[0].class_name == "carton"
    assert detections[0].confidence == 0.91
    assert detections[0].bbox == [120, 80, 40, 30]


def test_unavailable_detector_returns_readings_as_unavailable_not_safe(tmp_path, monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "cv2", SimpleNamespace(
        CAP_PROP_FPS=5,
        VideoCapture=lambda _path: FakeCapture(),
        imwrite=lambda *_args: True
    ))
    video_path = tmp_path / "warehouse.mp4"
    video_path.write_bytes(b"video")
    processor = InjectedVideoProcessor(str(video_path))
    processor.detector.has_yolo = False
    processor.detector.model_error = "Model weights are not installed"

    incidents = processor.process_and_detect_events()

    assert incidents == []
    assert processor.last_scan_summary["detector_status"] == "unavailable"
    assert processor.last_scan_summary["frames_read"] == 6
    assert processor.last_scan_summary["frames_analyzed"] == 3
    assert processor.last_scan_summary["detection_counts"] == {}
    assert "do not mean the footage is safe" in processor.last_scan_summary["interpretation"]


def test_undecodable_video_does_not_create_a_fake_incident(tmp_path, monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "cv2", SimpleNamespace(
        CAP_PROP_FPS=5,
        VideoCapture=lambda _path: FakeCapture(opened=False)
    ))
    video_path = tmp_path / "invalid.mp4"
    video_path.write_bytes(b"not a valid video")
    processor = InjectedVideoProcessor(str(video_path))
    monkeypatch.setattr(
        "backend.cv_pipeline.video_processor.EventDBManager.insert_event",
        lambda _event: pytest.fail("Invalid video must not create a fabricated event")
    )

    with pytest.raises(ValueError, match="Could not decode uploaded video"):
        processor.process_and_detect_events()


def test_custom_video_live_frame_does_not_use_demo_boxes(tmp_path, monkeypatch):
    import sys
    from backend.simulation.scenario_runner import LiveBayStream

    class FakeFrameCapture(FakeCapture):
        def set(self, _property, _value):
            return True

    monkeypatch.setitem(sys.modules, "cv2", SimpleNamespace(
        VideoCapture=lambda _path: FakeFrameCapture()
    ))
    stream = LiveBayStream("BAY-01", "Test Bay")
    stream.detector.has_yolo = False
    stream.custom_video_path = str(tmp_path / "warehouse.mp4")
    stream.custom_cap = FakeFrameCapture()
    detections_used = []
    stream.detector.detect_frame = lambda _frame, **kwargs: (
        detections_used.append(kwargs) or []
    )

    stream.get_current_frame(enable_privacy=False)

    assert detections_used == [{"allow_demo_detections": False}]
