"""Seed simulated history (simulated=1) so the dashboard and anomaly alert have a 7-day baseline. Owner: B.

Run: uv run python scripts/seed_fake.py                 # 7 days before today
     uv run python scripts/seed_fake.py --end 2026-10-10   # 7 days before the day the footage was recorded
     uv run python scripts/seed_fake.py --with-today       # also fake "today", with extra litter visits, for dashboard work
Re-running replaces earlier simulated events. Days that already have real events are never overwritten.
"""
import argparse
import random
from datetime import date, timedelta

from pawwatch import store
from pawwatch.simulate import CAMERAS, has_real_events, seed, simulate_day


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=store.DEFAULT_DB)
    ap.add_argument("--days", type=int, default=7, help="days of history")
    ap.add_argument("--end", type=date.fromisoformat, default=None, help="the 'today' the history leads up to (default: today)")
    ap.add_argument("--with-today", action="store_true", help="also simulate today, with extra litter visits so the anomaly alert fires")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    today = args.end or date.today()
    rng = random.Random(args.seed)
    conn = store.connect(args.db)
    removed = store.delete_simulated(conn)
    seeded, written = seed(conn, args.days, today - timedelta(days=1), rng)
    print(f"removed {removed} old simulated events; seeded {seeded} days ({written} events) before {today}")

    if args.with_today:
        if has_real_events(conn, today):
            print(f"{today} has real events; not simulating it")
        else:
            visits = simulate_day(today, rng)
            for i in range(4):  # push litter visits well above the usual 2-4
                start = visits[0][2] + 3600 * (i + 1)
                visits.append((CAMERAS["litter"], "litter", start, start + 90))
            for camera, zone, start, end in visits:
                store.insert_event(conn, camera, zone, start, end, simulated=True)
            print(f"simulated {today} too ({len(visits)} events, extra litter visits)")


if __name__ == "__main__":
    main()
