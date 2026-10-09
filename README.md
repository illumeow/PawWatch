# PawWatch

Edge-AI cat health monitor: fixed cameras log how often the cat eats, drinks and uses the litter box,
and alarm when it jumps onto a forbidden zone. Only events are stored, never video.

Built for the 2026 ASUS UGen AI League. See [docs/](docs/) for the product description and team plan.

## Setup

Requires [uv](https://docs.astral.sh/uv/). It installs Python 3.10 and all dependencies:

```bash
uv sync
```

## Run

```bash
# 1-minute camera test: how often is the cat detected?
uv run python scripts/check_clip.py data/videos/test_food.mp4

# Tests
uv run pytest

# Dashboard
uv run streamlit run dashboard/app.py
```

Footage goes in `data/videos/` (gitignored).
