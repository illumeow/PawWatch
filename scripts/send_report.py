"""Send the daily report to the owner's phone over LINE and/or Discord (see pawwatch.notify).

Run: uv run python scripts/send_report.py                       # today so far
     uv run python scripts/send_report.py --day 2026-10-10      # a past day, in full
     uv run python scripts/send_report.py --dry-run             # print it, send nothing
Nightly on the Linux host, from crontab -e (the variables in pawwatch.notify must be set there too):
     0 22 * * * cd /path/to/PawWatch && uv run python scripts/send_report.py
"""

import argparse
import os
from datetime import date

from pawwatch import notify, report, store


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--db", default=os.environ.get("PAWWATCH_DB", store.DEFAULT_DB))
    ap.add_argument("--day", type=date.fromisoformat, default=None, help="default: today so far")
    ap.add_argument("--cat", default=os.environ.get("PAWWATCH_CAT", "Tangerine"))
    ap.add_argument("--dry-run", action="store_true", help="print the message, send nothing")
    args = ap.parse_args()

    text = f"PawWatch daily report\n{report.daily_report(store.connect(args.db), args.day, args.cat)}"
    print(text)
    if args.dry_run:
        return
    if not notify.channels():
        raise SystemExit("not sent: set LINE_CHANNEL_TOKEN and LINE_USER_ID, or DISCORD_WEBHOOK_URL")
    sent = notify.send(text)
    if not sent:
        raise SystemExit("not sent: every channel failed")
    print(f"sent to {', '.join(sent)}")


if __name__ == "__main__":
    main()
