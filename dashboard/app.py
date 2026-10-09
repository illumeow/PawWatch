"""Streamlit dashboard. Owner: B.

Run: uv run streamlit run dashboard/app.py   (PAWWATCH_DB=data/demo.db to open another database)
One page: daily report, today's counts vs usual, alerts, timeline, 7-day trend (simulated days marked), stored data.
Reads only through pawwatch.store / anomaly / report.
"""
import os
from datetime import date, datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

from pawwatch import anomaly, report, store

# Display order and colors follow the zone, never its rank. Validated categorical slots 1-4 (light / dark).
ZONES = ["water", "food", "litter", "forbidden"]
LABELS = {"water": "Water", "food": "Food", "litter": "Litter box", "forbidden": "No-go spots"}
COLORS = {
    "light": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"],
    "dark": ["#3987e5", "#d95926", "#199e70", "#c98500"],
}
SIM_OPACITY = 0.4

st.set_page_config(page_title="PawWatch", page_icon=":material/pets:", layout="wide")


def colors():
    theme = getattr(getattr(st.context, "theme", None), "type", None)
    return COLORS["dark" if theme == "dark" else "light"]


def zone_scale():
    return alt.Scale(domain=[LABELS[z] for z in ZONES], range=colors())


def all_events(conn):
    return store.events_between(conn, 0, datetime(2100, 1, 1).timestamp())


def events_on(conn, day):
    start = anomaly.day_start(day)
    return store.events_between(conn, start, start + 86400)


def frame(events):
    df = pd.DataFrame([e.__dict__ for e in events], columns=["camera", "zone", "start_ts", "end_ts", "duration_s", "simulated"])
    df["start"] = pd.to_datetime(df["start_ts"], unit="s", utc=True).dt.tz_convert(datetime.now().astimezone().tzinfo).dt.tz_localize(None)
    df["Zone"] = df["zone"].map(LABELS)
    df["Data"] = df["simulated"].map({True: "simulated", False: "real"})
    return df


def watched_frame(spans, day):
    """Rows for the shaded "on camera" bands: one per zone and watched span."""
    day0 = datetime.combine(day, datetime.min.time())
    return pd.DataFrame([{"Zone": LABELS[z], "from": day0 + timedelta(seconds=s), "to": day0 + timedelta(seconds=e)}
                         for z in ZONES for s, e in spans[z]], columns=["Zone", "from", "to"])


def timeline_chart(df, day, spans=None):
    """One row per zone, a tick per visit, across the day. Simulated visits are faded only when mixed with real ones.

    spans: watched hours per zone, drawn as shaded bands when only part of the day was filmed.
    """
    mixed = df["simulated"].nunique() > 1
    day0 = datetime.combine(day, datetime.min.time())
    base = alt.Chart(df).encode(
        x=alt.X("start:T", title=None, scale=alt.Scale(domain=[day0, day0 + timedelta(days=1)]), axis=alt.Axis(format="%H:%M", tickCount=12, grid=True)),
        y=alt.Y("Zone:N", title=None, sort=[LABELS[z] for z in ZONES], scale=alt.Scale(domain=[LABELS[z] for z in ZONES])),
    )
    ticks = base.mark_tick(thickness=3, size=22, cornerRadius=1.5).encode(
        color=alt.Color("Zone:N", scale=zone_scale(), legend=None),
        opacity=alt.Opacity("Data:N", scale=alt.Scale(domain=["real", "simulated"], range=[1.0, SIM_OPACITY if mixed else 1.0]), legend=None),
        tooltip=[
            alt.Tooltip("Zone:N"),
            alt.Tooltip("start:T", title="Started", format="%H:%M"),
            alt.Tooltip("duration_s:Q", title="Seconds", format=".0f"),
            alt.Tooltip("Data:N"),
        ],
    )
    layers = [ticks]
    if spans is not None:
        bands = alt.Chart(watched_frame(spans, day)).mark_rect(opacity=0.12, color="gray").encode(
            x="from:T", x2="to:T", y=alt.Y("Zone:N", sort=[LABELS[z] for z in ZONES]),
            tooltip=[alt.Tooltip("Zone:N"), alt.Tooltip("from:T", title="On camera from", format="%H:%M"),
                     alt.Tooltip("to:T", title="until", format="%H:%M")])
        layers.insert(0, bands)
    if day == date.today():
        now = pd.DataFrame({"now": [datetime.now()]})
        layers.append(alt.Chart(now).mark_rule(strokeDash=[4, 3], strokeWidth=1, opacity=0.6).encode(x="now:T"))
    return alt.layer(*layers).properties(height=200)


