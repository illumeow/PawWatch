# Demo video

One take, no editing: record the whole screen with the MacBook mic, read the script, switch apps as it says.
About 2:45. Must be under 3:00. Upload to YouTube as unlisted.

**Bold** is what you do. Plain text is what you say. Slow down; pauses are fine.

## Set up (before you hit record)

1. **Quiet screen.** Focus → Do Not Disturb, allow Discord only. Quit every app not listed below. Hide the Dock
   (System Settings → Desktop & Dock → Automatically hide). Mac volume about 50%: the mic picks up the alarm from the speakers.
2. **Discord.** Your webhook's server, notifications on "All messages". Leave Discord running in the background
   (not in front), so the alarm text pops up as a banner.
3. **Video slides.** Only the slides the video uses, in its order. Rebuild if the deck changed:
   ```bash
   uv run --with pypdf python -c "from pypdf import PdfReader, PdfWriter; r = PdfReader('slides/slides.pdf'); w = PdfWriter(); [w.add_page(r.pages[i - 1]) for i in (3, 5, 6, 7, 9, 10, 18, 19, 20, 1)]; w.write('data/video-slides.pdf')"
   ```
   Open `data/video-slides.pdf` in **Preview**: View → Single Page, hide the sidebar and toolbar, Window → Fill,
   ⌘9 (zoom to fit). Stay on page 1 ("Cat hides illness"). → goes to the next slide.
4. **Dashboards.** In a terminal window you won't show, run both (one tab each):
   ```bash
   PAWWATCH_DB=data/demo.db uv run streamlit run dashboard/app.py --client.toolbarMode minimal --server.port 8501 --server.headless true
   PAWWATCH_DB=data/alert.db uv run streamlit run dashboard/app.py --client.toolbarMode minimal --server.port 8502 --server.headless true
   ```
   **Browser**, one window, Window → Fill: tab 1 `localhost:8501` (real day, opens on Sat, Oct 10),
   tab 2 `localhost:8502`, pick **Sat, Oct 10** in the Day picker. Scroll both to the top. Leave tab 1 showing.
5. **Terminal** for the take: a fresh window, big font (⌘+ a few times), Window → Fill. Then:
   ```bash
   read -rs DISCORD_WEBHOOK_URL && export DISCORD_WEBHOOK_URL   # paste the URL, Enter; it doesn't show
   scripts/demo_take.sh
   ```
   It clears the screen and waits on "Enter: food bowl camera".
6. **QuickTime**: open `data/videos/AmiDrink.mp4`, mute it, Window → Fill, drag the playhead to 0:15. Leave it in front.
7. **Mic check.** ⌘⇧5 → Record Entire Screen, Options → Microphone: MacBook Pro Microphone, Show Mouse Clicks off.
   Record 10 s of talking plus one alarm, stop, listen on headphones. Delete it.
8. Move the mouse to a corner. Do one full dry run without recording, then reset steps 3–6 (Preview page 1,
   browser tabs at the top, `scripts/demo_take.sh` waiting, QuickTime at 0:15).

## The take

**⌘⇧5 → Record. Wait 2 seconds. Press Space in QuickTime.**

This is Ami, one of our two cats. If she started drinking twice as much water, or using the litter box twice as
often, would you notice? Changes like these are often the first sign of illness, and cats hide them well.

**Space (pause). ⌘Tab to Preview: "Cat hides illness".**

Most of us are out all day, so we miss them.

**→ "Today's smart devices each watch one spot".**

Smart feeders and litter boxes each watch one spot. Pet cameras see more, but they stream our homes to the cloud,
for a monthly fee.

**→ "Solution: PawWatch".**

So we built PawWatch. Cameras watch the food bowl, the water bowl and the litter box. An AI accelerator at home
recognizes the cat and logs every visit.

**→ "Why run AI at home".**

Video never leaves the house, and there's no monthly fee.

**⌘Tab to Terminal. Enter.** The food bowl window opens in a few seconds.

Here it is on real footage of Tangerine, our other cat. When she stays in a zone for five seconds, PawWatch logs one
visit: when it started, and how long it lasted. The frame itself is thrown away.

**Wait for the food count to go from 0 to 1 (about 20 s into the clip).**

Drinking and the litter box work the same way.

**q.** Terminal shows "Enter: bed camera". **Enter.**

Some spots are off-limits. Watch the bed.

**The alarm sounds (about 6 s in) and the Discord banner pops up, top right.**

PawWatch sounds an alarm right away, and texts the owner on LINE or Discord.

**Let the clip end (15 s), or q.** ⌘Tab to the browser, tab 1 (real day).

Each visit becomes one row in a local database.

**Scroll down to "What PawWatch stores" and click it open.**

No images, no video: just when, where, and how long.

**⌃Tab to tab 2 (alert day).**

To show an alert, here is a simulated day. Tangerine used the litter box eight times; her usual is about three.
PawWatch suggests watching her, and considering a vet visit. It never diagnoses.

**Point at the daily report box.**

Every evening, a plain-English report like this reaches the owner's phone, ready to show the vet.

**⌘Tab to Preview. → "Architecture".**

Today, the prototype runs on a laptop.

**→ "Hardware".**

The target is the ASUS U Gen 300, whose Hailo 10 H chip draws two and a half watts. Our detector matches ASUS's
own U Gen 300 demos, so moving over means swapping one module.

**→ "Market".**

We start with owners of cats aged seven or older: two hundred sixty-six thousand homes in Taiwan.

**→ "Business model".**

The full kit is fourteen thousand nine hundred N T dollars, paid once, with no subscription: less than half of one
emergency visit.

**→ "Targeted audience roadmap".**

Next, vet clinics recommend it for cats with kidney disease. Later, device makers build PawWatch into their own products.

**→ title slide.**

PawWatch: know your cat's routine, without sending your home to the cloud.

**Hold 3 seconds. ⌃⌘Esc stops the recording.**

## If something goes wrong

Stop (⌃⌘Esc), reset (setup step 8), start over. A take is under 3 minutes.
If a take runs over 2:55, read faster through the slides, or drop "Drinking and the litter box work the same way."

## After the take

1. Open the recording in QuickTime and watch it once at full screen: no webhook URL, no stray notification,
   the alarm audible, under 3:00. Edit → Trim (⌘T) only if the first or last seconds are dead air.
2. Upload to YouTube as unlisted. Send the link to @bbwinner for the slides, and add it to the README.

Numbers to keep in step with the slides and data: 8 litter box visits against about 3 (`data/alert.db`), 2.5 W,
266k homes, NT$14,900, NT$30,000+ for an emergency visit (more than twice the kit). If a slide changes, change the line here,
and check the page numbers in setup step 3.
