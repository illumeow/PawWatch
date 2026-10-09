"""Forbidden-zone alarm. SHARED CONTRACT: A calls trigger(), B implements it.

A also draws the red box in its own detection window; this module only handles sound and notifications.
"""


def trigger(camera: str, zone: str, ts: float) -> None:
    """Cat just entered a forbidden zone. Plays a sound; optionally sends a Telegram message. Must return fast."""
    # TODO(B): play sound (non-blocking), optional Telegram notification.
    print(f"[alarm] cat entered {zone} on {camera} at {ts:.1f}", flush=True)
