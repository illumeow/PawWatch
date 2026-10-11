# Commands

Everything for recording the demo, on a Mac, from the repo root. Clips are in `data/videos/` (shared Drive, not git).
On Linux, drop `--device mps`.

## Detection window, one clip each

Plays at real speed; `q` stops. `data/scratch.db` is a throwaway database, delete it any time.

```bash
uv run python -m pawwatch.run data/videos/TangerineEat.mp4 --zones config/zones/cam_food.json --start 2026-10-10T07:30 --fps 5 --device mps --show --db data/scratch.db
uv run python -m pawwatch.run data/videos/AmiDrink.mp4 --zones config/zones/cam_water.json --start 2026-10-10T08:00 --fps 5 --device mps --show --db data/scratch.db
uv run python -m pawwatch.run data/videos/TangerinePee.mp4 --zones config/zones/cam_litter_box.json --start 2026-10-10T06:15 --fps 5 --device mps --show --db data/scratch.db
uv run python -m pawwatch.run data/videos/TangerineJumpOntoBed.mov --zones config/zones/cam_bed.json --start 2026-10-10T21:40 --fps 5 --device mps --show --db data/scratch.db
```

The bed clip rings the alarm; add `PAWWATCH_MUTE=1` in front to keep it quiet.

## Dashboard: the real day

Tangerine's clips on one day at made-up times, plus a simulated week before it. No alert: one day of clips is normal.

```bash
uv run python scripts/build_demo.py --device mps
PAWWATCH_DB=data/demo.db uv run streamlit run dashboard/app.py
```

## Dashboard: the simulated alert day

A fully simulated day with 8 litter box visits against a usual of about 3, so the alert fires. Label it as simulated
in the video and slides.

```bash
uv run python scripts/seed_fake.py --db data/alert.db --with-today --end 2026-10-10
PAWWATCH_DB=data/alert.db uv run streamlit run dashboard/app.py
```

Pick Sat, Oct 10 in the sidebar. Stop one dashboard (Ctrl+C) before starting another; they share the port.

## Live: feed a clip while the dashboard is open

The dashboard opens on Today with every zone "not on camera", and picks up each visit within 3 s of it ending.
Keep `--show`: it plays at real speed, so visits get real times. Without it a clip finishes in seconds and its visits
land in the future.

```bash
# once: fresh database with a simulated week before today
rm -f data/live.db && uv run python scripts/seed_fake.py --db data/live.db

# terminal 1
PAWWATCH_DB=data/live.db uv run streamlit run dashboard/app.py

# terminal 2, one clip at a time
uv run python -m pawwatch.run data/videos/TangerineEat.mp4 --zones config/zones/cam_food.json --start "$(date +%Y-%m-%dT%H:%M:%S)" --fps 5 --device mps --show --db data/live.db
uv run python -m pawwatch.run data/videos/AmiDrink.mp4 --zones config/zones/cam_water.json --start "$(date +%Y-%m-%dT%H:%M:%S)" --fps 5 --device mps --show --db data/live.db
uv run python -m pawwatch.run data/videos/TangerinePee.mp4 --zones config/zones/cam_litter_box.json --start "$(date +%Y-%m-%dT%H:%M:%S)" --fps 5 --device mps --show --db data/live.db
uv run python -m pawwatch.run data/videos/TangerineJumpOntoBed.mov --zones config/zones/cam_bed.json --start "$(date +%Y-%m-%dT%H:%M:%S)" --fps 5 --device mps --show --db data/live.db
```

The drinking clip is Ami, our other cat; the dashboard is titled Tangerine, so leave it out of a live dashboard shot
or change the cat's name in the sidebar.

## Zones

Opens a frame with the camera's zones drawn. `u` undoes the last point, then the last zone; `1` food, `2` water,
`3` litter, `4` forbidden; click the corners; `n` closes the shape; `s` saves; `q` quits without saving.
Draw each zone tight around the bowl, litter box or furniture: the cat is in the zone its box overlaps most.

```bash
uv run python scripts/draw_zones.py data/videos/TangerineEat.mp4 config/zones/cam_food.json --at 30
uv run python scripts/draw_zones.py data/videos/AmiDrink.mp4 config/zones/cam_water.json --at 40
uv run python scripts/draw_zones.py data/videos/TangerinePee.mp4 config/zones/cam_litter_box.json --at 30
uv run python scripts/draw_zones.py data/videos/TangerineJumpOntoBed.mov config/zones/cam_bed.json --at 7
```

After changing a zone, rerun `build_demo.py` so the real-day dashboard matches.

## Tests, lint, format

```bash
uv run pytest
uv run ruff check            # --fix applies the safe fixes
uv run ruff format           # rewrites files; --check only reports
```

## Ship develop to main

`main` only accepts pull requests:

```bash
gh pr create --base main --head develop --title "Submission update" --body "Latest develop."
gh pr merge develop --merge
```
