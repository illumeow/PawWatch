"""CLI: one camera's video files + its zones file -> visits in SQLite. Owner: A.

Usage:
    uv run python -m pawwatch.run data/videos/food_2026-10-09T1830.mp4 --zones config/zones/cam_food.json
    uv run python -m pawwatch.run data/videos/food_*.mp4 --zones config/zones/cam_food.json --fps 1 --device cuda
    uv run python -m pawwatch.run data/videos/food_2026-10-09T1830.mp4 --zones config/zones/cam_food.json --fps 5 --show

Per sampled frame: detector.infer -> highest-score box center -> zones.zone_at -> events.VisitTracker
-> store.insert_event for each finished visit, and alarm.trigger on every frame the cat is in a forbidden zone
(the alarm applies its own cooldown). With --show, each frame is also drawn in the detection window (pawwatch.overlay);
the per-frame logic is the same either way, so windowed and headless runs store the same rows.
Each file also gets a recordings row (camera, its zones, start to last processed frame), so the dashboard compares
only the hours that were actually filmed.
Frames are only read and displayed, never written anywhere.
Timestamps are video time: the recording start from the filename (<zone>_YYYY-MM-DDTHHMM.mp4) plus the
frame offset. Files are processed in time order with one tracker, so a visit spanning two files is one visit.
"""
import argparse
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import cv2

from pawwatch import alarm, events, overlay, store, zones
from pawwatch.detector import make_detector

FILENAME_START = re.compile(r"_(\d{4}-\d{2}-\d{2}T\d{4})$")


def parse_start(path, override=None):
    """Recording start of a video file as unix seconds (local time), from its name or an ISO override."""
    if override:
        return datetime.fromisoformat(override).timestamp()
    m = FILENAME_START.search(Path(path).stem)
    if not m:
        raise ValueError(f"{path}: name doesn't end in _YYYY-MM-DDTHHMM; pass --start to give the recording start")
    return datetime.strptime(m.group(1), "%Y-%m-%dT%H%M").timestamp()


def cat_zone(detections, zone_list):
    """Zone of the highest-score cat box's center, or None (single-cat MVP)."""
    cats = [d for d in detections if d[0] == "cat"]
    if not cats:
        return None
    _, _, (x1, y1, x2, y2) = max(cats, key=lambda d: d[1])
    return zones.zone_at(((x1 + x2) / 2, (y1 + y2) / 2), zone_list)


def sampled_frames(path, fps):
    """Yield (offset_s, frame) at about `fps` frames per second of video.

    Offsets are the container's frame timestamps, so variable-frame-rate phone footage stays in sync.
    """
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"cannot open {path}")
    next_sample = 0.0
    try:
        while cap.grab():  # grab without decoding; decode only the sampled frames
            offset = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if offset >= next_sample - 1e-3:  # 1 ms slack: summed 1/fps steps drift past exact frame times
                ok, frame = cap.retrieve()
                if ok:
                    yield offset, frame
                next_sample = max(next_sample + 1 / fps, offset)
    finally:
        cap.release()


def frames_in_order(files, fps):
    """Yield (t0, offset_s, frame) over [(t0, path), ...] in order."""
    for t0, path in files:
        print(f"{path.name}: start {datetime.fromtimestamp(t0):%Y-%m-%d %H:%M}", flush=True)
        for offset, frame in sampled_frames(path, fps):
            yield t0, offset, frame


def process(paths, zones_path, detector, conn, fps=1.0, start=None,
            min_dwell=events.MIN_DWELL_S, gap_tolerance=events.GAP_TOLERANCE_S,
            forbidden_dwell=events.FORBIDDEN_DWELL_S, window=None):
    """Run one camera's videos through the pipeline, ring the alarm on forbidden frames and store each visit as it
    finishes. Returns the visits.

    window: an overlay.Window to draw each frame in, or None for headless. Closing it stops early; the open visit
    is still stored.
    """
    camera, zone_list = zones.load_zones(zones_path)
    files = sorted((parse_start(p, start), Path(p)) for p in paths)
    tracker = events.VisitTracker(min_dwell, gap_tolerance, forbidden_dwell)
    stored = []
    counts = Counter()  # visits stored so far per zone, for the window
    watched = [z for z in store.ZONES if any(name == z for name, _ in zone_list)]
    recordings = {}  # file start -> recordings row id

    def save(visits):
        for v in visits:
            store.insert_event(conn, camera, v.zone, v.start_ts, v.end_ts)
            print(f"{camera} {v.zone:6} {datetime.fromtimestamp(v.start_ts):%Y-%m-%d %H:%M:%S}"
                  f" {v.end_ts - v.start_ts:6.1f} s", flush=True)
        stored.extend(visits)
        counts.update(v.zone for v in visits)

    try:
        for t0, offset, frame in frames_in_order(files, fps):
            ts = t0 + offset
            if t0 not in recordings:
                recordings[t0] = store.insert_recording(conn, camera, watched, t0)
            store.extend_recording(conn, recordings[t0], ts)
            detections = detector.infer(frame)
            zone = cat_zone(detections, zone_list)
            save(tracker.update(ts, zone))
            if tracker.alarm_zone:
                alarm.trigger(camera, tracker.alarm_zone, ts)
            if window and not window.show(overlay.render(frame, detections, zone_list, zone, counts), offset):
                break
    finally:
        if window:
            window.close()
    save(tracker.close())
    return stored


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Video files of one camera + its zones file -> visits in SQLite.",
        epilog="The cat in a forbidden zone rings the alarm. Set PAWWATCH_MUTE=1 to keep bulk runs silent.")
    ap.add_argument("videos", nargs="+", help="video files of one camera, any order")
    ap.add_argument("--zones", required=True, help="zones file, e.g. config/zones/cam_food.json")
    ap.add_argument("--db", default=str(store.DEFAULT_DB), help="events database (default: %(default)s)")
    ap.add_argument("--fps", type=float, default=1.0, help="frames per second to process: ~5 live, 1 bulk (default: %(default)s)")
    ap.add_argument("--show", action="store_true",
                    help="detection window paced to video time, q to stop (try --fps 5); default: headless")
    ap.add_argument("--device", help="detector device: cpu, cuda or mps (default: the detector's choice)")
    ap.add_argument("--start", help="recording start, e.g. 2026-10-09T18:30, for a single file without a dated name")
    ap.add_argument("--min-dwell", type=float, default=events.MIN_DWELL_S, help="seconds in a zone to count a visit, except forbidden zones")
    ap.add_argument("--forbidden-dwell", type=float, default=events.FORBIDDEN_DWELL_S,
                    help="seconds in a forbidden zone to count a visit (default: %(default)s)")
    ap.add_argument("--gap-tolerance", type=float, default=events.GAP_TOLERANCE_S, help="dropout seconds that don't end a visit")
    args = ap.parse_args(argv)
    if args.fps <= 0:
        ap.error("--fps must be positive")
    if args.start and len(args.videos) > 1:
        ap.error("--start applies to a single file; name multiple files <zone>_YYYY-MM-DDTHHMM.mp4 instead")

    try:
        zones.load_zones(args.zones)  # fail on a bad zones file before loading the model
        for p in args.videos:
            parse_start(p, args.start)
    except ValueError as e:
        ap.error(str(e))
    detector = make_detector(device=args.device)
    stored = process(args.videos, args.zones, detector, store.connect(args.db), args.fps, args.start,
                     args.min_dwell, args.gap_tolerance, args.forbidden_dwell,
                     window=overlay.Window() if args.show else None)
    print(f"stored {len(stored)} visits in {args.db}")


if __name__ == "__main__":
    main()
