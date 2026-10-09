"""Today vs the cat's usual pattern. Owner: B. Reads only through store.

"Usual" = the average over the previous 7 days, counted up to the same time of day, so a normal morning
isn't flagged for missing the evening meal. Days with no events at all (cameras off) are left out of the baseline.
Wording is up to the caller; it must suggest watching or seeing a vet, never a diagnosis.
"""
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from pawwatch import store

HEALTH_ZONES = ("food", "water", "litter")  # forbidden-zone jumps are alarms, not health signals
WINDOW_DAYS = 7
HIGH_RATIO = 2.0  # at least twice the usual...
LOW_RATIO = 0.5  # ...or at most half of it
MIN_GAP = 3  # and at least this many visits apart, so 1 vs 0 isn't an alert


@dataclass(frozen=True)
class Anomaly:
    zone: str
    count: int
    expected: float
    direction: str  # "high" | "low"
    partial_day: bool  # True while the day is still in progress


def _day_start(day):
    return datetime.combine(day, time()).timestamp()


def _cutoff(day, now):
    """Seconds into `day` that count as "so far": the whole day once it's over."""
    elapsed = (now or datetime.now()).timestamp() - _day_start(day)
    return min(max(elapsed, 0.0), 86400.0)


def counts_until(conn, day, seconds):
    """Visits per zone on `day` that started within its first `seconds`."""
    counts = dict.fromkeys(store.ZONES, 0)
    start = _day_start(day)
    for ev in store.events_between(conn, start, start + seconds):
        counts[ev.zone] += 1
    return counts


def expected_counts(conn, day, now=None, window=WINDOW_DAYS):
    """Average visits per zone over the previous `window` days, up to the same time of day.

    Returns ({zone: mean}, days_used); ({}, 0) when there's no history.
    """
    cutoff = _cutoff(day, now)
    totals = dict.fromkeys(store.ZONES, 0)
    used = 0
    for i in range(1, window + 1):
        prev = day - timedelta(days=i)
        if not any(counts_until(conn, prev, 86400).values()):
            continue  # cameras off that day
        used += 1
        for zone, n in counts_until(conn, prev, cutoff).items():
            totals[zone] += n
    if not used:
        return {}, 0
    return {zone: n / used for zone, n in totals.items()}, used


def find_anomalies(conn, day=None, now=None):
    """Health zones whose count so far on `day` differs a lot from the usual."""
    now = now or datetime.now()
    day = day or now.date()
    expected, used = expected_counts(conn, day, now)
    if not used:
        return []
    cutoff = _cutoff(day, now)
    counts = counts_until(conn, day, cutoff)
    found = []
    for zone in HEALTH_ZONES:
        n, usual = counts[zone], expected[zone]
        if n >= usual * HIGH_RATIO and n - usual >= MIN_GAP:
            found.append(Anomaly(zone, n, usual, "high", cutoff < 86400))
        elif n <= usual * LOW_RATIO and usual - n >= MIN_GAP:
            found.append(Anomaly(zone, n, usual, "low", cutoff < 86400))
    return found
