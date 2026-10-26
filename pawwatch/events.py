"""Detections over time to visits. Pure logic: no model, no video, no database.

Input is one sample per processed frame: (video_ts, zone or None), in time order.
Rules:
- a visit counts only after the cat stays in one zone at least a minimum dwell time;
- debounce: dropouts up to a gap tolerance don't close a visit, so a flickering box isn't counted twice;
- a visit still open at the end of the stream is closed and counted.
A visit runs from the first to the last sample that saw the cat in its zone.
Forbidden zones use a shorter dwell, so a quick jump still counts, and are signalled on every sample the cat is in one
(VisitTracker.alarm_zone), because the alarm can't wait for the visit to end.
"""

from collections.abc import Iterable
from dataclasses import dataclass

MIN_DWELL_S = 5.0
FORBIDDEN_DWELL_S = 1.0
GAP_TOLERANCE_S = 5.0  # 3 s split real stays when a cat turned or was briefly hidden (petting, litter box rim)
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

    def __init__(
        self,
        min_dwell: float = MIN_DWELL_S,
        gap_tolerance: float = GAP_TOLERANCE_S,
        forbidden_dwell: float = FORBIDDEN_DWELL_S,
    ):
        self.min_dwell = min_dwell
        self.gap_tolerance = gap_tolerance
        self.forbidden_dwell = forbidden_dwell
        self.open: Visit | None = None  # the visit in progress: its zone, first and latest sample seeing the cat
        self.alarm_zone: str | None = None

    def update(self, ts: float, zone: str | None) -> list[Visit]:
        self.alarm_zone = zone if zone == FORBIDDEN else None
        done = []
        if self.open and (ts - self.open.end_ts > self.gap_tolerance or zone not in (None, self.open.zone)):
            done = self.close()
        if zone is not None:
            start = self.open.start_ts if self.open else ts
            self.open = Visit(zone, start, ts)
        return done

    def _long_enough(self, visit: Visit) -> bool:
        dwell = self.forbidden_dwell if visit.zone == FORBIDDEN else self.min_dwell
        return visit.end_ts - visit.start_ts >= dwell

    @property
    def counting(self) -> str | None:
        """Zone of the open visit once it has lasted long enough to count, else None. A visit that qualifies is
        never dropped, so run.py writes it to the database at this point and screens can count it."""
        return self.open.zone if self.open and self._long_enough(self.open) else None

    def close(self) -> list[Visit]:
        """End the open visit, if any. Returns it in a list if it lasted long enough."""
        visit, self.open = self.open, None
        return [visit] if visit and self._long_enough(visit) else []


def visits(
    samples: Iterable[tuple[float, str | None]],
    min_dwell: float = MIN_DWELL_S,
    gap_tolerance: float = GAP_TOLERANCE_S,
    forbidden_dwell: float = FORBIDDEN_DWELL_S,
) -> list[Visit]:
    """All visits in a finished stream of (ts, zone or None) samples."""
    tracker = VisitTracker(min_dwell, gap_tolerance, forbidden_dwell)
    found = []
    for ts, zone in samples:
        found += tracker.update(ts, zone)
    return found + tracker.close()
