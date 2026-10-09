# PawWatch team plan

2026-10-09

Three people deliver PawWatch by 2026-10-14. Two build the code in parallel, split at one seam: the SQLite events table.
Half A (vision) writes events from real cat video; half B (output) reads them into the dashboard, anomaly alerts and daily report.
C owns the slides, research and the architecture diagram.

## Status and next steps (updated 2026-10-09)

We're finishing in **3 days (Fri 10/9 to Sun 10/11)**, with 10/12 to 10/14 as buffer. See Schedule below.

**Half B is done and merged into `develop`** ([PR #1](https://github.com/illumeow/PawWatch/pull/1)): the simulated 7-day history,
anomaly alert, daily report, alarm sound and Streamlit dashboard. To see it:

```bash
uv sync
uv run python scripts/seed_fake.py --with-today
uv run streamlit run dashboard/app.py
```

**@meander (A):**
- Read PR #1's description: it touched two shared contracts. `store.delete_simulated()` is new (additive, table unchanged), and
  `alarm.trigger(camera, zone, ts)` is implemented with a 30 s cooldown per camera, so call it on every frame the cat
  is in a forbidden zone. Set `PAWWATCH_MUTE=1` for bulk runs.
- Day 1: cameras up, 1-minute test (`uv run python scripts/check_clip.py <clip>`), record overnight, stage a counter jump.
- Day 2: zones files, visit logic, `run.py` writing real events by the evening. Use the GPU if there is one
  (`device="cuda"`; `"mps"` on Macs) and 1 frame per second for the overnight footage.
- Day 3 morning: screen captures of detection and the airplane-mode shot.
- Check the alarm sound on Fedora once:
  `uv run python -c "import time; from pawwatch import alarm; alarm.trigger('cam_counter','forbidden',time.time()); time.sleep(1)"`

**@bbwinner (C):**
- Day 1: research, slide outline, business model page (35% of the score).
- Day 2: slide text, architecture diagram, Hailo's published YOLOv8 speed on Hailo-10H (cite the source).
  B sends dashboard screenshots and the repo link on Day 2 evening.
- Day 3: finish slides, add the demo video link, submit.

**@illumeow (B):** README, dashboard on real events, screenshots to C, then the demo video on Day 3.

**Cut for time:** Hailo backend port, Telegram setup, LLM-written daily report, a second day of recording.

**Open:** who does registration? Check its deadline on the competition page.

## Roles

meander lives with the cat and takes A; illumeow takes B; bbwinner takes C. A needs a tight loop with the cameras
(move, re-shoot, retune in minutes) and knows which bowl is which; B can work from simulated data until real events arrive;
C needs no code and can start research today.

| Role | Owner | Builds | Works from |
| --- | --- | --- | --- |
| A: vision | @meander | Detection, zones, visit events, SQLite writes, red box on forbidden zone, `run.py` CLI | Real video footage |
| B: output | @illumeow | Seed script, alarm (sound, optional Telegram), anomaly alert, daily report, Streamlit dashboard, README, demo video edit | Simulated events, then A's real events |
| C: slides | @bbwinner | English slides (~12 pages), market and vet research, architecture diagram, references | Product docs, then screenshots and clips from A and B |

The forbidden-zone alarm is split: A draws the red box in the detection window and calls `alarm.trigger(...)` when the cat enters a forbidden zone; B implements what the trigger does.

Handoffs to C:

| What | From | By |
| --- | --- | --- |
| Detection screenshots (boxes, zones, alarm) | A | Sat 10/10 evening |
| Dashboard and daily report screenshots | B | Sat 10/10 evening |
| Public GitHub repo link | B | Sat 10/10 evening |
| Architecture diagram, for README and video | C to B | Sat 10/10 evening |

## Interface contract

Two things cross the A/B line, so we fix both on day 1. Changing either needs a heads-up to the other person.

1. The events table in `pawwatch/store.py`, for finished visits.
2. The live alarm hook in `pawwatch/alarm.py`, for the moment the cat enters a forbidden zone. It can't go through SQLite, because a visit is written only after it ends.

```sql
CREATE TABLE events (
  id         INTEGER PRIMARY KEY,
  camera     TEXT NOT NULL,     -- e.g. cam_food
  zone       TEXT NOT NULL,     -- food | water | litter | forbidden
  start_ts   REAL NOT NULL,     -- unix seconds, from video time, not wall clock
  end_ts     REAL NOT NULL,
  duration_s REAL NOT NULL,
  simulated  INTEGER NOT NULL DEFAULT 0  -- 1 = seeded fake history
);
```

`store.py` exposes plain functions: `insert_event(...)`, `events_between(start, end)`, `daily_counts(days)`. B reads only through these.

```python
# pawwatch/alarm.py (owned by B, called by A)
def trigger(camera: str, zone: str, ts: float) -> None:
    """Cat just entered a forbidden zone. Plays a sound; optionally sends a Telegram message. Must return fast."""
```

Two contracts stay inside half A but are written down so the UGen300 port is a drop-in:

- Detector output: `infer(frame_bgr) -> list[(label, score, (x1, y1, x2, y2))]` in original-image pixels,
  the same as `ObjectDetector` in the [ugen300-demos](https://github.com/erp0917-stack/ugen300-demos) repo.
- Zones file, one per camera: `{"camera": "cam_food", "zones": [{"name": "food", "polygon": [[x, y], ...]}]}`.

## Repo layout

Each file has one owner; nobody edits the other half's files without asking.

| Path | Owner | Purpose |
| --- | --- | --- |
| `pawwatch/store.py` | Shared | Events table and query functions |
| `pawwatch/detector.py` | A | YOLO cat detection, Ultralytics now, Hailo later |
| `pawwatch/zones.py` | A | Load zones file, point-in-polygon |
| `pawwatch/events.py` | A | Detections over time to visits, with debounce (pure logic, tested) |
| `pawwatch/alarm.py` | Shared interface, B implements | `trigger()`: sound and optional Telegram; A calls it |
| `pawwatch/run.py` | A | CLI: videos + zones to events in SQLite |
| `config/zones/*.json` | A | One zones file per camera |
| `scripts/check_clip.py` | A | 1-minute test: cat detection rate on a clip |
| `scripts/seed_fake.py` | B | 7 days of simulated events |
| `pawwatch/anomaly.py` | B | Today vs 7-day mean |
| `pawwatch/report.py` | B | Daily report text |
| `dashboard/app.py` | B | Streamlit page |
| `README.md` | B | Features, architecture, run steps, UGen300 notes |
| `tests/` | Each own | Tests for their own modules |

Gitignored: `data/videos/`, `*.pt`, `*.hef`, `*.db`. Footage lives in a shared Google Drive folder.

## Data strategy

The demo shows real today plus simulated history: anomaly alerts need 7 days of baseline,
and we will have about one day of footage.

| Data | Written by | Proves or enables | Shown in demo |
| --- | --- | --- | --- |
| Real video | Filmed by A | Model and event logic work | Detection window: boxes, zones, count ticking up, counter alarm |
| Real events (`simulated=0`) | `run.py` | Today's numbers are genuine | Today's counts, timeline, daily report |
| Simulated history (`simulated=1`) | `seed_fake.py` | B can build before A is done; anomaly has a baseline | 7-day trend, "2x more litter visits than usual" alert |

- Label simulated history as "simulated" in the dashboard (B) and slides (C).
- To make the alert fire on camera, seed a baseline that today's real count clearly exceeds (e.g. 3 litter visits a day vs 6 today).
- Days of real recording replace their simulated days, so the trend becomes partly real.

## Demo plan

Everything runs on a laptop: the UGen300 ships only to finalists, so the demo shows the real pipeline on a laptop
and argues that the UGen300 port is low-risk. Never present laptop footage as running on UGen300.

| What | Owner | Why |
| --- | --- | --- |
| Recorded footage through the real pipeline: boxes, zones, counts ticking up, alarm, then dashboard and report | A, B | Proves it works |
| Caption on the detection window: "Running on laptop · YOLOv8n · target: ASUS UGen300" | A | Honest about hardware |
| Frame-rate limit per camera (`run.py --fps`, about 5 live, 1 for bulk runs) | A | Edge-sized load; makes bulk processing feasible |
| Airplane mode on camera while the pipeline keeps running | A records, B edits | Shows "no cloud" |
| Database rows with no images, empty frames folder | B | Shows "events only" |
| Architecture slide: laptop backend today, Hailo backend after; same `(label, score, box)` contract as ASUS's UGen300 demos | C | Port is a swap, not a rewrite |
| Stock COCO YOLOv8: Hailo publishes precompiled versions for Hailo-10H, so no training or model conversion | C | No model risk |
| Load fits the chip: 3 cameras × 5 fps = 15 inferences/s vs Hailo's published YOLOv8 speed on Hailo-10H (look up and cite) | C | Hardware is sufficient |

Video: the 0:50–2:10 live section adds the airplane-mode shot and the caption; the "fits the chip" numbers go in 2:10–2:45.

### Compute

YOLOv8n on a 1280×720 frame, measured on an M3 Pro laptop (2026-10-09):

| Device | Model input size | ms / frame | fps |
| --- | --- | --- | --- |
| CPU | 640 | 20.5 | 49 |
| CPU | 416 | 10.8 | 93 |
| Apple GPU (`device="mps"`) | 640 | 5.9 | 169 |
| Apple GPU (`device="mps"`) | 416 | 5.1 | 195 |

- Live demo needs about 15 fps in total: fine even on CPU.
- Bulk runs are the cost: 2 days × 3 cameras is 144 camera-hours. At 1 fps that's about 3 h on CPU or under 1 h on the Apple GPU; at 5 fps, about 14 h on CPU.
- Ultralytics picks CUDA automatically but not Apple's GPU; pass `device="mps"` on Macs.
- Time a clip on the machine that will process the footage first; a laptop without a GPU may be 2–3× slower.

## Recording guide

Start recording today: every later step needs footage, and lost recording days can't be made up.

Setup and settings:

- One device per zone (food, water, litter); with two devices, put the bowls side by side and split them with two zones.
- Fix the camera with a tripod, clamp or tape; it must not move, because zones are pixel coordinates.
- About 1 to 2 m away, slightly above, side view; the cat should fill a good part of the frame.
- Keep a small lamp on at night; dark phone footage loses detections.
- 720p at 15 fps (less to decode later), real time (no time-lapse), 1-hour segments if the app allows.
- Name files with the start time, e.g. `food_2026-10-09T1830.mp4`.
- Devices plugged in; auto-lock and battery saver off.

Checklist:

- [ ] Record 1 minute per spot with the cat in frame
- [ ] Run `check_clip.py` on each clip; move the camera if the cat is missed
- [ ] Long recording, all zones at once, overnight (one night is enough)
- [ ] Staged clips: cat jumping on counter or table (forbidden zone)
- [ ] Close-up shots of eating and drinking for the demo video
- [ ] Upload clips to the shared Drive folder as they finish

## Git workflow

Keep it light: one feature branch each, small PRs into `develop`, merged at least once a day.

1. `main` = what we submit; `develop` = shared integration branch.
2. Skeleton commit lands on `develop` first (stubs, `store.py` schema, `.gitignore`, sample zones file).
3. Each person branches off it: `feat/vision` (A), `feat/dashboard` (B).
4. Small PRs into `develop`, at least daily; pull `develop` into your branch before each PR.
5. Don't edit the other half's files; `store.py` changes need a heads-up first.
6. `develop` merges to `main` on Sun 10/11 before the final recording, and again if fixes land before 10/14.

`CLAUDE.md` is in the repo, so everyone's Claude sessions follow the same contract.

## Schedule

Three working days; real events reach the dashboard on Day 2 evening, everything on Day 3 is recording and submission.

| Day | A: vision (@meander) | B: output (@illumeow) | C: slides (@bbwinner) |
| --- | --- | --- | --- |
| Fri 10/9 | Cameras up, 1-minute test, record overnight, stage a counter jump | Half B done and merged (PR #1); README | Research, slide outline, business model page |
| Sat 10/10 | Zones, visit logic, `run.py`; first real events by evening; send screenshots | Dashboard on real events; send screenshots and repo link | Slide text, architecture diagram, Hailo speed number |
| Sun 10/11 | Morning: screen captures, airplane-mode shot | Edit demo video, TTS voice-over, upload unlisted to YouTube | Finish slides, add video link, submit |
| 10/12–10/14 | Buffer | Buffer: check every link in slides and README | Buffer |
