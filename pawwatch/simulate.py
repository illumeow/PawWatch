"""Simulated visit history, so the dashboard and anomaly alert have a 7-day baseline. Owner: B.

Every event written from here is stored with simulated=1 and labeled "simulated" wherever it's shown.
Each simulated day also gets simulated camera recordings: around the clock, except on some days one camera is offline
for a few hours (no recording, no visits), so the dashboard shows what an outage looks like.
"""

import random
import sqlite3
from datetime import date, datetime, time, timedelta

from pawwatch import store

CAMERAS = {"food": "cam_food", "water": "cam_water", "litter": "cam_litter", "forbidden": "cam_counter"}

# Typical day for one adult indoor cat: (hour, jitter_h, duration_s range).
MEALS = [(7, 0.5, (90, 240)), (12.5, 1.0, (60, 150)), (18, 0.5, (90, 240)), (22.5, 0.75, (45, 120))]
WATER_PER_DAY = (3, 5)
WATER_HOURS = (6, 24)
WATER_DURATION = (15, 60)
LITTER_PER_DAY = (2, 4)
LITTER_HOURS = (5, 24)
LITTER_DURATION = (40, 150)
FORBIDDEN_PER_DAY = (0, 2)
FORBIDDEN_HOURS = (9, 23)
FORBIDDEN_DURATION = (5, 25)
OUTAGE_EVERY = 3  # days: one camera goes offline on days whose ordinal is a multiple of this
OUTAGE_START_H = (9, 18)
OUTAGE_LENGTH_H = (2, 5)


def _at(day: date, hour: float) -> float:
    return datetime.combine(day, time()).timestamp() + hour * 3600


def simulate_day(day: date, rng: random.Random) -> list[tuple[str, str, float, float]]:
    """One day of visits: [(camera, zone, start_ts, end_ts)], sorted by start."""
    visits = []

    def add(zone, hour, duration):
        hour = min(max(hour, 0.0), 23.99)
        start = _at(day, hour)
        visits.append((CAMERAS[zone], zone, start, start + duration))

    for hour, jitter, dur in MEALS:
        if rng.random() < 0.9:  # skips a meal now and then
            add("food", rng.gauss(hour, jitter), rng.uniform(*dur))
    for zone, per_day, hours, dur in [
        ("water", WATER_PER_DAY, WATER_HOURS, WATER_DURATION),
        ("litter", LITTER_PER_DAY, LITTER_HOURS, LITTER_DURATION),
        ("forbidden", FORBIDDEN_PER_DAY, FORBIDDEN_HOURS, FORBIDDEN_DURATION),
    ]:
        for _ in range(rng.randint(*per_day)):
            add(zone, rng.uniform(*hours), rng.uniform(*dur))
    return sorted(visits, key=lambda v: v[2])


def outage(day: date) -> tuple[str, float, float] | None:
    """(zone, start_ts, end_ts) of the day's camera outage, or None. Seeded by the date, so it doesn't change the
    other simulated visits."""
    if day.toordinal() % OUTAGE_EVERY:
        return None
    rng = random.Random(day.toordinal())
    zone = rng.choice(list(CAMERAS))
    start = rng.uniform(*OUTAGE_START_H)
    return zone, _at(day, start), _at(day, min(start + rng.uniform(*OUTAGE_LENGTH_H), 24.0))


def has_real_events(conn: sqlite3.Connection, day: date) -> bool:
    start = _at(day, 0)
    return any(not ev.simulated for ev in store.events_between(conn, start, start + 86400))


def seed(conn: sqlite3.Connection, days: int, end_day: date, rng: random.Random) -> tuple[int, int]:
    """Write `days` days of simulated history ending with `end_day`. Days that have real events are skipped.

    Returns (days_seeded, events_written).
    """
    seeded = written = 0
    for i in range(days):
        day = end_day - timedelta(days=days - 1 - i)
        if has_real_events(conn, day):
            continue
        off = outage(day)
        for zone, camera in CAMERAS.items():
            spans = [(_at(day, 0), _at(day, 24))]
            if off and off[0] == zone:
                spans = [(_at(day, 0), off[1]), (off[2], _at(day, 24))]
            for a, b in spans:
                store.insert_recording(conn, camera, [zone], a, b, simulated=True)
        for camera, zone, start, end in simulate_day(day, rng):
            if off and zone == off[0] and off[1] <= start < off[2]:
                continue  # the camera was offline: the visit happened, but nobody saw it
            store.insert_event(conn, camera, zone, start, end, simulated=True)
            written += 1
        seeded += 1
    return seeded, written
