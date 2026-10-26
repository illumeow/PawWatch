#!/usr/bin/env bash
# One-take demo video helper (docs/DemoVideo.md): Enter plays the next detection clip, so nothing is typed on camera.
# Clips write to data/live.db at the current time, so the dashboard open on it shows them as they happen.
# macOS. Run from the terminal window the video shows; set DISCORD_WEBHOOK_URL first so the alarm texts.
set -euo pipefail
cd "$(dirname "$0")/.."

# A retake starts clean: drop the last take's real visits, keep the simulated week.
sqlite3 data/live.db "DELETE FROM events WHERE simulated = 0; DELETE FROM recordings WHERE simulated = 0;"

clip() {
    uv run python -m pawwatch.run "data/videos/$1" --zones "config/zones/$2.json" --start "$(date +%Y-%m-%dT%H:%M:%S)" \
        --fps 5 --device mps --show --db data/live.db >/dev/null
}

clear
read -rp "PawWatch · Enter: food bowl camera " _
clear
clip TangerineEat.mp4 cam_food
clear
read -rp "PawWatch · Enter: bed camera " _
clear
clip TangerineJumpOntoBed.mov cam_bed
clear
