from datetime import date, datetime, timedelta

from pawwatch import report, store
from pawwatch.anomaly import Anomaly

TODAY = date(2026, 10, 9)


def at(day, hour):
    return datetime.combine(day, datetime.min.time()) + timedelta(hours=hour)


def add(conn, zone, day, hour, simulated=False):
    ts = at(day, hour).timestamp()
    store.insert_event(conn, f"cam_{zone}", zone, ts, ts + 60, simulated=simulated)


def usual_week(conn):
    for i in range(1, 8):
        day = TODAY - timedelta(days=i)
        for zone, hour in [("food", 7), ("food", 18), ("water", 9), ("water", 15), ("litter", 10), ("litter", 20)]:
            add(conn, zone, day, hour, simulated=True)


def test_normal_day():
    conn = store.connect(":memory:")
    usual_week(conn)
    for zone, hour in [("food", 7), ("food", 18), ("water", 9), ("water", 15), ("litter", 10), ("litter", 20)]:
        add(conn, zone, TODAY, hour)
    text = report.daily_report(conn, TODAY, now=at(TODAY, 23))
    assert text == (
        "Tangerine ate twice, drank water twice and used the litter box twice today. "
        "Nothing unusual compared with the past week."
    )


def test_high_litter_gets_comparison_and_advice():
    conn = store.connect(":memory:")
    usual_week(conn)
    add(conn, "food", TODAY, 7)
    for hour in range(8, 15):
        add(conn, "litter", TODAY, hour)
    add(conn, "forbidden", TODAY, 13)
    text = report.daily_report(conn, TODAY, now=at(TODAY, 16))
    assert text == (
        "Tangerine ate once, didn't drink and used the litter box 7 times today. "
        "Tangerine jumped onto a no-go spot once. "
        "Litter box visits are well above usual (about 1 by this time). "
        "Keep an eye on it, and consider a vet visit if it continues."
    )


def test_describe_anomaly_stands_alone():
    assert report.describe_anomaly(Anomaly("food", 0, 4, "low", "day")) == (
        "Tangerine didn't eat today; usually about 4 a day. Keep an eye on it, and consider a vet visit if it continues."
    )
    assert report.describe_anomaly(Anomaly("water", 1, 4.4, "low", "so_far")).startswith(
        "Tangerine only drank water once today; usually about 4 by this time."
    )


def test_past_day_wording_and_simulated_label():
    conn = store.connect(":memory:")
    usual_week(conn)
    text = report.daily_report(conn, TODAY - timedelta(days=1), now=at(TODAY, 12))
    assert text.startswith("[Simulated data] Tangerine ate twice")
    assert "on Thursday, Oct 8." in text


def test_empty_day_and_no_history():
    conn = store.connect(":memory:")
    assert report.daily_report(conn, TODAY, now=at(TODAY, 8)) == "No visits recorded for Tangerine today yet."
    add(conn, "food", TODAY, 7)
    assert "isn't enough history" in report.daily_report(conn, TODAY, now=at(TODAY, 8))


def test_short_clips_name_what_was_on_camera():
    conn = store.connect(":memory:")
    usual_week(conn)
    day_ts = datetime.combine(TODAY, datetime.min.time()).timestamp()
    store.insert_recording(conn, "cam_food2", ["food"], day_ts + 22 * 3600 + 22, day_ts + 22 * 3600 + 91)
    store.insert_recording(conn, "cam_bed", ["forbidden"], day_ts + 22 * 3600 + 1340, day_ts + 22 * 3600 + 1409)
    add(conn, "food", TODAY, 22 + 1 / 60)
    add(conn, "forbidden", TODAY, 22 + 23 / 60)
    text = report.daily_report(conn, TODAY, now=at(TODAY + timedelta(days=1), 12))
    assert text == (
        "Tangerine ate once on Friday, Oct 9. "
        "Cameras were recording 22:00–22:02 and 22:22–22:24. "
        "The water bowl and the litter box weren't on camera. "
        "Tangerine jumped onto a no-go spot once. "
        "Nothing unusual compared with the past week."
    )
