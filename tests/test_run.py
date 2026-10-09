import json
from datetime import datetime

import cv2
import numpy as np
import pytest

from pawwatch import run, store

T0 = datetime(2026, 10, 9, 18, 30).timestamp()
W, H, FPS = 160, 120, 10
LEFT, RIGHT = (40, 60), (120, 60)  # cat centers inside the food (left) and water (right) zones


def test_parse_start_from_filename():
    assert run.parse_start("data/videos/food_2026-10-09T1830.mp4") == T0


def test_parse_start_override():
    assert run.parse_start("clip.mp4", override="2026-10-09T18:30") == T0
    assert run.parse_start("food_2026-10-01T0000.mp4", override="2026-10-09T18:30") == T0


def test_parse_start_rejects_unnamed_file():
    with pytest.raises(ValueError, match="--start"):
        run.parse_start("IMG_0042.mp4")


def test_cat_zone_uses_highest_score_box_center():
    zs = [("food", [(0, 0), (80, 0), (80, 120), (0, 120)]), ("water", [(80, 0), (160, 0), (160, 120), (80, 120)])]
    dets = [("cat", 0.5, (10, 10, 50, 50)), ("cat", 0.9, (100, 10, 140, 50))]
    assert run.cat_zone(dets, zs) == "water"
    assert run.cat_zone([], zs) is None
    assert run.cat_zone([("dog", 0.95, (100, 10, 140, 50)), ("cat", 0.5, (10, 10, 50, 50))], zs) == "food"
    assert run.cat_zone([("cat", 0.9, (0, 0, 2, 2))], [("food", [(50, 50), (60, 50), (60, 60)])]) is None


def write_video(path, script):
    """script: [(seconds, cat center or None)]; the cat is a white square on black."""
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    assert out.isOpened()
    for seconds, center in script:
        for _ in range(seconds * FPS):
            frame = np.zeros((H, W, 3), np.uint8)
            if center:
                x, y = center
                frame[y - 15 : y + 15, x - 15 : x + 15] = 255
            out.write(frame)
    out.release()
    return path


class StubDetector:
    """Box around the white pixels: real frames go through, no model."""

    def infer(self, frame_bgr):
        ys, xs = np.nonzero(frame_bgr[:, :, 0] > 128)
        if not len(xs):
            return []
        return [("cat", 0.9, (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))]


@pytest.fixture
def zones_file(tmp_path):
    path = tmp_path / "cam_food.json"
    path.write_text(json.dumps({"camera": "cam_food", "zones": [
        {"name": "food", "polygon": [[0, 0], [80, 0], [80, 120], [0, 120]]},
        {"name": "water", "polygon": [[80, 0], [160, 0], [160, 120], [80, 120]]},
    ]}))
    return path


def rows(db):
    conn = store.connect(db)
    return [(e.camera, e.zone, e.start_ts - T0, e.duration_s, e.simulated) for e in store.events_between(conn, 0, 2e10)]


def test_pipeline_writes_visits(tmp_path, zones_file):
    video = write_video(tmp_path / "food_2026-10-09T1830.mp4", [(8, LEFT), (4, None), (2, RIGHT), (4, None), (7, RIGHT)])
    db = tmp_path / "events.db"
    run.process([video], zones_file, StubDetector(), store.connect(db), fps=5)
    # food 0-7.8 s; water 12-13.8 s and 18-24.8 s are 4.2 s apart (beyond tolerance): the 2 s one is too short
    assert rows(db) == [
        ("cam_food", "food", 0.0, pytest.approx(7.8), False),
        ("cam_food", "water", 18.0, pytest.approx(6.8), False),
    ]


def test_cli_processes_files_in_time_order(tmp_path, zones_file, monkeypatch):
    late = write_video(tmp_path / "food_2026-10-09T1831.mp4", [(6, LEFT)])
    early = write_video(tmp_path / "food_2026-10-09T1830.mp4", [(2, None), (6, LEFT)])
    devices = []
    monkeypatch.setattr(run, "make_detector", lambda **kw: devices.append(kw["device"]) or StubDetector())
    db = tmp_path / "events.db"
    run.main([str(late), str(early), "--zones", str(zones_file), "--db", str(db), "--fps", "1", "--device", "cpu"])
    assert devices == ["cpu"]
    assert rows(db) == [
        ("cam_food", "food", 2.0, 5.0, False),
        ("cam_food", "food", 60.0, 5.0, False),
    ]


def test_cli_start_override_needs_a_single_file(tmp_path, zones_file):
    with pytest.raises(SystemExit):
        run.main(["a.mp4", "b.mp4", "--zones", str(zones_file), "--start", "2026-10-09T18:30"])
