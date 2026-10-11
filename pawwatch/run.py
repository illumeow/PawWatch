"""CLI: one camera's video files + its zones file -> visits in SQLite. Owner: A.

Usage:
    uv run python -m pawwatch.run data/videos/food_2026-10-09T1830.mp4 --zones config/zones/cam_food.json
    uv run python -m pawwatch.run data/videos/food_*.mp4 --zones config/zones/cam_food.json --fps 1 --device cuda
    uv run python -m pawwatch.run data/videos/food_2026-10-09T1830.mp4 --zones config/zones/cam_food.json --fps 5 --show

Per sampled frame: detector.infer -> highest-score box -> zones.zone_for_box (most overlap) -> events.VisitTracker
-> store.insert_event for each finished visit, and alarm.trigger on every frame the cat is in a forbidden zone
(the alarm applies its own cooldown). With --show, each frame is also drawn in the detection window (pawwatch.overlay);
the per-frame logic is the same either way, so windowed and headless runs store the same rows.
Each file also gets a recordings row (camera, its zones, start to last processed frame), so the dashboard compares
only the hours that were actually filmed.
Frames are only read and displayed, never written anywhere.
Timestamps are video time: the recording start from the filename plus the frame offset. Two name formats:
<zone>_YYYY-MM-DDTHHMM.mp4 (ours) and YYYYMMDD-HHMMSS-<microseconds>-<n>.avi (the overnight camera's segments).
Files are processed in time order with one tracker, so a visit spanning two files is one visit.
"""

import argparse
import re
import sqlite3
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from pawwatch import alarm, events, overlay, store, zones
from pawwatch.detector import Detection, Detector, make_detector

FILENAME_STARTS = [  # (pattern on the file stem, strptime format of its first group)
    (re.compile(r"_(\d{4}-\d{2}-\d{2}T\d{4})$"), "%Y-%m-%dT%H%M"),
    (re.compile(r"^(\d{8}-\d{6})-\d+-\d+$"), "%Y%m%d-%H%M%S"),
]


def parse_start(path: str | Path, override: str | None = None) -> float:
    """Recording start of a video file as unix seconds (local time), from its name or an ISO override."""
    if override:
        return datetime.fromisoformat(override).timestamp()
    stem = Path(path).stem
    for pattern, fmt in FILENAME_STARTS:
        if m := pattern.search(stem):
            return datetime.strptime(m.group(1), fmt).timestamp()
    raise ValueError(
        f"{path}: name doesn't end in _YYYY-MM-DDTHHMM or look like YYYYMMDD-HHMMSS-...;"
        " pass --start to give the recording start"
    )


def cat_zone(detections: Sequence[Detection], zone_list: Iterable[zones.Zone]) -> str | None:
    """Zone the highest-score cat box overlaps most, or None (single-cat MVP)."""
    cats = [d for d in detections if d[0] == "cat"]
    if not cats:
        return None
    return zones.zone_for_box(max(cats, key=lambda d: d[1])[2], zone_list)


def sampled_frames(path: str | Path, fps: float) -> Iterator[tuple[float, np.ndarray]]:
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


def frames_in_order(files: Iterable[tuple[float, Path]], fps: float) -> Iterator[tuple[float, float, np.ndarray]]:
    """Yield (t0, offset_s, frame) over [(t0, path), ...] in order."""
    for t0, path in files:
        print(f"{path.name}: start {datetime.fromtimestamp(t0):%Y-%m-%d %H:%M}", flush=True)
        for offset, frame in sampled_frames(path, fps):
            yield t0, offset, frame


def process(
    paths: Iterable[str | Path],
    zones_path: str | Path,
    detector: Detector,
    conn: sqlite3.Connection,
    fps: float = 1.0,
    start: str | None = None,
    min_dwell: float = events.MIN_DWELL_S,
    gap_tolerance: float = events.GAP_TOLERANCE_S,
    forbidden_dwell: float = events.FORBIDDEN_DWELL_S,
    window: overlay.Display | None = None,
) -> list[events.Visit]:
    """Run one camera's videos through the pipeline, ring the alarm on forbidden frames and store each visit live:
    written once it qualifies, its end moved forward while the cat stays. Returns the finished visits.

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
    rows = {}  # (zone, start) of a visit already written -> its events row id

    def write(v: events.Visit) -> None:
        """Insert the visit the first time it's written, then move its end forward."""
        key = (v.zone, v.start_ts)
        if key in rows:
            store.extend_event(conn, rows[key], v.end_ts)
        else:
            rows[key] = store.insert_event(conn, camera, v.zone, v.start_ts, v.end_ts)

    def save(visits: list[events.Visit]) -> None:
        for v in visits:
            write(v)
            rows.pop((v.zone, v.start_ts), None)
            print(
                f"{camera} {v.zone:6} {datetime.fromtimestamp(v.start_ts):%Y-%m-%d %H:%M:%S}"
                f" {v.end_ts - v.start_ts:6.1f} s",
                flush=True,
            )
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
            if tracker.counting and tracker.open:  # live: the visit qualified, so it will be stored; write it now
                write(tracker.open)
            if tracker.alarm_zone:
                alarm.trigger(camera, tracker.alarm_zone, ts)
            shown = counts + Counter(
                [tracker.counting] if tracker.counting else []
            )  # the open visit counts once it qualifies
            if window and not window.show(overlay.render(frame, detections, zone_list, zone, shown), offset):
                break
    finally:
        if window:
            window.close()
    save(tracker.close())
    return stored


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description="Video files of one camera + its zones file -> visits in SQLite.",
        epilog="The cat in a forbidden zone rings the alarm. Set PAWWATCH_MUTE=1 to keep bulk runs silent.",
    )
    ap.add_argument("videos", nargs="+", help="video files of one camera, any order")
    ap.add_argument("--zones", required=True, help="zones file, e.g. config/zones/cam_food.json")
    ap.add_argument("--db", default=str(store.DEFAULT_DB), help="events database (default: %(default)s)")
    ap.add_argument(
        "--fps", type=float, default=1.0, help="frames per second to process: ~5 live, 1 bulk (default: %(default)s)"
    )
    ap.add_argument(
        "--show",
        action="store_true",
        help="detection window paced to video time, q to stop (try --fps 5); default: headless",
    )
    ap.add_argument("--device", help="detector device: cpu, cuda or mps (default: the detector's choice)")
    ap.add_argument("--start", help="recording start, e.g. 2026-10-09T18:30, for a single file without a dated name")
    ap.add_argument(
        "--min-dwell",
        type=float,
        default=events.MIN_DWELL_S,
        help="seconds in a zone to count a visit, except forbidden zones",
    )
    ap.add_argument(
        "--forbidden-dwell",
        type=float,
        default=events.FORBIDDEN_DWELL_S,
        help="seconds in a forbidden zone to count a visit (default: %(default)s)",
    )
    ap.add_argument(
        "--gap-tolerance", type=float, default=events.GAP_TOLERANCE_S, help="dropout seconds that don't end a visit"
    )
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
    stored = process(
        args.videos,
        args.zones,
        detector,
        store.connect(args.db),
        args.fps,
        args.start,
        args.min_dwell,
        args.gap_tolerance,
        args.forbidden_dwell,
        window=overlay.Window() if args.show else None,
    )
    print(f"stored {len(stored)} visits in {args.db}")


if __name__ == "__main__":
    main()
