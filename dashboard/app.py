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
REFRESH_S = 3  # visits processed while the page is open show up within this
MIN_BAND = 1 / 96  # bands are drawn at least this share of the visible time range wide
STEPS = [f"{m // 60:02d}:{m % 60:02d}" for m in range(0, 24 * 60 + 1, 15)]  # hours slider, every 15 min

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
    df = pd.DataFrame(
        [e.__dict__ for e in events], columns=["camera", "zone", "start_ts", "end_ts", "duration_s", "simulated"]
    )
    df["start"] = (
        pd.to_datetime(df["start_ts"], unit="s", utc=True)
        .dt.tz_convert(datetime.now().astimezone().tzinfo)
        .dt.tz_localize(None)
    )
    df["end"] = df["start"] + pd.to_timedelta(df["duration_s"], unit="s")
    df["Zone"] = df["zone"].map(LABELS)
    df["Data"] = df["simulated"].map({True: "simulated", False: "real"})
    df["visit"] = range(len(df))  # identity for the hover selection
    return df


def watched_frame(spans, day, hours=(0.0, 24.0)):
    """Rows for the shaded "on camera" bands: one per zone and watched span.

    Bands are drawn at least MIN_BAND of the visible range wide, so a 1-minute clip shows on a 24 h axis without
    looking longer than it was once zoomed in; tooltips keep the real times.
    """
    min_band = (hours[1] - hours[0]) * 3600 * MIN_BAND
    day0 = datetime.combine(day, datetime.min.time())
    rows = []
    for z in ZONES:
        for s, e in spans[z]:
            mid, half = (s + e) / 2, max(e - s, min_band) / 2
            rows.append(
                {
                    "Zone": LABELS[z],
                    "from": day0 + timedelta(seconds=s),
                    "to": day0 + timedelta(seconds=e),
                    "x": day0 + timedelta(seconds=mid - half),
                    "x2": day0 + timedelta(seconds=mid + half),
                }
            )
    return pd.DataFrame(rows, columns=["Zone", "from", "to", "x", "x2"])


def timeline_chart(df, day, spans=None, hours=(0.0, 24.0)):
    """One row per zone, one mark per visit. Simulated visits are faded only when mixed with real ones.

    A visit is a tick (visible at any zoom) over a bar from its start to its end (its length shows once zoomed in).
    Hover snaps to the nearest visit, so a 30 s visit on a 24 h axis doesn't need pixel-perfect aim.
    spans: watched hours per zone, drawn as shaded bands when only part of the day was filmed.
    hours: the part of the day to show, in hours, e.g. (7.0, 9.5).
    """
    mixed = df["simulated"].nunique() > 1
    day0 = datetime.combine(day, datetime.min.time())
    rows = [LABELS[z] for z in ZONES]
    time_scale = alt.Scale(domain=[day0 + timedelta(hours=hours[0]), day0 + timedelta(hours=hours[1])])
    x = alt.X("start:T", title=None, scale=time_scale, axis=alt.Axis(format="%H:%M", tickCount=12, grid=True))
    y = alt.Y("Zone:N", title=None, sort=rows, scale=alt.Scale(domain=rows))
    color = alt.Color("Zone:N", scale=zone_scale(), legend=None)
    opacity = alt.Opacity(
        "Data:N", scale=alt.Scale(domain=["real", "simulated"], range=[1.0, SIM_OPACITY if mixed else 1.0]), legend=None
    )
    hover = alt.selection_point(on="pointerover", nearest=True, fields=["visit"], empty=False, clear="pointerout")
    base = alt.Chart(df).encode(x=x, y=y)

    durations = base.mark_bar(height=14, cornerRadius=2, clip=True).encode(x2="end:T", color=color, opacity=opacity)
    ticks = base.mark_tick(thickness=3, cornerRadius=1.5, clip=True).encode(
        color=color,
        opacity=opacity,
        size=alt.condition(hover, alt.value(34), alt.value(22)),  # the hovered visit lifts, keeping its color
    )
    hits = (  # invisible, larger than the mark: the pointer only has to be closest
        base.mark_point(size=700, opacity=0, clip=True)
        .encode(
            tooltip=[
                alt.Tooltip("Zone:N"),
                alt.Tooltip("start:T", title="Started", format="%H:%M:%S"),
                alt.Tooltip("end:T", title="Ended", format="%H:%M:%S"),
                alt.Tooltip("duration_s:Q", title="Seconds", format=".0f"),
                alt.Tooltip("Data:N"),
            ]
        )
        .add_params(hover)
    )
    layers = [durations, ticks, hits]
    if spans is not None:
        bands = (
            alt.Chart(watched_frame(spans, day, hours))
            .mark_rect(opacity=0.18, color="gray", clip=True)
            .encode(
                x=alt.X("x:T", scale=time_scale),
                x2="x2:T",
                y=alt.Y("Zone:N", sort=rows),
                tooltip=[
                    alt.Tooltip("Zone:N"),
                    alt.Tooltip("from:T", title="On camera from", format="%H:%M"),
                    alt.Tooltip("to:T", title="until", format="%H:%M"),
                ],
            )
        )
        layers.insert(0, bands)
    if day == date.today():
        now = pd.DataFrame({"now": [datetime.now()]})
        layers.append(
            alt.Chart(now).mark_rule(strokeDash=[4, 3], strokeWidth=1, opacity=0.6, clip=True).encode(x="now:T")
        )
    return alt.layer(*layers).properties(height=200)


