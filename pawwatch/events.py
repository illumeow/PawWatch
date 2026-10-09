"""Detections over time to visits. Owner: A. Pure logic: no model, no video, no database.

Input is one sample per processed frame: (video_ts, zone or None), in time order.
Rules (docs/Worklist.md):
- a visit counts only after the cat stays in one zone at least a minimum dwell time;
- debounce: dropouts up to a gap tolerance don't close a visit, so a flickering box isn't counted twice;
- a visit still open at the end of the stream is closed and counted.
A visit runs from the first to the last sample that saw the cat in its zone.
Forbidden zones use a shorter dwell, so a quick jump still counts, and are signalled on every sample the cat is in one
(VisitTracker.alarm_zone), because the alarm can't wait for the visit to end.
"""
from dataclasses import dataclass

MIN_DWELL_S = 5.0
FORBIDDEN_DWELL_S = 1.0
GAP_TOLERANCE_S = 3.0
FORBIDDEN = "forbidden"


@dataclass(frozen=True)
class Visit:
    zone: str
    start_ts: float
    end_ts: float


class VisitTracker:
    """Feed samples with update(); each call returns the visits that just finished. Call close() at the end.

    After each update(), alarm_zone is the forbidden zone the cat is in at that sample, or None.
    """

    def __init__(self, min_dwell=MIN_DWELL_S, gap_tolerance=GAP_TOLERANCE_S, forbidden_dwell=FORBIDDEN_DWELL_S):
        self.min_dwell = min_dwell
        self.gap_tolerance = gap_tolerance
        self.forbidden_dwell = forbidden_dwell
        self.zone = None  # zone of the open visit, or None
        self.start = self.last_seen = None
        self.alarm_zone = None

    def update(self, ts, zone):
        self.alarm_zone = zone if zone == FORBIDDEN else None
        done = []
        if self.zone is not None and (ts - self.last_seen > self.gap_tolerance or zone not in (None, self.zone)):
            done = self.close()
        if zone is not None:
            if self.zone is None:
                self.zone, self.start = zone, ts
            self.last_seen = ts
        return done

    def close(self):
        """End the open visit, if any. Returns it in a list if it lasted long enough."""
        if self.zone is None:
            return []
        visit = Visit(self.zone, self.start, self.last_seen)
        self.zone = self.start = self.last_seen = None
        dwell = self.forbidden_dwell if visit.zone == FORBIDDEN else self.min_dwell
        return [visit] if visit.end_ts - visit.start_ts >= dwell else []


def visits(samples, min_dwell=MIN_DWELL_S, gap_tolerance=GAP_TOLERANCE_S, forbidden_dwell=FORBIDDEN_DWELL_S):
    """All visits in a finished stream of (ts, zone or None) samples."""
    tracker = VisitTracker(min_dwell, gap_tolerance, forbidden_dwell)
    found = []
    for ts, zone in samples:
        found += tracker.update(ts, zone)
    return found + tracker.close()
