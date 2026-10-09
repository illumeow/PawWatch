# Demo video

Under 3 minutes, English, uploaded to YouTube as unlisted. Owner: @illumeow (edit and voice-over).
Narration is TTS; total speech is about 2 minutes, which leaves room for the alarm sound and for shots to breathe.

## Shot list

| Time | Shot | Source | Narration |
| --- | --- | --- | --- |
| 0:00–0:18 | Tangerine eating, raw footage | `TangerineEat.mp4` (Drive) | 1 |
| 0:18–0:35 | Problem and existing products | Slides 2–3 (C) | 2 |
| 0:35–1:00 | Detection window on the eat clip (box, food zone, count goes 0 → 1), then quick cuts of the drinking and litter box clips | Screen recordings, `run.py --show` (A) | 3a |
| 1:00–1:12 | Detection window on the bed clip, red box, **alarm sound audible** | Screen recording (A) | 3b |
| 1:12–1:20 | Turning on airplane mode while the pipeline keeps running | Phone or screen recording (A) | 3c |
| 1:20–1:45 | Dashboard on the simulated alert day: alert, tiles, timeline, past week; open "What PawWatch stores" | Screen recording (B) | 3d |
| 1:45–1:52 | Zoom on the daily report box | Same recording (B) | 3e |
| 1:52–2:35 | Architecture diagram, then the "fits the chip" numbers | Slides (C) | 4 |
| 2:35–2:50 | Future work, then logo and repo link | Slides (C) | 5 |

On screen at all times during the live part: the detection window's caption
("Running on laptop · YOLOv8n · target: ASUS UGen300"), and "simulated data" on the dashboard shots.

## Narration

Spellings like "U Gen 300" are for the TTS voice; captions use the normal spelling.

**1 (13 s).** This is Tangerine. If she started drinking twice as much water, or visiting the litter box three times as
often, would you notice? Changes like these are often the first sign that a cat is unwell, and cats are very good at
hiding them.

**2 (13 s).** Most of us are out all day, so we miss them. Pet cameras could watch, but they stream video of our homes
to the cloud and charge a monthly fee. Smart litter boxes see only one part of the picture. So we built PawWatch.

**3a (16 s).** Fixed cameras point at the food bowl, the water bowl and the litter box. An off-the-shelf YOLO model finds
the cat in each frame. When Tangerine stays in the food zone long enough, PawWatch logs one visit: when it started, and
how long it lasted. The frame itself is thrown away.

**3b (7 s).** Some spots are off-limits. The moment she jumps onto the bed, PawWatch sounds an alarm, and it can text
your phone.

**3c (4 s).** Everything runs at home. We switch off the internet, and it keeps working.

**3d (20 s).** Each visit becomes one row in a local database. No images, no video. The dashboard compares today with
Tangerine's usual week. In this simulated example, she used the litter box eight times, almost three times her usual,
so PawWatch suggests keeping an eye on her, and considering a vet visit. It never diagnoses.

**3e (4 s).** Every day ends with a short report in plain English, ready to show your vet.

**4 (31 s).** Today, the prototype runs on a laptop. The target is a small Linux box with the ASUS U Gen 300
accelerator. Our detector returns the same boxes as ASUS's own U Gen 300 demos, and Hailo publishes YOLO v8 precompiled
for the Hailo 10 H, so moving over means swapping one module. Three cameras at five frames per second need fifteen
detections per second, well within the chip's published speed. On the edge, video stays private, there's no monthly
fee, and it works offline.

**5 (9 s).** Next, we want to tell several cats apart, and help track street cats. PawWatch: know your cat's routine,
without sending your home to the cloud.

Check before recording:

- "Well within the chip's published speed" stays only once C has the cited Hailo number for YOLOv8 on Hailo-10H;
  otherwise cut that clause.
- 3d matches the dashboard from `seed_fake.py --with-today` (8 litter box visits, usual about 3). If the alert day
  changes, change the numbers here.

## Voice-over

macOS, one file per section so each lines up with its shot:

```bash
say -v Samantha -r 165 -f 1.txt -o 1.aiff   # repeat per section; durations above are from this voice and rate
```

## Dashboard recording

The alert day must be a full past day, or "today" before any simulated visit has happened looks empty:

```bash
uv run python scripts/seed_fake.py --db data/video.db --with-today --end <yesterday>
PAWWATCH_DB=data/video.db uv run streamlit run dashboard/app.py
```

Pick yesterday in the sidebar, collapse the sidebar, and record the browser window.
