from types import SimpleNamespace

import numpy as np

from pawwatch import overlay

W, H = 640, 360
ZONES = [("food", [(0, 0), (320, 0), (320, 360), (0, 360)]), ("forbidden", [(320, 0), (640, 0), (640, 360), (320, 360)])]
CAT = [("cat", 0.9, (400, 100, 500, 200))]


def blank():
    return np.zeros((H, W, 3), np.uint8)


def test_cat_box_is_red_in_a_forbidden_zone_and_green_elsewhere():
    left_edge = (150, 400)  # (row, col) on the box's left side
    assert tuple(overlay.render(blank(), CAT, ZONES, "forbidden", {})[left_edge]) == overlay.RED
    assert tuple(overlay.render(blank(), CAT, ZONES, None, {})[left_edge]) == overlay.GREEN


def test_counts_text_lists_every_zone_of_the_camera():
    assert overlay.counts_text(ZONES, {"forbidden": 2}) == "food 0 · forbidden 2"


def test_counts_are_drawn_and_the_input_frame_is_untouched():
    frame = blank()
    before = overlay.render(frame, [], ZONES, None, {})
    after = overlay.render(frame, [], ZONES, None, {"food": 1})
    assert not frame.any()
    assert (before != after).any()  # the count ticked up on screen


def test_caption_is_drawn():
    assert overlay.CAPTION == "Running on laptop · YOLOv8n · target: ASUS UGen300"
    bottom = overlay.render(blank(), [], [], None, {})[H - 40 :]
    assert bottom.any()


def test_window_counts_as_closed_only_after_it_was_seen_open(monkeypatch):
    win = SimpleNamespace(title="t", seen_visible=False)
    reported = iter([0.0, 1.0, 1.0, 0.0])  # a backend that reports late; then the user closes it
    monkeypatch.setattr(overlay.cv2, "getWindowProperty", lambda title, prop: next(reported))
    assert [overlay.closed_by_user(win) for _ in range(4)] == [False, False, False, True]


def test_backend_that_never_reports_visible_never_closes(monkeypatch):  # macOS Cocoa
    win = SimpleNamespace(title="t", seen_visible=False)
    monkeypatch.setattr(overlay.cv2, "getWindowProperty", lambda title, prop: -1.0)
    assert not any(overlay.closed_by_user(win) for _ in range(3))
