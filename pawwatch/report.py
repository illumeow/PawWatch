"""Daily report text. Owner: B. Template sentences; an on-device LLM rewrite is optional later.

Wording suggests watching or seeing a vet, never a diagnosis. Simulated days are labeled.
"""
from datetime import datetime

from pawwatch import anomaly, store

DID = {"food": "ate", "water": "drank water", "litter": "used the litter box"}
DID_NOT = {"food": "didn't eat", "water": "didn't drink", "litter": "didn't use the litter box"}
NOUN = {"food": "Meals", "water": "Water visits", "litter": "Litter box visits"}
ADVICE = "Keep an eye on it, and consider a vet visit if it continues."


def times(n):
    return {1: "once", 2: "twice"}.get(n, f"{n} times")


def join(parts):
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def describe_anomaly(a, cat_name="Tangerine"):
    """One alert sentence, e.g. for the dashboard or a notification."""
    usual = f"usually about {round(a.expected)} {'by this time' if a.partial_day else 'a day'}"
    if a.count == 0:
        return f"{cat_name} {DID_NOT[a.zone]} today; {usual}. {ADVICE}"
    only = "only " if a.direction == "low" else ""
    return f"{cat_name} {only}{DID[a.zone]} {times(a.count)} today; {usual}. {ADVICE}"


def daily_report(conn, day=None, cat_name="Tangerine", now=None):
    """Plain-language summary, e.g. "Tangerine ate 4 times, drank water 6 times (2 more than usual) and ..." """
    now = now or datetime.now()
    day = day or now.date()
    seconds = anomaly.seconds_so_far(day, now)
    counts = anomaly.counts_until(conn, day, seconds)
    expected, history_days = anomaly.expected_counts(conn, day, now)
    when = "today" if day == now.date() else f"on {day:%A, %b} {day.day}"

    start = anomaly.day_start(day)
    day_events = store.events_between(conn, start, start + seconds)
    label = "[Simulated data] " if day_events and all(ev.simulated for ev in day_events) else ""

    if not day_events:
        return f"No visits recorded for {cat_name} {when}{' yet' if seconds < 86400 else ''}."

    alerts = anomaly.find_anomalies(conn, day, now) if history_days else []
    alerted = {a.zone for a in alerts}
    parts = []
    for zone in anomaly.HEALTH_ZONES:
        n = counts[zone]
        if not n:
            parts.append(DID_NOT[zone])
            continue
        part = f"{DID[zone]} {times(n)}"
        if history_days and zone not in alerted:
            diff = n - round(expected[zone])
            if abs(diff) >= 2:
                part += f" ({abs(diff)} {'more' if diff > 0 else 'fewer'} than usual)"
        parts.append(part)
    sentences = [f"{cat_name} {join(parts)} {when}."]

    if counts["forbidden"]:
        sentences.append(f"{cat_name} jumped onto a no-go spot {times(counts['forbidden'])}.")

    if not history_days:
        sentences.append("There isn't enough history yet to compare with a usual day.")
    elif not alerts:
        sentences.append("Nothing unusual compared with the past week.")
    else:
        for a in alerts:
            usual = f"about {round(a.expected)} {'by this time' if a.partial_day else 'a day'}"
            sentences.append(f"{NOUN[a.zone]} are well {'above' if a.direction == 'high' else 'below'} usual ({usual}).")
        sentences.append(ADVICE)

    return label + " ".join(sentences)
