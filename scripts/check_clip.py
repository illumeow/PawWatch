"""1-minute camera test: how often is the cat detected in this clip? Owner: A.

Run: uv run python scripts/check_clip.py data/videos/test_food.mp4
Prints the detection rate and saves a few annotated frames to data/check/ (gitignored) to eyeball.
If the cat is missed often, move the camera or add light before the long recording.
"""
import argparse
from pathlib import Path

import cv2

from pawwatch.detector import make_detector


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("clip")
    ap.add_argument("--every", type=int, default=5, help="check every Nth frame")
    ap.add_argument("--conf", type=float, default=0.4)
    ap.add_argument("--out", default="data/check")
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.clip)
    if not cap.isOpened():
        raise SystemExit(f"cannot open {args.clip}")
    det = make_detector(conf=args.conf)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(args.clip).stem

    checked = hits = saved_hit = saved_miss = 0
    scores = []
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % args.every == 0:
            cats = det.infer(frame)
            checked += 1
            if cats:
                hits += 1
                scores.append(max(s for _, s, _ in cats))
            for _, score, (x1, y1, x2, y2) in cats:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 0), 3)
                cv2.putText(frame, f"cat {score:.2f}", (x1, max(y1 - 8, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 0), 2)
            if cats and saved_hit < 3:
                cv2.imwrite(str(out / f"{stem}_hit{saved_hit}.jpg"), frame)
                saved_hit += 1
            elif not cats and saved_miss < 2:
                cv2.imwrite(str(out / f"{stem}_miss{saved_miss}.jpg"), frame)
                saved_miss += 1
        idx += 1
    cap.release()

    if not checked:
        raise SystemExit("no frames read")
    rate = hits / checked
    mean = sum(scores) / len(scores) if scores else 0.0
    print(f"{stem}: cat in {hits}/{checked} checked frames ({rate:.0%}), mean confidence {mean:.2f}")
    print(f"sample frames in {out}/")
    if rate < 0.5:
        print("Low rate. If the cat was in frame most of the clip, move the camera closer, change the angle or add light.")


if __name__ == "__main__":
    main()
