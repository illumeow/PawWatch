# PawWatch

Edge-AI cat health monitor for the **2026 ASUS UGen AI League** hackathon.
Fixed cameras watch the cat's food, water, litter and no-go zones; YOLO detects the cat; an event engine logs visits,
flags changes from the cat's normal pattern, alarms on no-go zones and writes a daily report.
Video never leaves the box: only events are stored.

Product, plan, work split and hardware notes live in `docs/`. Read the relevant doc before starting a task.
Current status and each person's next steps: the top section of `docs/TeamPlan.md`.

## Constraints

- Hackathon prototype with a hard deadline: build the smallest thing the demo shows; effort goes into slides and video.
- Runs on a laptop now; the ASUS UGen300 (Hailo-10H) accelerator is the deployment target. Keep the detector swappable.
- Supported platforms: Linux (deployment host) and macOS (development laptops). Windows is not supported.
- Demo runs on pre-recorded video, not a live camera.
- Three people work in parallel: two code halves and the slides. Respect file ownership and shared contracts described
  in `docs/`; changing a shared contract needs a heads-up to the others.

## Architecture principles

- Pipeline: cameras → detector → zone and dwell event logic → SQLite (events only) → dashboard, report, alerts.
- The SQLite events table is the seam between halves; downstream code reads only through the store module.
- The detector is one interface returning `(label, score, (x1, y1, x2, y2))` in original-image pixels, so backends swap.
  Never import `hailo_platform` unless the Hailo backend is selected.
- Event logic is pure (detections + timestamps in, events out) and testable without a model or video.
  Use video time, not wall clock, so recorded footage replays correctly.
- Python 3.10–3.13 supported (HailoRT's range); develop on 3.12. No cloud services.
- Managed with uv: `uv sync` to set up, `uv run` to execute, `uv add` / `uv remove` for dependencies. No bare `pip`.

## Conventions

- Privacy is the product: no code path saves or uploads frames.
- Never commit footage, model weights or databases.
- Everything in the repo is English.
- Docs are local Markdown in `docs/`, committed, so both teammates and their Claude sessions see them.
  Don't use Claude Docs or artifacts for project docs unless asked.
- Anomaly wording suggests watching or seeing a vet; never a diagnosis. Simulated data is always labeled as such.
- Prefer small, readable scripts over frameworks.
