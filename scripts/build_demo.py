"""Rebuild the demo database: our real clips on one day, plus 7 simulated days before it. Owner: B.

Run: uv run python scripts/build_demo.py --device mps        # Macs; leave --device off elsewhere
     PAWWATCH_DB=data/demo.db uv run streamlit run dashboard/app.py

The clips were filmed on different days; their start times here are made up but plausible, so the dashboard shows
one real day with every health zone on camera. Only Tangerine's clips go in: the dashboard is hers, and the drinking
clip is of Ami, our other cat, so water shows as "not on camera". The alarm stays muted while building.
"""

import argparse
import os
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from pawwatch import report, run, simulate, store
from pawwatch.detector import make_detector

CLIPS = [  # file in data/videos, zones file, made-up start time on the demo day
    ("TangerinePee.mp4", "config/zones/cam_litter_box.json", "06:15"),
    ("TangerineEat.mp4", "config/zones/cam_food.json", "07:30"),
    ("TangerineJumpOntoBed.mov", "config/zones/cam_bed.json", "21:40"),
]


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--db", default="data/demo.db", help="rebuilt from scratch (default: %(default)s)")
    ap.add_argument(
        "--day",
        type=date.fromisoformat,
        default=date.today() - timedelta(days=1),
        help="the real day (default: yesterday, so the whole day is in the past)",
    )
    ap.add_argument("--videos", default="data/videos")
    ap.add_argument(
        "--fps", type=float, default=5.0, help="same as the --show runs in the video (default: %(default)s)"
    )
    ap.add_argument("--device", help="detector device: cpu, cuda or mps")
    args = ap.parse_args()

    missing = [name for name, _, _ in CLIPS if not (Path(args.videos) / name).exists()]
    if missing:
        raise SystemExit(f"missing in {args.videos}: {', '.join(missing)} (the footage is in the shared Drive)")

    os.environ["PAWWATCH_MUTE"] = "1"
    Path(args.db).unlink(missing_ok=True)
    conn = store.connect(args.db)
    detector = make_detector(device=args.device)
    for name, zones_path, at in CLIPS:
        start = f"{args.day.isoformat()}T{at}"
        run.process([Path(args.videos) / name], zones_path, detector, conn, fps=args.fps, start=start)

    days, written = simulate.seed(conn, 7, args.day - timedelta(days=1), random.Random(42))
    print(f"seeded {days} simulated days ({written} events) before {args.day}")
    print(report.daily_report(conn, args.day, now=datetime.combine(args.day + timedelta(days=1), datetime.min.time())))


if __name__ == "__main__":
    main()
