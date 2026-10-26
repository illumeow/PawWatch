"""Daily report text. Template sentences; an on-device LLM rewrite is optional later.

Wording suggests watching or seeing a vet, never a diagnosis. Simulated data is labeled by the dashboard, not here.
"""

import sqlite3
from datetime import date, datetime

from pawwatch import anomaly, store

DID = {"food": "ate", "water": "drank water", "litter": "used the litter box"}
DID_NOT = {"food": "didn't eat", "water": "didn't drink", "litter": "didn't use the litter box"}
NOUN = {"food": "Meals", "water": "Water visits", "litter": "Litter box visits"}
PLACE = {"food": "the food bowl", "water": "the water bowl", "litter": "the litter box", "forbidden": "the no-go spot"}
USUAL = {"day": "a day", "so_far": "by this time", "recorded": "in the same hours"}
ADVICE = "Keep an eye on it, and consider a vet visit if it continues."


def times(n: int) -> str:
    return {1: "once", 2: "twice"}.get(n, f"{n} times")


def join(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def clock(seconds: float) -> str:
    return f"{int(seconds) // 3600:02d}:{int(seconds) % 3600 // 60:02d}"


def on_camera(spans: anomaly.Spans) -> str:
    """Watched hours in words, e.g. "22:00–22:02 and 22:22–22:24", or "about 9 hours" when there are many spans."""
    if len(spans) > 3:
        return f"about {round(sum(e - s for s, e in spans) / 3600)} hours"
    return join([f"{clock(s)}–{clock(e + 59)}" for s, e in spans])


def gaps(spans: anomaly.Spans, until: float) -> anomaly.Spans:
    """The parts of [0, until) not covered by spans (merged)."""
    found, at = [], 0.0
    for s, e in spans:
        if s > at:
            found.append((at, s))
        at = max(at, e)
    return found + ([(at, until)] if at < until else [])


def capitalized(text: str) -> str:
    return text[:1].upper() + text[1:]


def describe_anomaly(a: anomaly.Anomaly, cat_name: str = "Tangerine", when: str = "today") -> str:
    """One alert sentence, e.g. for the dashboard or a notification."""
    usual = f"usually about {round(a.expected)} {USUAL[a.scope]}"
    if a.count == 0:
        return f"{cat_name} {DID_NOT[a.zone]} {when}; {usual}. {ADVICE}"
    only = "only " if a.direction == "low" else ""
    return f"{cat_name} {only}{DID[a.zone]} {times(a.count)} {when}; {usual}. {ADVICE}"


def daily_report(
    conn: sqlite3.Connection, day: date | None = None, cat_name: str = "Tangerine", now: datetime | None = None
) -> str:
    """Plain-language summary, e.g. "Tangerine ate 4 times, drank water 6 times (2 more than usual) and ..."

    Only watched hours count: zones whose camera wasn't recording are named as such, never as "didn't eat".
    """
    now = now or datetime.now()
    day = day or now.date()
    seconds = anomaly.seconds_so_far(day, now)
    spans = anomaly.watched(conn, day, now)
    counts = anomaly.counts(conn, day, spans)
    expected, history_days = anomaly.expected_counts(conn, day, now)
    when = "today" if day == now.date() else f"on {day:%A, %b} {day.day}"

    start = anomaly.day_start(day)
    day_events = store.events_between(conn, start, start + seconds)

    if not day_events:
        return f"No visits recorded for {cat_name} {when}{' yet' if seconds < 86400 else ''}."

    alerts = anomaly.find_anomalies(conn, day, now) if history_days else []
    alerted = {a.zone for a in alerts}
    parts, off_camera = [], []
    for zone in anomaly.HEALTH_ZONES:
        n = counts[zone]
        if not spans[zone]:
            off_camera.append(PLACE[zone])
            continue
        if not n:
            parts.append(DID_NOT[zone])
            continue
        part = f"{DID[zone]} {times(n)}"
        if zone in expected and zone not in alerted:
            diff = n - round(expected[zone])
            if abs(diff) >= 2:
                part += f" ({abs(diff)} {'more' if diff > 0 else 'fewer'} than usual)"
        parts.append(part)
    sentences = [f"{cat_name} {join(parts)} {when}."] if parts else []
    # Partly filmed zones: mostly off (short clips) -> when cameras recorded; mostly on (an outage) -> when it was off.
    partial = [z for z in store.ZONES if spans[z] and anomaly.scope(spans[z], day, now) == "recorded"]
    mostly_off = [z for z in partial if sum(e - s for s, e in spans[z]) < seconds / 2]
    if mostly_off:
        all_spans = anomaly.merge([s for z in mostly_off for s in spans[z]])
        sentences.append(f"Cameras were recording {on_camera(all_spans)}.")
    for z in partial:
        if z not in mostly_off:
            sentences.append(f"{capitalized(PLACE[z])} camera was off {on_camera(gaps(spans[z], seconds))}.")
    if off_camera:
        verb = "wasn't" if len(off_camera) == 1 else "weren't"
        sentences.append(f"{join(off_camera)[0].upper()}{join(off_camera)[1:]} {verb} on camera.")

    if counts["forbidden"]:
        sentences.append(f"{cat_name} jumped onto a no-go spot {times(counts['forbidden'])}.")

    if not history_days:
        sentences.append("There isn't enough history yet to compare with a usual day.")
    elif not alerts:
        sentences.append("Nothing unusual compared with the past week.")
    else:
        for a in alerts:
            usual = f"about {round(a.expected)} {USUAL[a.scope]}"
            sentences.append(
                f"{NOUN[a.zone]} are well {'above' if a.direction == 'high' else 'below'} usual ({usual})."
            )
        sentences.append(ADVICE)

    return " ".join(sentences)
