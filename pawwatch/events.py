"""Detections over time to visits. Owner: A. Pure logic: no model, no video, no database.

Input is one sample per processed frame: (video_ts, zone or None), in time order.
Rules (docs/Worklist.md):
- a visit counts only after the cat stays in one zone at least a minimum dwell time;
- debounce: dropouts up to a gap tolerance don't close a visit, so a flickering box isn't counted twice;
- a visit still open at the end of the stream is closed and counted.
A visit runs from the first to the last sample that saw the cat in its zone.
Next (issue 05): entering a forbidden zone must be reported immediately (for alarm.trigger), not only when the visit ends.
"""
from dataclasses import dataclass

MIN_DWELL_S = 5.0
GAP_TOLERANCE_S = 3.0


@dataclass(frozen=True)
class Visit:
    zone: str
    start_ts: float
    end_ts: float


class VisitTracker:
    """Feed samples with update(); each call returns the visits that just finished. Call close() at the end."""

    def __init__(self, min_dwell=MIN_DWELL_S, gap_tolerance=GAP_TOLERANCE_S):
        self.min_dwell = min_dwell
        self.gap_tolerance = gap_tolerance
        self.zone = None  # zone of the open visit, or None
        self.start = self.last_seen = None

    def update(self, ts, zone):
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
        return [visit] if visit.end_ts - visit.start_ts >= self.min_dwell else []


def visits(samples, min_dwell=MIN_DWELL_S, gap_tolerance=GAP_TOLERANCE_S):
    """All visits in a finished stream of (ts, zone or None) samples."""
    tracker = VisitTracker(min_dwell, gap_tolerance)
    found = []
    for ts, zone in samples:
        found += tracker.update(ts, zone)
    return found + tracker.close()
