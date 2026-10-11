"""Streamlit dashboard. Owner: B.

Run: uv run streamlit run dashboard/app.py
Setup by environment: PAWWATCH_DB (default data/pawwatch.db), PAWWATCH_CAT (default Tangerine).
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
HIT_PX = 24  # width of the hover box around each visit
AXIS_PX = 80  # zone-label column of the timeline, the same in its detail and overview charts
REFRESH_S = 3  # visits processed while the page is open show up within this

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


def watched_frame(spans, day):
    """Rows for the shaded "on camera" bands: one per zone and watched span."""
    day0 = datetime.combine(day, datetime.min.time())
    rows = [
        {"Zone": LABELS[z], "from": day0 + timedelta(seconds=a), "to": day0 + timedelta(seconds=b)}
        for z in ZONES
        for a, b in spans[z]
    ]
    return pd.DataFrame(rows, columns=["Zone", "from", "to"])


def timeline_chart(df, day, spans=None):
    """Visits through the day: a detail chart over a full-day overview strip. Drag on the strip to zoom the detail
    chart to that time range, drag the selection to pan, double-click to go back to the whole day.

    Detail: one row per zone; a visit is a rounded bar from its start to its end (a short one still shows on the full
    day), with a hover area HIT_PX / 2 wider on every side. Simulated visits are faded only when mixed with real ones.
    spans: watched hours per zone, drawn as shaded bands when only part of the day was filmed.
    """
    mixed = df["simulated"].nunique() > 1
    day0 = datetime.combine(day, datetime.min.time())
    full_day = [day0, day0 + timedelta(days=1)]
    rows = [LABELS[z] for z in ZONES]
    zoom = alt.selection_interval(name="zoom", encodings=["x"])
    hover = alt.selection_point(on="pointerover", fields=["visit"], empty=False, clear="pointerout")
    color = alt.Color("Zone:N", scale=zone_scale(), legend=None)
    opacity = alt.Opacity(
        "Data:N",
        sort=["real", "simulated"],
        scale=alt.Scale(domain=["real", "simulated"], range=[1.0, SIM_OPACITY if mixed else 1.0]),
        legend=None,
    )
    y_axis = alt.Axis(minExtent=AXIS_PX, maxExtent=AXIS_PX)  # same width in both charts, so their times line up

    # Detail: the whole day, or the zoom selection once there is one (domainRaw overrides domain when set).
    detail_scale = alt.Scale(domain=full_day, domainRaw={"expr": "zoom.start"})
    axis = alt.Axis(format="%H:%M", tickCount=12, grid=True)
    detail_x = alt.X("start:T", title=None, scale=detail_scale, axis=axis)  # the range, declared on one layer only
    y = alt.Y("Zone:N", title=None, sort=rows, scale=alt.Scale(domain=rows), axis=y_axis)
    base = alt.Chart(df).encode(x=alt.X("start:T", title=None, axis=axis), y=y)
    # One rounded bar per visit, start to end. Its outline in the same color adds a few pixels on every side, so a
    # 30 s visit still shows on a 24 h axis; zoomed in it is a plain rounded bar. The hovered visit gets thicker.
    visits = base.mark_bar(cornerRadius=3, strokeWidth=4, strokeJoin="round", clip=True).encode(
        x=detail_x,
        x2="end:T",
        color=color,
        stroke=alt.Stroke("Zone:N", scale=zone_scale(), legend=None),
        opacity=opacity,
        size=alt.condition(hover, alt.value(22), alt.value(12)),
    )
    hits = (  # invisible, the bar plus HIT_PX / 2 on every side, so a short visit is easy to hover
        base.mark_bar(opacity=0, stroke="black", strokeWidth=HIT_PX, size=22, clip=True)
        .encode(
            x2="end:T",
            tooltip=[
                alt.Tooltip("Zone:N"),
                alt.Tooltip("start:T", title="Started", format="%H:%M:%S"),
                alt.Tooltip("end:T", title="Ended", format="%H:%M:%S"),
                alt.Tooltip("duration_s:Q", title="Seconds", format=".0f"),
            ],
        )
        .add_params(hover)
    )
    layers = [visits, hits]
    if spans is not None:
        bands = (  # the outline keeps a 1-minute clip visible on a 24 h axis without widening it when zoomed in
            alt.Chart(watched_frame(spans, day))
            .mark_rect(color="gray", fillOpacity=0.18, strokeOpacity=0.18, strokeWidth=4, clip=True)
            .encode(
                x="from:T",
                x2="to:T",
                y=alt.Y("Zone:N", sort=rows),
                tooltip=[
                    alt.Tooltip("Zone:N"),
                    alt.Tooltip("from:T", title="On camera from", format="%H:%M"),
                    alt.Tooltip("to:T", title="until", format="%H:%M"),
                ],
            )
        )
        layers.insert(0, bands)
    if day == date.today():  # to the minute, so the chart (and a zoom selection) isn't rebuilt on every refresh
        now = pd.DataFrame({"now": [datetime.now().replace(second=0, microsecond=0)]})
        layers.append(
            alt.Chart(now).mark_rule(strokeDash=[4, 3], strokeWidth=1, opacity=0.6, clip=True).encode(x="now:T")
        )
    detail = alt.layer(*layers).properties(height=200, width="container")

    # Overview: the whole day, small; the selection lives here.
    overview = (
        alt.Chart(df)
        .mark_tick(thickness=2, size=8)
        .encode(
            x=alt.X(
                "start:T",
                title=None,
                scale=alt.Scale(domain=full_day),
                axis=alt.Axis(format="%H:%M", tickCount=8, labelFontSize=10, grid=False),
            ),
            y=alt.Y(
                "Zone:N",
                title=None,
                sort=rows,
                scale=alt.Scale(domain=rows),
                axis=alt.Axis(labels=False, ticks=False, domain=False, minExtent=AXIS_PX, maxExtent=AXIS_PX),
            ),
            color=color,
            opacity=opacity,
        )
        .add_params(zoom)
        .properties(height=44, width="container")
    )
    return (
        alt.vconcat(detail, overview, spacing=6)
        .resolve_scale(x="independent")  # the overview always shows the whole day
        .properties(autosize=alt.AutoSizeParams(type="fit-x", contains="padding"))  # both fit the page width
    )


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
                "Data:N",
                sort=["real", "simulated"],
                scale=alt.Scale(domain=["real", "simulated"], range=[1.0, SIM_OPACITY]),
                legend=None,
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


# Setup, not UI: an owner never picks a database file or retypes the cat's name.
db_path = os.environ.get("PAWWATCH_DB", str(store.DEFAULT_DB))
cat = os.environ.get("PAWWATCH_CAT", "Tangerine")

# Today is always offered, so a dashboard opened before the first visit picks up footage processed while it's open.
events = all_events(store.connect(db_path))
days = sorted({datetime.fromtimestamp(e.start_ts).date() for e in events} | {date.today()}, reverse=True)
real_days = [datetime.fromtimestamp(e.start_ts).date() for e in events if not e.simulated]
title_col, day_col = st.columns([4, 1], vertical_alignment="bottom")
with day_col:  # the page's one control, in the header row
    day = st.selectbox(
        "Day",
        days,
        index=days.index(max(real_days, default=date.today())),
        format_func=lambda d: "Today" if d == date.today() else d.strftime("%a, %b %d"),
    )
with title_col:
    st.title(f"{cat} · {'Today' if day == date.today() else day.strftime('%A, %B %d')}")


@st.fragment(run_every=f"{REFRESH_S}s")
def body():
    conn = store.connect(db_path)
    now = datetime.now()
    day_events = events_on(conn, day)
    simulated_day = bool(day_events) and all(e.simulated for e in day_events)
    when = "Today" if day == now.date() else day.strftime("%A, %B %d")

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
        chart = timeline_chart(frame(day_events), day, spans if partly_filmed else None)
        st.altair_chart(chart, width="stretch", key="timeline")
        hint = "Drag across the strip below the chart to zoom in; double-click it for the whole day."
        if partly_filmed:
            hint += " Shaded: hours on camera; only those hours are compared with the usual."
        st.caption(hint)
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