def trend_chart(rows, zone, color, ymax):
    """Daily visits for one zone; simulated days faded and starred."""
    df = pd.DataFrame(rows)
    bars = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, width={"band": 0.6}, color=color)
        .encode(
            x=alt.X("label:N", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("count:Q", title=None, scale=alt.Scale(domain=[0, ymax]), axis=alt.Axis(tickMinStep=1, grid=True)),
            opacity=alt.Opacity(
                "Data:N", scale=alt.Scale(domain=["real", "simulated"], range=[1.0, SIM_OPACITY]), legend=None
            ),
            tooltip=[alt.Tooltip("day:N", title="Day"), alt.Tooltip("count:Q", title="Visits"), alt.Tooltip("Data:N")],
        )
    )
    return bars.properties(title=LABELS[zone], height=180)


def week_rows(conn, day):
    """Per zone: [{day, label, count, Data}] for the 7 days before `day` plus `day` itself."""
    rows = {z: [] for z in ZONES}
    for i in range(7, -1, -1):
        d = day - timedelta(days=i)
        evs = events_on(conn, d)
        simulated = bool(evs) and all(e.simulated for e in evs)
        label = ("today" if d == date.today() else f"{d:%a} {d.day}") + (
            "*" if simulated else ""
        )  # 8 days: weekdays repeat
        for z in ZONES:
            rows[z].append(
                {
                    "day": d.isoformat(),
                    "label": label,
                    "count": sum(e.zone == z for e in evs),
                    "Data": "simulated" if simulated else "real",
                }
            )
    return rows


with st.sidebar:
    st.header("PawWatch")
    db_path = st.text_input("Database", os.environ.get("PAWWATCH_DB", str(store.DEFAULT_DB)))
    cat = st.text_input("Cat's name", "Tangerine")
    live = st.toggle(f"Auto-refresh every {REFRESH_S} s", value=True)

# Today is always offered, so a dashboard opened before the first visit picks up footage processed while it's open.
events = all_events(store.connect(db_path))
days = sorted({datetime.fromtimestamp(e.start_ts).date() for e in events} | {date.today()}, reverse=True)
real_days = [datetime.fromtimestamp(e.start_ts).date() for e in events if not e.simulated]
with st.sidebar:
    day = st.selectbox(
        "Day",
        days,
        index=days.index(max(real_days, default=date.today())),
        format_func=lambda d: "Today" if d == date.today() else d.strftime("%a, %b %d"),
    )


@st.fragment(run_every=f"{REFRESH_S}s" if live else None)
def body():
    conn = store.connect(db_path)
    now = datetime.now()
    day_events = events_on(conn, day)
    simulated_day = bool(day_events) and all(e.simulated for e in day_events)
    when = "Today" if day == now.date() else day.strftime("%A, %B %d")

    st.title(f"{cat} · {when}")
    st.caption(
        "Laptop prototype · events only, no video stored"
        + (" · **this day uses simulated data**" if simulated_day else "")
    )

    with st.container(border=True):
        st.markdown(f"**Daily report**  \n{report.daily_report(conn, day, cat_name=cat, now=now)}")

    for a in anomaly.find_anomalies(conn, day, now):
        st.warning(
            report.describe_anomaly(a, cat, when.lower() if day == now.date() else f"on {when}"),
            icon=":material/warning:",
        )

    spans = anomaly.watched(conn, day, now)
    counts = anomaly.counts(conn, day, spans)
    expected, _ = anomaly.expected_counts(conn, day, now)
    for col, z in zip(st.columns(4), ZONES, strict=True):
        if not spans[z]:
            col.metric(LABELS[z], "–", delta="not on camera", delta_color="off", delta_arrow="off", border=True)
            continue
        usual = {"day": "a day", "so_far": "by now", "recorded": "in these hours"}[anomaly.scope(spans[z], day, now)]
        diff = counts[z] - round(expected[z]) if z in expected else None
        delta = None if diff is None else (f"same as usual {usual}" if diff == 0 else f"{diff:+d} vs usual {usual}")
        col.metric(
            LABELS[z],
            counts[z],
            delta=delta,
            delta_color="off",
            delta_arrow="off" if diff == 0 else "auto",
            border=True,
        )

    st.subheader("Visits through the day")
    partly_filmed = any(anomaly.scope(spans[z], day, now) == "recorded" for z in ZONES)
    if day_events:
        start, end = st.select_slider("Hours shown", STEPS, value=(STEPS[0], STEPS[-1]), key="hours")
        hours = (STEPS.index(start) / 4, max(STEPS.index(end), STEPS.index(start) + 1) / 4)
        chart = timeline_chart(frame(day_events), day, spans if partly_filmed else None, hours)
        st.altair_chart(chart, width="stretch")
        if partly_filmed:
            st.caption("Shaded: hours on camera. Only those hours are compared with the usual.")
    else:
        st.caption("No visits recorded on this day.")

    st.subheader("Past week")
    rows = week_rows(conn, day)
    ymax = max(max(r["count"] for r in rows[z]) for z in ZONES) + 1
    cols = st.columns(2) + st.columns(2)  # 2x2, so every day label fits
    for col, z, color in zip(cols, ZONES, colors(), strict=True):
        col.altair_chart(trend_chart(rows[z], z, color, ymax), width="stretch")
    if any(r["Data"] == "simulated" for r in rows[ZONES[0]]):
        st.caption("\\* Faded days use **simulated** data, to give the anomaly check a baseline.")

    with st.expander("What PawWatch stores"):
        total = len(all_events(conn))
        st.markdown(f"**{total} events** in the database · **0 images** · **0 video**. One row per visit:")
        table = frame(day_events)[["camera", "Zone", "start", "duration_s", "Data"]] if day_events else pd.DataFrame()
        st.dataframe(
            table.rename(columns={"camera": "Camera", "start": "Started", "duration_s": "Seconds"}),
            hide_index=True,
            width="stretch",
        )


body()
