from datetime import date, datetime

import pytest

from pawwatch import store


@pytest.fixture
def conn():
    return store.connect(":memory:")


def ts(day, hour):
    return datetime.combine(day, datetime.min.time()).timestamp() + hour * 3600


def test_insert_and_read_back(conn):
    d = date(2026, 10, 9)
    store.insert_event(conn, "cam_food", "food", ts(d, 8), ts(d, 8) + 90)
    [ev] = store.events_between(conn, ts(d, 0), ts(d, 24))
    assert (ev.camera, ev.zone, ev.duration_s, ev.simulated) == ("cam_food", "food", 90, False)


def test_rejects_unknown_zone(conn):
    with pytest.raises(ValueError):
        store.insert_event(conn, "cam_food", "sofa", 0, 1)


def test_daily_counts_zero_filled(conn):
    today = date(2026, 10, 9)
    store.insert_event(conn, "cam_litter", "litter", ts(today, 9), ts(today, 9) + 60)
    store.insert_event(conn, "cam_litter", "litter", ts(date(2026, 10, 8), 9), ts(date(2026, 10, 8), 9) + 60, simulated=True)
    counts = store.daily_counts(conn, 7, today=today)
    assert list(counts) == [date(2026, 10, d) for d in range(3, 10)]
    assert counts[today] == {"food": 0, "water": 0, "litter": 1, "forbidden": 0}
    assert counts[date(2026, 10, 8)]["litter"] == 1
