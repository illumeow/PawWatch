"""Draw a camera's zones on a frame of its clip and write its zones file. Owner: A.

Run: uv run python scripts/draw_zones.py data/videos/food_2026-10-09T1830.mp4 config/zones/cam_food.json
     add --at 12.5 to draw on the frame 12.5 s in (default: the first frame)

In the window:
    click         add a vertex
    1 2 3 4       zone name: food, water, litter, forbidden
    n or Enter    close the polygon (3+ vertices)
    u             undo the last vertex, or the last zone
    s             save and quit (asks in the terminal before overwriting an existing file)
    q or Esc      quit without saving

Zones already in the file are loaded, drawn and kept unless undone. Draw the food and water polygons around where
the cat's body center is while it eats or drinks, not just the bowl. Only the JSON is written, never a frame.
"""
import argparse
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np

from pawwatch import overlay, store, zones

MAX_W, MAX_H = 1280, 800  # the window is scaled to fit; clicks are mapped back to original pixels
HELP_H = 36  # help bar at the top of the window; clicks on it are ignored


def read_frame(clip, at_s):
    cap = cv2.VideoCapture(str(clip))
    cap.set(cv2.CAP_PROP_POS_MSEC, at_s * 1000)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise SystemExit(f"cannot read a frame at {at_s} s from {clip}")
    return frame


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("clip", help="a video from the camera, at its native resolution")
    ap.add_argument("out", help="zones file to write, e.g. config/zones/cam_food.json")
    ap.add_argument("--at", type=float, default=0.0, help="seconds into the clip to draw on (default: %(default)s)")
    ap.add_argument("--camera", help="camera name (default: from the existing file, else the file name)")
    args = ap.parse_args()

    out = Path(args.out)
    camera, drawn = (zones.load_zones(out) if out.exists() else (out.stem, []))
    camera = args.camera or camera
    frame = read_frame(args.clip, args.at)
    h, w = frame.shape[:2]
    scale = min(1.0, MAX_W / w, MAX_H / h)
    state = {"name": store.ZONES[0], "points": [], "dirty": True}
    win = SimpleNamespace(title="PawWatch zones", seen_visible=False)

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and y >= HELP_H:
            state["points"].append((x / scale, y / scale))
            state["dirty"] = True

    cv2.namedWindow(win.title, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
    cv2.setMouseCallback(win.title, on_mouse)
    print(f"camera {camera}, frame {w}x{h}; keys: 1-4 name, click vertex, n close, u undo, s save, q quit")
    saved = False
    while not saved:
        if state["dirty"]:
            cv2.imshow(win.title, draw(frame, drawn, state["name"], state["points"], scale))
            state["dirty"] = False
        key = cv2.waitKey(30) & 0xFF
        if overlay.closed_by_user(win) or key in (ord("q"), 27):
            print("quit without saving")
            break
        if ord("1") <= key < ord("1") + len(store.ZONES):
            state["name"] = store.ZONES[key - ord("1")]
        elif key in (ord("n"), 13, 10):
            if len(state["points"]) >= 3:
                drawn.append((state["name"], state["points"]))
                state["points"] = []
            else:
                print("a zone needs at least 3 vertices")
        elif key == ord("u"):
            if state["points"]:
                state["points"].pop()
            elif drawn:
                drawn.pop()
        elif key == ord("s"):
            saved = save(out, camera, drawn, state["points"])
        else:
            continue
        state["dirty"] = True
    cv2.destroyAllWindows()


def draw(frame, drawn, name, points, scale):
    """The frame with the finished zones, the polygon in progress and a help line, scaled for the window."""
    img = frame.copy()
    overlay.draw_zones(img, drawn)
    color = overlay.ZONE_COLORS[name]
    pts = np.array([(round(x), round(y)) for x, y in points], np.int32)
    if len(pts):
        cv2.polylines(img, [pts], False, color, 2, cv2.LINE_AA)
        for p in pts:
            cv2.circle(img, tuple(int(v) for v in p), 5, color, -1, cv2.LINE_AA)
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) if scale < 1 else img
    names = "  ".join(f"{i}:{z}" for i, z in enumerate(store.ZONES, 1))
    img[:HELP_H] //= 3
    cv2.putText(img, f"zone: {name}   [{names}]   n close  u undo  s save  q quit", (10, 24),
                overlay.FONT, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def save(out, camera, drawn, points):
    """Write the zones file. Returns True when written."""
    if points:
        print("finish (n) or undo (u) the polygon in progress first")
        return False
    if not drawn:
        print("no zones drawn")
        return False
    if out.exists() and input(f"{out} exists. Overwrite? [y/N] ").strip().lower() != "y":
        print("not saved; keep drawing or press q")
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    zones.save_zones(out, camera, drawn)
    print(f"wrote {len(drawn)} zones for {camera} to {out}")
    return True


if __name__ == "__main__":
    main()
