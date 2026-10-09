"""Forbidden-zone alarm. SHARED CONTRACT: A calls trigger(), B implements it.

A also draws the red box in its own detection window; this module only handles sound and notifications.

Environment (all optional):
    PAWWATCH_MUTE=1                    no sound (e.g. bulk runs over long recordings)
    PAWWATCH_ALARM_SOUND=path          custom sound file instead of the system alert
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID   also send a text message; nothing is sent unless both are set
"""
import json
import os
import platform
import subprocess
import threading
import time
import urllib.request
from datetime import datetime

COOLDOWN_S = 30.0  # per camera and zone, in video time: one alarm per jump, not per frame
MIN_WALL_GAP_S = 2.0  # never overlap sounds, even when footage is processed faster than real time

_last_video = {}
_last_wall = 0.0


def trigger(camera: str, zone: str, ts: float) -> None:
    """Cat just entered a forbidden zone. Plays a sound; optionally sends a Telegram message. Must return fast."""
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
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        text = f"PawWatch: your cat jumped onto a no-go spot ({camera}) at {when}."
        threading.Thread(target=_send_telegram, args=(token, chat, text), daemon=True).start()


def _play_sound():
    """Start the alert sound and return immediately."""
    custom = os.environ.get("PAWWATCH_ALARM_SOUND")
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["afplay", custom or "/System/Library/Sounds/Sosumi.aiff"])
        elif system == "Windows":
            import winsound

            if custom:
                winsound.PlaySound(custom, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
        else:
            subprocess.Popen(["paplay", custom or "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"])
    except Exception as e:  # noqa: BLE001 — a missing player must never stop the pipeline
        print(f"[alarm] sound failed ({e}); ringing the terminal bell", flush=True)
        print("\a", end="", flush=True)


def _send_telegram(token, chat_id, text):
    """Text only: never frames."""
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat_id, "text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10).close()
    except Exception as e:  # noqa: BLE001
        print(f"[alarm] Telegram failed: {e}", flush=True)
