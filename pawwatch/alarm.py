"""Forbidden-zone alarm: the run loop calls trigger() for every frame with the cat in a no-go zone.

The detection window draws the red box itself; this module only handles sound and notifications.

Environment (all optional):
    PAWWATCH_MUTE=1                    no sound (e.g. bulk runs over long recordings)
    PAWWATCH_ALARM_SOUND=path          custom sound file instead of the system alert
    LINE / Discord variables           also send a text message; see pawwatch.notify
"""

import os
import platform
import shutil
import subprocess
import threading
import time
from datetime import datetime

from pawwatch import notify

COOLDOWN_S = 30.0  # per camera and zone, in video time: one alarm per jump, not per frame
MIN_WALL_GAP_S = 2.0  # never overlap sounds, even when footage is processed faster than real time

_last_video = {}
_last_wall = 0.0


def trigger(camera: str, zone: str, ts: float) -> None:
    """Cat just entered a forbidden zone. Plays a sound; optionally texts the owner (LINE, Discord). Returns fast."""
    global _last_wall
    key = (camera, zone)
    if ts - _last_video.get(key, float("-inf")) < COOLDOWN_S:
        return
    _last_video[key] = ts
    when = datetime.fromtimestamp(ts).strftime("%H:%M")
    print(f"[alarm] cat entered {zone} on {camera} at {when}", flush=True)

    now = time.monotonic()
    if os.environ.get("PAWWATCH_MUTE") != "1" and now - _last_wall >= MIN_WALL_GAP_S:
        _last_wall = now
        _play_sound()
    if notify.channels():
        text = f"PawWatch: your cat jumped onto a no-go spot ({camera}) at {when}."
        threading.Thread(target=notify.send, args=(text,), daemon=True).start()


def _play_sound():
    """Start the alert sound and return immediately."""
    custom = os.environ.get("PAWWATCH_ALARM_SOUND")
    system = platform.system()
    try:
        if system == "Darwin":  # development laptops
            subprocess.Popen(["afplay", custom or "/System/Library/Sounds/Sosumi.aiff"])
        else:  # Linux: PulseAudio's paplay, or PipeWire's pw-play (Fedora)
            player = shutil.which("paplay") or shutil.which("pw-play")
            if not player:
                raise FileNotFoundError("no paplay or pw-play")
            subprocess.Popen([player, custom or "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"])
    except Exception as e:  # noqa: BLE001 — a missing player must never stop the pipeline
        print(f"[alarm] sound failed ({e}); ringing the terminal bell", flush=True)
        print("\a", end="", flush=True)
