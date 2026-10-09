"""Cat detection. Owner: A.

Every backend returns [(label, score, (x1, y1, x2, y2))] in original-image pixels, the same contract as
ObjectDetector in ugen300-demos, so the UGen300 backend drops in (see docs/UGen300Notes.md).
"""

COCO_CAT = 15


class UltralyticsDetector:
    """Laptop backend: off-the-shelf COCO YOLO, cats only."""

    def __init__(self, weights="yolov8n.pt", conf=0.4, device=None):
        from ultralytics import YOLO

        self.model = YOLO(weights)
        self.conf = conf
        self.device = device  # None = Ultralytics picks (CUDA if present); "mps" on Macs

    def infer(self, frame_bgr):
        result = self.model(frame_bgr, conf=self.conf, classes=[COCO_CAT], device=self.device, verbose=False)[0]
        return [
            (result.names[int(cls)], float(score), tuple(int(v) for v in box))
            for box, score, cls in zip(result.boxes.xyxy.tolist(), result.boxes.conf.tolist(), result.boxes.cls.tolist())
        ]


def make_detector(backend="ultralytics", **kwargs):
    if backend == "ultralytics":
        return UltralyticsDetector(**kwargs)
    if backend == "hailo":
        raise NotImplementedError("UGen300 backend: port hailo_detect.py, see docs/UGen300Notes.md")
    raise ValueError(f"unknown backend {backend!r}")
