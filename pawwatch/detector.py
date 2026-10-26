"""Cat detection.

Every backend returns [(label, score, (x1, y1, x2, y2))] in original-image pixels, the same contract as
ObjectDetector in ugen300-demos, so the UGen300 backend drops in (see docs/UGen300Notes.md).
"""

from typing import Protocol

import numpy as np

COCO_CAT = 15

Box = tuple[int, int, int, int]  # x1, y1, x2, y2 in original-image pixels
Detection = tuple[str, float, Box]  # (label, score, box): the contract every backend returns


class Detector(Protocol):
    """Any backend: Ultralytics on the laptop today, Hailo on the UGen300 later."""

    def infer(self, frame_bgr: np.ndarray) -> list[Detection]: ...


class UltralyticsDetector:
    """Laptop backend: off-the-shelf COCO YOLO, cats only."""

    def __init__(self, weights: str = "yolov8n.pt", conf: float = 0.4, device: str | None = None):
        from ultralytics import YOLO

        self.model = YOLO(weights)
        self.conf = conf
        self.device = device  # None = Ultralytics picks (CUDA if present); "mps" on Macs

    def infer(self, frame_bgr: np.ndarray) -> list[Detection]:
        from ultralytics.engine.results import Results

        results = list(
            self.model.predict(frame_bgr, conf=self.conf, classes=[COCO_CAT], device=self.device, verbose=False)
        )
        result = results[0] if results else None
        if not isinstance(result, Results) or result.boxes is None:
            return []
        boxes = result.boxes
        found = []
        for box, score, cls in zip(boxes.xyxy.tolist(), boxes.conf.tolist(), boxes.cls.tolist(), strict=True):
            x1, y1, x2, y2 = (int(v) for v in box)
            found.append((result.names[int(cls)], float(score), (x1, y1, x2, y2)))
        return found


def make_detector(backend: str = "ultralytics", **kwargs) -> Detector:
    if backend == "ultralytics":
        return UltralyticsDetector(**kwargs)
    if backend == "hailo":
        raise NotImplementedError("UGen300 backend: port hailo_detect.py, see docs/UGen300Notes.md")
    raise ValueError(f"unknown backend {backend!r}")
