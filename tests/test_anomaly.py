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
    assert (a.zone, a.count, a.expected, a.direction, a.scope) == ("litter", 8, 3, "high", "so_far")


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
    assert (a.zone, a.count, a.expected, a.direction, a.scope) == ("food", 1, 4, "low", "day")


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


def record(conn, camera, zones, day, start_hour, end_hour):
    store.insert_recording(conn, camera, zones, at(day, start_hour).timestamp(), at(day, end_hour).timestamp())


def test_short_clip_is_compared_only_over_its_hours():
    """2 minutes of food-cam footage with one meal is not "didn't drink" or "barely ate" all day."""
    conn = store.connect(":memory:")
    week_of(conn, [("food", 7), ("food", 12), ("food", 18), ("water", 9), ("water", 15), ("water", 21), ("litter", 10)])
    record(conn, "cam_food", ["food"], TODAY, 22, 22 + 2 / 60)
    add(conn, "food", TODAY, 22)
    now = at(TODAY + timedelta(days=1), 12)
    assert anomaly.find_anomalies(conn, TODAY, now) == []
    spans = anomaly.watched(conn, TODAY, now)
    assert spans["water"] == [] and spans["food"] == [(22 * 3600, 22 * 3600 + 120)]
    assert anomaly.expected_counts(conn, TODAY, now)[0] == {"food": 0}


def test_recorded_hours_still_flag_a_real_drop():
    conn = store.connect(":memory:")
    week_of(conn, [("water", h) for h in (1, 3, 5, 7)])
    record(conn, "cam_water", ["water"], TODAY, 0, 8)
    add(conn, "water", TODAY, 2)
    [a] = anomaly.find_anomalies(conn, TODAY, now=at(TODAY + timedelta(days=1), 12))
    assert (a.zone, a.count, a.expected, a.direction, a.scope) == ("water", 1, 4, "low", "recorded")


def test_partly_recorded_days_are_left_out_of_the_baseline():
    conn = store.connect(":memory:")
    week_of(conn, [("food", 7), ("food", 8)])
    prev = TODAY - timedelta(days=1)
    record(conn, "cam_food", ["food"], prev, 20, 24)  # yesterday's footage doesn't cover 6-9 today
    record(conn, "cam_food", ["food"], TODAY, 6, 9)
    expected, used = anomaly.expected_counts(conn, TODAY, now=at(TODAY, 23))
    assert (expected, used) == ({"food": 2}, 6)


def test_merge_and_covers():
    assert anomaly.merge([(5, 8), (0, 2), (1, 3), (8, 9), (4, 4)]) == [(0, 3), (5, 9)]
    assert anomaly.covers([(0, 10)], [(2, 3), (5, 6)])
    assert not anomaly.covers([(0, 4), (5, 10)], [(3, 6)])
