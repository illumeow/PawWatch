"""Detection window for the demo: boxes, zones, live visit counts. Owner: A.

render() draws on a copy of a frame and is pure; Window only displays. Nothing here saves a frame:
the demo video is a screen capture taken outside the program.
"""
import time

import cv2
import numpy as np

CAPTION = "Running on laptop · YOLOv8n · target: ASUS UGen300"
GREEN, RED = (0, 220, 0), (0, 0, 255)  # BGR
ZONE_COLORS = {"food": (0, 165, 255), "water": (255, 180, 0), "litter": (200, 120, 200), "forbidden": RED}
FONT = cv2.FONT_HERSHEY_SIMPLEX


def counts_text(zone_list, counts):
    """Visits logged so far for each of the camera's zones, e.g. 'food 2 · water 0'."""
    return " · ".join(f"{name} {counts.get(name, 0)}" for name, _ in zone_list)


def render(frame, detections, zone_list, zone, counts):
    """Annotated copy of a frame. zone is the cat's current zone; the top cat box turns red in a forbidden one."""
    img = frame.copy()
    s = scale(img)
    thick = max(1, round(2 * s))
    band = round(56 * s)
    draw_zones(img, zone_list, top=band)

    cats = sorted((d for d in detections if d[0] == "cat"), key=lambda d: -d[1])
    for i, (label, score, (x1, y1, x2, y2)) in enumerate(cats):
        color = RED if i == 0 and zone == "forbidden" else GREEN
        cv2.rectangle(img, (x1, y1), (x2, y2), color, max(2, round(3 * s)))
        cv2.putText(img, f"{label} {score:.2f}", (x1, max(y1 - round(8 * s), band + round(24 * s))),
                    FONT, 0.8 * s, color, thick, cv2.LINE_AA)

    img[:band] //= 3  # darkened bands keep the text readable on any footage
    img[-band:] //= 3
    _text(img, "Visits  " + counts_text(zone_list, counts), (round(16 * s), round(38 * s)), s, (255, 255, 255))
    caption = 0.8 * s
    width = cv2.getTextSize(CAPTION, FONT, caption, max(1, round(2 * caption)))[0][0]
    caption *= min(1.0, (img.shape[1] - 32 * s) / width)  # portrait frames: shrink the caption to fit
    _text(img, CAPTION, (round(16 * s), img.shape[0] - round(18 * s)), caption, (220, 220, 220))
    return img


def scale(img):
    """Sizes are tuned for 1280 px on the long side, so portrait phone clips get the same text size as landscape."""
    return max(img.shape[:2]) / 1280


def draw_zones(img, zone_list, top=0):
    """Zone outlines with their names, in place. Labels stay below `top` px (the counts band)."""
    s = scale(img)
    for name, polygon in zone_list:
        color = ZONE_COLORS[name]
        pts = [(round(x), round(y)) for x, y in polygon]
        cv2.polylines(img, [np.array(pts, np.int32)], True, color, max(1, round(2 * s)), cv2.LINE_AA)
        x, y = min(p[0] for p in pts), min(p[1] for p in pts)
        cv2.putText(img, name, (x + round(8 * s), max(y, top) + round(32 * s)),
                    FONT, 0.9 * s, color, max(1, round(2 * s)), cv2.LINE_AA)


def _text(img, text, org, scale, color):
    """putText with ' · ' drawn as a dot: Hershey fonts are ASCII only."""
    thick = max(1, round(2 * scale))
    x, y = org
    for i, part in enumerate(text.split(" · ")):
        if i:
            gap = round(14 * scale)
            cv2.circle(img, (x + gap, y - round(10 * scale)), max(2, round(4 * scale)), color, -1, cv2.LINE_AA)
            x += 2 * gap
        cv2.putText(img, part, (x, y), FONT, scale, color, thick, cv2.LINE_AA)
        x += cv2.getTextSize(part, FONT, scale, thick)[0][0]


def closed_by_user(win):
    """True once a window that was shown has been closed with its title-bar button.

    win needs .title and .seen_visible. Some backends (macOS Cocoa) never report the window as visible,
    so the property is only trusted after it has said visible once.
    """
    visible = cv2.getWindowProperty(win.title, cv2.WND_PROP_VISIBLE) >= 1
    win.seen_visible = win.seen_visible or visible
    return win.seen_visible and not visible


class Window:
    """Shows rendered frames paced to video time, so recorded footage plays back like a live feed."""

    def __init__(self, title="PawWatch"):
        self.title = title
        self.last = None  # (video offset, monotonic time) of the frame on screen
        self.seen_visible = False
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)

    def show(self, img, offset):
        """Display img once its video offset is due. Returns False when the user presses q or closes the window."""
        keys = []
        if self.last and offset >= self.last[0]:  # an earlier offset means a new file: show at once
            wait = self.last[1] + offset - self.last[0] - time.monotonic()
            if wait > 0:
                keys.append(cv2.waitKey(max(1, round(wait * 1000))))  # waitKey also keeps the window responsive
        cv2.imshow(self.title, img)
        keys.append(cv2.waitKey(1))
        self.last = (offset, time.monotonic())
        return not closed_by_user(self) and not any(k & 0xFF == ord("q") for k in keys if k != -1)

    def close(self):
        cv2.destroyWindow(self.title)
        cv2.waitKey(1)
