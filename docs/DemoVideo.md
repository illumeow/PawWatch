# Demo video

One take, no editing: record the whole screen with the MacBook mic, read the script, switch apps as it says.
About 2:30, with time to show the dashboard. Must be under 3:00. Upload to YouTube as unlisted.

**Bold** is what you do. Plain text is what you say. Slow down; pauses are fine.

## Set up (before you hit record)

1. **Quiet screen.** Focus → Do Not Disturb, allow Discord only. Quit every app not listed below. Hide the Dock
   (System Settings → Desktop & Dock → Automatically hide). Mac volume about 50%: the mic picks up the alarm from the speakers.
2. **Discord.** Your webhook's server, notifications on "All messages". Leave Discord running in the background
   (not in front), so the alarm text pops up as a banner.
3. **Slides.** Open `slides/slides.pdf` in **Preview**: View → Single Page, hide the sidebar and toolbar, Window → Fill,
   ⌘9 (zoom to fit). Go to p. 3 ("Cat hides illness"). → is the next page; ⌥⌘G, the number, Enter jumps to a page.
4. **Dashboards.** In a terminal window you won't show. On the recording day, make the live database: a simulated week
   before today, nothing today yet. Then run both dashboards, one tab each:
   ```bash
   rm -f data/live.db && uv run python scripts/seed_fake.py --db data/live.db
   PAWWATCH_DB=data/live.db uv run streamlit run dashboard/app.py --client.toolbarMode minimal --server.port 8501 --server.headless true
   PAWWATCH_DB=data/alert.db uv run streamlit run dashboard/app.py --client.toolbarMode minimal --server.port 8502 --server.headless true
   ```
   **Browser**, one window, Window → Fill: tab 1 `localhost:8501` (live, opens on Today, every zone "not on camera"),
   tab 2 `localhost:8502`, pick **Sat, Oct 10** in the Day picker. Scroll both to the top. Leave tab 1 showing.
5. **Terminal** for the take: a fresh window, big font (⌘+ a few times), Window → Fill. Then:
   ```bash
   read -rs DISCORD_WEBHOOK_URL && export DISCORD_WEBHOOK_URL   # paste the URL, Enter; it doesn't show
   scripts/demo_take.sh
   ```
   It clears today's visits from the last take, then waits on "Enter: food bowl camera". The clips write to
   `data/live.db` at the current time, so tab 1 shows them within 3 s.
6. **QuickTime**: open `data/videos/AmiDrink.mp4`, mute it, Window → Fill, drag the playhead to 0:15. Leave it in front.
7. **Mic check.** ⌘⇧5 → Record Entire Screen, Options → Microphone: MacBook Pro Microphone, Show Mouse Clicks off.
   Record 10 s of talking plus one alarm, stop, listen on headphones. Delete it.
8. Move the mouse to a corner. Do one full dry run without recording, then reset steps 3–6 (Preview on p. 3,
   browser tabs at the top, `scripts/demo_take.sh` waiting, QuickTime at 0:15).

## The take

**⌘⇧5 → Record. Wait 2 seconds. Press Space in QuickTime.**

This is Ami, one of our cats. Would you notice if she drank twice as much water?

**Space (pause). ⌘Tab to Preview: p. 3 "Cat hides illness".**

Cats hide illness. A change in daily habits is often the first sign.

**→ → p. 5 "Today's smart devices each watch one spot".**

Today's devices each watch one spot, and pet cameras stream your home to the cloud.

**→ p. 6 "Solution: PawWatch".**

So we built PawWatch. Cameras watch the food, the water and the litter box, and AI at home logs every visit.

**→ p. 7 "Why run AI at home, not in the cloud".**

Video never leaves the house.

**⌘Tab to Terminal. Enter.** The food bowl window opens in a few seconds.

Here's Tangerine at the food bowl. After five seconds in the zone, PawWatch logs a visit, and throws the frame away.

**Wait for the food count to go from 0 to 1 (about 20 s into the clip). q.**
**Terminal shows "Enter: bed camera". Enter.**

Some spots are off-limits.

**The alarm sounds (about 6 s in) and the Discord banner pops up, top right.**

An alarm, and a text to the owner.

**Let the clip end (15 s), or q. ⌘Tab to the browser, tab 1 (live).**

Both visits are already on the dashboard.

**Scroll down to "What PawWatch stores" and click it open. Hold 2 s.**

It stores only events. No images, no video.

**⌃Tab to tab 2 (alert day). Scroll to the top.**

Here's a simulated day with an alert.

**Point at the yellow warning, then the four counts with "vs usual". Hold 3 s.**
**Scroll to "Visits through the day". Hover a litter box bar for its time and length. Drag across the strip under
the chart to zoom into a few hours; double-click it to zoom back out.**

Every visit through the day,

**Scroll to "Past week". Hover the litter box chart's last bar.**

against her usual week.

**Scroll back up to the daily report box.**

Each evening, a short report

**⌘Tab to Terminal ("Enter: send the daily report"). Enter. ⌘Tab to Discord when the banner pops up.**

goes to the owner's phone.

**⌘Tab to Preview. → → p. 9 "Architecture: video in, events out".**

Today it runs on a laptop.

**→ p. 10 "Hardware: one host, many fixed cameras".**

The target is the ASUS U Gen 300; moving over means swapping one module.

**⌥⌘G 19: p. 19 "Business model: buy once, no monthly fee".**

One box, bought once. No subscription.

**→ p. 20 "Targeted audience roadmap".**

First cat owners, then vet clinics, then device makers.

**⌥⌘G 1: p. 1, the title slide.**

PawWatch: know your cat's routine, without sending your home to the cloud.

**Hold 3 seconds. ⌃⌘Esc stops the recording.**

## If something goes wrong

Stop (⌃⌘Esc), reset (setup step 8), start over. A take is under 3 minutes.
If a take runs over 2:55, spend less time zooming the timeline.

## After the take

1. Open the recording in QuickTime and watch it once at full screen: no webhook URL, no stray notification,
   the alarm audible, under 3:00. Edit → Trim (⌘T) only if the first or last seconds are dead air.
2. Upload to YouTube as unlisted. Send the link to @bbwinner for the slides, and add it to the README.

If a slide is added or moved, check the page numbers in the take.
