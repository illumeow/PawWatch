from datetime import date, datetime, timedelta

from pawwatch import anomaly, store

TODAY = date(2026, 10, 9)


def at(day, hour):
    return datetime.combine(day, datetime.min.time()) + timedelta(hours=hour)


def add(conn, zone, day, hour):
    ts = at(day, hour).timestamp()
    store.insert_event(conn, f"cam_{zone}", zone, ts, ts + 60)


def week_of(conn, per_day):
    """per_day: [(zone, hour), ...] repeated on each of the 7 days before TODAY."""
    for i in range(1, 8):
        for zone, hour in per_day:
            add(conn, zone, TODAY - timedelta(days=i), hour)


def test_flags_twice_the_usual_litter_visits():
    conn = store.connect(":memory:")
    week_of(conn, [("litter", 8), ("litter", 14), ("litter", 20)])
    for hour in range(8, 16):
        add(conn, "litter", TODAY, hour)
    [a] = anomaly.find_anomalies(conn, TODAY, now=at(TODAY, 21))
    assert (a.zone, a.count, a.expected, a.direction, a.partial_day) == ("litter", 8, 3, "high", True)


def test_normal_morning_is_not_low():
    conn = store.connect(":memory:")
    week_of(conn, [("food", 7), ("food", 12), ("food", 18), ("food", 22)])
    add(conn, "food", TODAY, 7)
    assert anomaly.find_anomalies(conn, TODAY, now=at(TODAY, 9)) == []


def test_flags_low_food_once_the_day_is_over():
    conn = store.connect(":memory:")
    week_of(conn, [("food", 7), ("food", 12), ("food", 18), ("food", 22)])
    add(conn, "food", TODAY, 7)
    [a] = anomaly.find_anomalies(conn, TODAY, now=at(TODAY + timedelta(days=1), 9))
    assert (a.zone, a.count, a.expected, a.direction, a.partial_day) == ("food", 1, 4, "low", False)


def test_small_differences_and_forbidden_zone_are_ignored():
    conn = store.connect(":memory:")
    week_of(conn, [("water", 10)])
    add(conn, "water", TODAY, 9)
    add(conn, "water", TODAY, 10)
    for hour in range(9, 15):
        add(conn, "forbidden", TODAY, hour)
    assert anomaly.find_anomalies(conn, TODAY, now=at(TODAY, 23)) == []


def test_days_without_any_events_are_left_out_of_the_baseline():
    conn = store.connect(":memory:")
    add(conn, "litter", TODAY - timedelta(days=1), 10)
    add(conn, "litter", TODAY - timedelta(days=1), 12)
    expected, used = anomaly.expected_counts(conn, TODAY, now=at(TODAY, 23))
    assert used == 1
    assert expected["litter"] == 2


def test_no_history_means_no_alerts():
    conn = store.connect(":memory:")
    for hour in range(8, 18):
        add(conn, "litter", TODAY, hour)
    assert anomaly.find_anomalies(conn, TODAY, now=at(TODAY, 20)) == []