def trend_chart(rows, zone, color, ymax):
    """Daily visits for one zone; simulated days faded and starred."""
    df = pd.DataFrame(rows)
    bars = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, width={"band": 0.6}, color=color).encode(
        x=alt.X("label:N", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("count:Q", title=None, scale=alt.Scale(domain=[0, ymax]), axis=alt.Axis(tickMinStep=1, grid=True)),
        opacity=alt.Opacity("Data:N", scale=alt.Scale(domain=["real", "simulated"], range=[1.0, SIM_OPACITY]), legend=None),
        tooltip=[alt.Tooltip("day:N", title="Day"), alt.Tooltip("count:Q", title="Visits"), alt.Tooltip("Data:N")],
    )
    return bars.properties(title=LABELS[zone], height=180)


def week_rows(conn, day):
    """Per zone: [{day, label, count, Data}] for the 7 days before `day` plus `day` itself."""
    rows = {z: [] for z in ZONES}
    for i in range(7, -1, -1):
        d = day - timedelta(days=i)
        evs = events_on(conn, d)
        simulated = bool(evs) and all(e.simulated for e in evs)
        label = ("today" if d == date.today() else f"{d:%a} {d.day}") + ("*" if simulated else "")  # 8 days: weekdays repeat
        for z in ZONES:
            rows[z].append({"day": d.isoformat(), "label": label, "count": sum(e.zone == z for e in evs), "Data": "simulated" if simulated else "real"})
    return rows


with st.sidebar:
    st.header("PawWatch")
    db_path = st.text_input("Database", os.environ.get("PAWWATCH_DB", str(store.DEFAULT_DB)))
    cat = st.text_input("Cat's name", "Tangerine")
    live = st.toggle("Auto-refresh every 10 s", value=True)

conn = store.connect(db_path)
events = all_events(conn)
if not events:
    st.title("PawWatch")
    st.info("No events yet. For a demo database run `uv run python scripts/seed_fake.py --with-today`, "
            "or process footage with `pawwatch.run`.", icon=":material/info:")
    st.stop()

days = sorted({datetime.fromtimestamp(e.start_ts).date() for e in events}, reverse=True)
with st.sidebar:
    day = st.selectbox("Day", days, index=0, format_func=lambda d: "Today" if d == date.today() else d.strftime("%a, %b %d"))


@st.fragment(run_every="10s" if live else None)
def body():
    conn = store.connect(db_path)
    now = datetime.now()
    day_events = events_on(conn, day)
    simulated_day = bool(day_events) and all(e.simulated for e in day_events)
    when = "Today" if day == now.date() else day.strftime("%A, %B %d")

    st.title(f"{cat} · {when}")
    st.caption("Laptop prototype · events only, no video stored" + (" · **this day uses simulated data**" if simulated_day else ""))

    with st.container(border=True):
        st.markdown(f"**Daily report**  \n{report.daily_report(conn, day, cat_name=cat, now=now)}")

    for a in anomaly.find_anomalies(conn, day, now):
        st.warning(report.describe_anomaly(a, cat, when.lower() if day == now.date() else f"on {when}"),
                   icon=":material/warning:")

    spans = anomaly.watched(conn, day, now)
    counts = anomaly.counts(conn, day, spans)
    expected, _ = anomaly.expected_counts(conn, day, now)
    for col, z in zip(st.columns(4), ZONES):
        if not spans[z]:
            col.metric(LABELS[z], "–", delta="not on camera", delta_color="off", delta_arrow="off", border=True)
            continue
        usual = {"day": "a day", "so_far": "by now", "recorded": "in these hours"}[anomaly.scope(spans[z], day, now)]
        diff = counts[z] - round(expected[z]) if z in expected else None
        delta = None if diff is None else (f"same as usual {usual}" if diff == 0 else f"{diff:+d} vs usual {usual}")
        col.metric(LABELS[z], counts[z], delta=delta, delta_color="off", delta_arrow="off" if diff == 0 else "auto", border=True)

    st.subheader("Visits through the day")
    partly_filmed = any(anomaly.scope(spans[z], day, now) == "recorded" for z in ZONES)
    if day_events:
        st.altair_chart(timeline_chart(frame(day_events), day, spans if partly_filmed else None), width="stretch")
        if partly_filmed:
            st.caption("Shaded: hours on camera. Only those hours are compared with the usual.")
    else:
        st.caption("No visits recorded on this day.")

    st.subheader("Past week")
    rows = week_rows(conn, day)
    ymax = max(max(r["count"] for r in rows[z]) for z in ZONES) + 1
    cols = st.columns(2) + st.columns(2)  # 2x2, so every day label fits
    for col, z, color in zip(cols, ZONES, colors()):
        col.altair_chart(trend_chart(rows[z], z, color, ymax), width="stretch")
    if any(r["Data"] == "simulated" for r in rows[ZONES[0]]):
        st.caption("\\* Faded days use **simulated** data, to give the anomaly check a baseline.")

    with st.expander("What PawWatch stores"):
        total = len(all_events(conn))
        st.markdown(f"**{total} events** in the database · **0 images** · **0 video**. One row per visit:")
        table = frame(day_events)[["camera", "Zone", "start", "duration_s", "Data"]] if day_events else pd.DataFrame()
        st.dataframe(table.rename(columns={"camera": "Camera", "start": "Started", "duration_s": "Seconds"}),
                     hide_index=True, width="stretch")


body()
