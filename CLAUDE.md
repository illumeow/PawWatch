# PawWatch

Edge-AI cat health monitor for the **2026 ASUS UGen AI League** hackathon (Lightning track).
Fixed cameras watch food bowl, water bowl, litter box and "no-go" zones; YOLO detects the cat; an event engine
logs eat / drink / litter visits to SQLite, flags anomalies vs the 7-day average, sounds an alarm on no-go zones,
and writes a daily report. Video never leaves the box: only events are stored.

Source docs (zh-TW, authoritative): `docs/ProductDescription.md` (what/why), `docs/Worklist.md` (tasks, schedule, deliverables).

## Deadline and scope

- **Submit by 2026-10-14**: registration, English slides (~12 pages, max 20), English demo video (≤3 min, unlisted YouTube), **public GitHub repo with README**.
- Goal: smallest demoable MVP; effort goes into slides and video. Don't build what the demo doesn't show.
- **No UGen300 hardware yet** (shipped only to finalists). MVP runs on a laptop with Ultralytics; UGen300 is a documented deployment target with a ready backend swap.
- Demo input = **pre-recorded video files** of our own cat, one fixed camera per zone. Do not depend on a live webcam.
- Business model is 35% of judging. Code quality matters less than a clean, believable demo.

## MVP features (Worklist §1)

1. **Detection**: Ultralytics `yolov8n.pt` (COCO, no training). Keep class 15 = `cat` only.
2. **Zones**: one `zones.json` per camera, polygon coords per zone (`food`, `water`, `litter`, `forbidden`). Cat is "in" a zone when its bbox **center** is inside the polygon. Process multiple video files/streams at once; every event carries a `camera` id.
3. **Events**: cat stays in a zone > N seconds → one visit. Debounce so a flickering box doesn't double-count (tolerate short dropouts before closing a visit).
4. **Storage**: SQLite, events only (`camera`, `zone`, `start`, `end`/`duration`). Never store frames. This is the privacy pitch.
5. **Forbidden-zone alarm**: play a sound + draw red box on screen. Telegram notify is optional.
6. **Anomaly alert**: today's count per zone vs 7-day mean; flag large deviations (e.g. litter visits 2x normal). Past 7 days may be **seeded fake data, labeled "simulated"** in slides/UI. Wording: "watch / see a vet", never a diagnosis.
7. **Daily report**: template string is enough (e.g. "Mochi drank 6 times today, 2 more than usual"). Optional: small local LLM via Ollama (Qwen ~1.5B).
8. **Dashboard**: Streamlit, one page: today's counts, timeline, 7-day trend, daily report.
9. **README**: features, architecture diagram, how to run, how to deploy on UGen300 (Hailo-10H).

Known limit: can't tell multiple cats apart (future work, same tech as street-cat TNR ear-tip tracking).

## Architecture

```
fixed cams (RTSP / video files) ─▶ host ─▶ detector (YOLO cat) ─▶ zone + dwell event engine ─▶ SQLite (events only)
                                     │                                                            │
                                 UGen300 later                                     Streamlit dashboard · daily report · alerts
```

Keep these as separate modules so the pure logic is testable without a model or video:
- **detector**: one interface, `infer(frame_bgr) -> list[(label, score, (x1, y1, x2, y2))]` in original-image pixels. Same contract as `ObjectDetector` in the UGen300 demos, so the Hailo backend drops in.
- **zones / events**: pure functions over detections + timestamps. Use the video's own timestamps (frame index / fps), not wall clock, so recorded footage replays correctly.
- **store**: SQLite access only.
- **report / anomaly**: read from store, no CV imports.
- **dashboard**: Streamlit, reads from store.

Stack: Python 3.10 (matches HailoRT), OpenCV, numpy, Ultralytics, SQLite (stdlib), Streamlit. No cloud services.

## UGen300 deployment target

UGen300 = ASUS accelerator, Hailo-10H, 40 TOPS, 8 GB, USB or M.2. It's a card plugged into a host, not a standalone computer.
Reference code: https://github.com/erp0917-stack/ugen300-demos (Windows 11, Python 3.10, HailoRT 5.3.x). Patterns worth copying for a `hailo` backend:

- `HeadCount/hailo_detect.py`: `ObjectDetector(hef)`, InferModel API, `yolov8m.hef`/`yolov8s.hef` with built-in NMS; returns the same `(label, score, box)` tuples. COCO index 15 = `cat` there too.
- `*/hailo_vdevice.py`: **one VDevice per process**, keep every HailoRT object alive (`keep()`), exit with `os._exit` (`exit_now()`). On Windows, releasing/destructing HailoRT objects over USB can drop the device (`LIBUSB_ERROR_IO`) until replugged.
- `Traffic/tracker.py`: simple IoU/centroid tracker if per-cat track IDs are needed.
- `OfflineChat/llm_engine.py`: on-device LLM via `hailo_platform.genai.LLM` (e.g. `Qwen2.5-1.5B-Instruct.hef`), a path for an on-device daily report.
- Models: `.hef` files from the Hailo Model Zoo (hailo10h target), not in git.

Select backend by flag/env (e.g. `--backend ultralytics|hailo`); never import `hailo_platform` unless the hailo backend is chosen.

## Conventions

- Never commit video footage, `.pt`/`.hef` model weights, or SQLite DBs. Keep them in gitignored folders.
- User-facing deliverables (README, UI strings, slides, video) are **English**. Planning docs in `docs/` are zh-TW.
- Privacy is the product: no code path should save or upload frames (debug snapshots off by default and gitignored).
- Prefer small, readable scripts over frameworks. Hackathon prototype: no premature abstraction beyond the detector backend seam.
