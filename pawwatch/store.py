"""Event storage. SHARED CONTRACT between A (writes) and B (reads): change only with a heads-up.

Only visits are stored: no frames, ever. A visit is written as soon as it qualifies (the cat stayed the minimum
dwell time) and its end is moved forward while the cat stays, so the dashboard follows a live stream; a visit that
never qualifies is never written. Timestamps are unix seconds derived from video time (recording start + frame
offset), not wall clock at processing time.
Each processed video file also gets a recordings row (which camera and zones were watched, and when), so a day
with a few hours of footage is compared only over those hours. Days without recordings count as watched all day.
"""

import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

DEFAULT_DB = Path("data/pawwatch.db")
ZONES: tuple[str, ...] = ("food", "water", "litter", "forbidden")

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  id         INTEGER PRIMARY KEY,
  camera     TEXT NOT NULL,
  zone       TEXT NOT NULL,
  start_ts   REAL NOT NULL,
  end_ts     REAL NOT NULL,
  duration_s REAL NOT NULL,
  simulated  INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS events_start ON events (start_ts);
CREATE TABLE IF NOT EXISTS recordings (
  id       INTEGER PRIMARY KEY,
  camera   TEXT NOT NULL,
  zones    TEXT NOT NULL,  -- comma-separated zone names this camera watches
  start_ts REAL NOT NULL,
  end_ts   REAL NOT NULL
);
"""


@dataclass(frozen=True)
class Event:
    camera: str
    zone: str
    start_ts: float
    end_ts: float
    duration_s: float
    simulated: bool


def connect(path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    """Open (and create if needed) the events database. ":memory:" gives a throwaway one."""
    path = Path(path)
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def insert_event(
    conn: sqlite3.Connection, camera: str, zone: str, start_ts: float, end_ts: float, simulated: bool = False
) -> int:
    """Store one visit (in progress or finished). Returns its row id for extend_event."""
    if zone not in ZONES:
        raise ValueError(f"unknown zone {zone!r}, expected one of {ZONES}")
    if end_ts < start_ts:
        raise ValueError("end_ts is before start_ts")
    cur = conn.execute(
        "INSERT INTO events (camera, zone, start_ts, end_ts, duration_s, simulated) VALUES (?, ?, ?, ?, ?, ?)",
        (camera, zone, start_ts, end_ts, end_ts - start_ts, int(simulated)),
    )
    conn.commit()
    assert cur.lastrowid is not None
    return cur.lastrowid


def extend_event(conn: sqlite3.Connection, event_id: int, end_ts: float) -> None:
    """Move a visit's end forward while the cat is still there."""
    conn.execute(
        "UPDATE events SET end_ts = MAX(end_ts, ?), duration_s = MAX(end_ts, ?) - start_ts WHERE id = ?",
        (end_ts, end_ts, event_id),
    )
    conn.commit()


@dataclass(frozen=True)
class Recording:
    camera: str
    zones: tuple[str, ...]
    start_ts: float
    end_ts: float


def insert_recording(
    conn: sqlite3.Connection, camera: str, zones: Iterable[str], start_ts: float, end_ts: float | None = None
) -> int:
    """Start logging what a camera watched, from start_ts. Returns the row id for extend_recording."""
    zones = list(zones)
    unknown = set(zones) - set(ZONES)
    if unknown:
        raise ValueError(f"unknown zones {sorted(unknown)}, expected some of {ZONES}")
    cur = conn.execute(
        "INSERT INTO recordings (camera, zones, start_ts, end_ts) VALUES (?, ?, ?, ?)",
        (camera, ",".join(zones), start_ts, start_ts if end_ts is None else end_ts),
    )
    conn.commit()
    assert cur.lastrowid is not None
    return cur.lastrowid


def extend_recording(conn: sqlite3.Connection, rec_id: int, end_ts: float) -> None:
    """Move a recording's end forward as frames are processed."""
    conn.execute("UPDATE recordings SET end_ts = MAX(end_ts, ?) WHERE id = ?", (end_ts, rec_id))
    conn.commit()


def recordings_between(conn: sqlite3.Connection, start_ts: float, end_ts: float) -> list[Recording]:
    """Recordings overlapping [start_ts, end_ts), oldest first."""
    rows = conn.execute(
        "SELECT camera, zones, start_ts, end_ts FROM recordings WHERE end_ts > ? AND start_ts < ? ORDER BY start_ts",
        (start_ts, end_ts),
    ).fetchall()
    return [Recording(c, tuple(z.split(",")) if z else (), s, e) for c, z, s, e in rows]


def delete_simulated(conn: sqlite3.Connection) -> int:
    """Remove all seeded fake events. Returns how many were deleted."""
    cur = conn.execute("DELETE FROM events WHERE simulated = 1")
    conn.commit()
    return cur.rowcount


def events_between(conn: sqlite3.Connection, start_ts: float, end_ts: float) -> list[Event]:
    """Visits that started in [start_ts, end_ts), oldest first."""
    rows = conn.execute(
        "SELECT camera, zone, start_ts, end_ts, duration_s, simulated FROM events"
        " WHERE start_ts >= ? AND start_ts < ? ORDER BY start_ts",
        (start_ts, end_ts),
    ).fetchall()
    return [Event(c, z, s, e, d, bool(sim)) for c, z, s, e, d, sim in rows]


def daily_counts(conn: sqlite3.Connection, days: int, today: date | None = None) -> dict[date, dict[str, int]]:
    """Visit counts per local day and zone for the last `days` days, today included.

    Returns {date: {zone: count}}, oldest day first, every day and zone present (zero-filled).
    """
    today = today or date.today()
    first = today - timedelta(days=days - 1)
    counts = {first + timedelta(days=i): dict.fromkeys(ZONES, 0) for i in range(days)}
    start = datetime.combine(first, time()).timestamp()
    end = datetime.combine(today + timedelta(days=1), time()).timestamp()
    for ev in events_between(conn, start, end):
        counts[datetime.fromtimestamp(ev.start_ts).date()][ev.zone] += 1
    return counts
