#!/usr/bin/env bash
# One-take demo video helper (docs/DemoVideo.md): Enter plays the next detection clip, so nothing is typed on camera.
# macOS. Run from the terminal window the video shows; set DISCORD_WEBHOOK_URL first so the alarm texts.
set -euo pipefail
cd "$(dirname "$0")/.."

clip() {
    uv run python -m pawwatch.run "data/videos/$1" --zones "config/zones/$2.json" --start "$3" \
        --fps 5 --device mps --show --db data/scratch.db >/dev/null
}

clear
read -rp "PawWatch · Enter: food bowl camera " _
clear
clip TangerineEat.mp4 cam_food 2026-10-10T07:30
clear
read -rp "PawWatch · Enter: bed camera " _
clear
clip TangerineJumpOntoBed.mov cam_bed 2026-10-10T21:40
clear
