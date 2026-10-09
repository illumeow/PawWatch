import random
from datetime import date, datetime

from pawwatch import simulate, store


def test_simulate_day_is_plausible_and_deterministic():
    day = date(2026, 10, 5)
    a = simulate.simulate_day(day, random.Random(1))
    b = simulate.simulate_day(day, random.Random(1))
    assert a == b
    zones = [zone for _, zone, _, _ in a]
    assert 2 <= zones.count("food") <= 4
    assert 2 <= zones.count("litter") <= 4
    for _, _, start, end in a:
        assert datetime.fromtimestamp(start).date() == day
        assert end > start


def test_seed_marks_simulated_and_skips_real_days():
    conn = store.connect(":memory:")
    real_day = date(2026, 10, 8)
    real_ts = datetime(2026, 10, 8, 9).timestamp()
    store.insert_event(conn, "cam_food", "food", real_ts, real_ts + 60)

    seeded, _ = simulate.seed(conn, 7, real_day, random.Random(0))

    assert seeded == 6
    day_events = store.events_between(conn, real_ts - 9 * 3600, real_ts + 15 * 3600)
    assert [ev.simulated for ev in day_events] == [False]
    week = store.events_between(conn, datetime(2026, 10, 2).timestamp(), datetime(2026, 10, 8).timestamp())
    assert week and all(ev.simulated for ev in week)


def test_delete_simulated_keeps_real_events():
    conn = store.connect(":memory:")
    store.insert_event(conn, "cam_food", "food", 0, 60)
    store.insert_event(conn, "cam_food", "food", 100, 160, simulated=True)
    assert store.delete_simulated(conn) == 1
    assert len(store.events_between(conn, 0, 1000)) == 1
