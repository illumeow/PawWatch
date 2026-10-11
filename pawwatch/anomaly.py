"""Today vs the cat's usual pattern. Owner: B. Reads only through store.

"Usual" = the average over the previous 7 days, counted over the same hours of the day, so a normal morning
isn't flagged for missing the evening meal. Days with no events at all (cameras off) are left out of the baseline.

Only watched hours count. When run.py logged recordings for a day, each zone is compared only over the hours its
camera was recording, and only against past days whose cameras covered those hours too: 2 minutes of footage
with one meal is not "didn't drink all day". Days without recordings (simulated history) count as watched all day.

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
FULL_DAY = 86400.0


@dataclass(frozen=True)
class Anomaly:
    zone: str
    count: int
    expected: float
    direction: str  # "high" | "low"
    scope: str  # what was compared: "day" (all of it), "so_far" (today up to now) or "recorded" (some hours)


def day_start(day):
    return datetime.combine(day, time()).timestamp()


def seconds_so_far(day, now):
    """Seconds into `day` that count as "so far": the whole day once it's over."""
    elapsed = (now or datetime.now()).timestamp() - day_start(day)
    return min(max(elapsed, 0.0), FULL_DAY)


def merge(spans):
    """Sorted, non-overlapping version of [(start, end), ...]."""
    out = []
    for s, e in sorted(spans):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        elif e > s:
            out.append((s, e))
    return out


def covers(outer, inner):
    """True if every span in `inner` lies inside one span of `outer` (both merged)."""
    return all(any(os <= s and e <= oe for os, oe in outer) for s, e in inner)


def watched(conn, day, now=None):
    """{zone: [(start_s, end_s), ...]}: when each zone was on camera during `day`, in seconds into the day, up to now.

    A day without recordings counts as watched all day (so far) for every zone.
    """
    cutoff = seconds_so_far(day, now)
    start = day_start(day)
    recordings = store.recordings_between(conn, start, start + cutoff)
    if not recordings:
        return {zone: [(0.0, cutoff)] for zone in store.ZONES}
    spans = {zone: [] for zone in store.ZONES}
    for r in recordings:
        for zone in r.zones:
            spans[zone].append((max(r.start_ts - start, 0.0), min(r.end_ts - start, cutoff)))
    return {zone: merge(s) for zone, s in spans.items()}


def scope(spans, day, now=None):
    """How a zone's watched spans read: "day", "so_far" (today up to now) or "recorded" (some hours)."""
    if spans == [(0.0, FULL_DAY)]:
        return "day"
    if spans == [(0.0, seconds_so_far(day, now))]:
        return "so_far"
    return "recorded"


def counts(conn, day, spans):
    """Visits per zone on `day` that started inside that zone's spans ({zone: [(start_s, end_s), ...]})."""
    found = dict.fromkeys(store.ZONES, 0)
    start = day_start(day)
    for ev in store.events_between(conn, start, start + FULL_DAY):
        t = ev.start_ts - start
        if any(s <= t < e for s, e in spans.get(ev.zone, ())):
            found[ev.zone] += 1
    return found


def expected_counts(conn, day, now=None, window=WINDOW_DAYS):
    """Average visits per zone over the previous `window` days, over the hours that zone was watched on `day`.

    A past day counts for a zone only if its cameras covered those hours. Returns ({zone: mean}, days_used):
    zones without usable history are left out, and days_used is the most any zone had (0 = no history).
    """
    spans = watched(conn, day, now)
    totals = dict.fromkeys(store.ZONES, 0)
    days = dict.fromkeys(store.ZONES, 0)
    for i in range(1, window + 1):
        prev = day - timedelta(days=i)
        if not store.events_between(conn, day_start(prev), day_start(prev) + FULL_DAY):
            continue  # cameras off that day
        prev_spans = watched(conn, prev, now)
        prev_counts = counts(conn, prev, spans)
        for zone in store.ZONES:
            if spans[zone] and covers(prev_spans[zone], spans[zone]):
                totals[zone] += prev_counts[zone]
                days[zone] += 1
    expected = {zone: totals[zone] / days[zone] for zone in store.ZONES if days[zone]}
    return expected, max(days.values())


def find_anomalies(conn, day=None, now=None):
    """Health zones whose count over the watched hours of `day` differs a lot from the usual."""
    now = now or datetime.now()
    day = day or now.date()
    spans = watched(conn, day, now)
    expected, _ = expected_counts(conn, day, now)
    found_counts = counts(conn, day, spans)
    found = []
    for zone in HEALTH_ZONES:
        if zone not in expected:
            continue
        n, usual = found_counts[zone], expected[zone]
        if n >= usual * HIGH_RATIO and n - usual >= MIN_GAP:
            found.append(Anomaly(zone, n, usual, "high", scope(spans[zone], day, now)))
        elif n <= usual * LOW_RATIO and usual - n >= MIN_GAP:
            found.append(Anomaly(zone, n, usual, "low", scope(spans[zone], day, now)))
    return found
