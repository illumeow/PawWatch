"""Simulated visit history, so the dashboard and anomaly alert have a 7-day baseline. Owner: B.

Every event written from here is stored with simulated=1 and labeled "simulated" wherever it's shown.
"""
from datetime import datetime, time, timedelta

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


def _at(day, hour):
    return datetime.combine(day, time()).timestamp() + hour * 3600


def simulate_day(day, rng):
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


def has_real_events(conn, day):
    start = _at(day, 0)
    return any(not ev.simulated for ev in store.events_between(conn, start, start + 86400))


def seed(conn, days, end_day, rng):
    """Write `days` days of simulated history ending with `end_day`. Days that have real events are skipped.

    Returns (days_seeded, events_written).
    """
    seeded = written = 0
    for i in range(days):
        day = end_day - timedelta(days=days - 1 - i)
        if has_real_events(conn, day):
            continue
        for camera, zone, start, end in simulate_day(day, rng):
            store.insert_event(conn, camera, zone, start, end, simulated=True)
            written += 1
        seeded += 1
    return seeded, written
