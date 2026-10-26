# Demo video

Under 3 minutes, English, uploaded to YouTube as unlisted. Owner: @illumeow, recorded and edited alone on a MacBook:
screen recordings with ⌘⇧5, voice-over in QuickTime, edit in iMovie. No other hardware.

The video does two jobs: explain the proposal (problem, solution, business) and demo every feature on real footage.
About 340 words of narration, about 2:20 at a calm pace; the cut lands near 2:40, which leaves the alarm and shots
room to breathe, and 20 s of slack under the limit.

## Shot list

| Time | Part | Picture | Source |
| --- | --- | --- | --- |
| 0:00–0:17 | 1 Hook | Tangerine eating, then a few seconds of Ami drinking | `TangerineEat.mp4`, `AmiDrink.mp4`, raw |
| 0:17–0:32 | 2 Problem | Slides "Cat hides illness", then "Today's smart devices each watch one spot" | Slide stills |
| 0:32–0:46 | 3 Solution | Slides "Solution: PawWatch", then "Why run AI at home, not in the cloud" | Slide stills |
| 0:46–1:05 | 4a Visits | Detection window: eating (count 0 → 1), quick cuts of drinking (Ami) and the litter box | Recording B |
| 1:05–1:17 | 4b Alarm | Detection window on the bed clip (red box, ALARM) beside Discord, the text arriving; **alarm sound** | Recording C |
| 1:17–1:38 | 4c Dashboard | Real day, open "What PawWatch stores"; then the alert day | Recording D |
| 1:38–1:46 | 4d Report | Daily report box (zoom), then the same report arriving in Discord | Recordings D, E |
| 1:46–2:05 | 5 System | Slides "Architecture: video in, events out", then "Hardware: one host, many fixed cameras" | Slide stills |
| 2:05–2:28 | 6 Business | Slides "Market", "Business model: buy once, no monthly fee", "Targeted audience roadmap" | Slide stills |
| 2:28–2:40 | 7 Close | End card: PawWatch, the closing line, github.com/illumeow/PawWatch | iMovie title |

On screen in the edit:

- Over 4a and 4b: the detection window already shows "Running on laptop · YOLOv8n · target: ASUS UGen300".
- Over the alert day, the zoomed report and the Discord report (4c, 4d): a title "Simulated data". The real day's dashboard
  labels its simulated week in its own header line.
- Over the drinking cut: "Ami, our other cat".

Two cats appear: Tangerine (eating, bed, litter box) and Ami (drinking, the only drinking footage we have).
PawWatch logs one cat per household, so the narration says "our cats" and never presents Ami's visits as Tangerine's.
The dashboard is Tangerine's.

## Narration

Spellings like "U Gen 300" show how to say it; titles use the normal spelling (UGen300, Hailo-10H, YOLOv8).
Prices are New Taiwan dollars; say "N T dollars" once. If the cut runs over 2:55, drop the sentence marked (cut).

**1 Hook (16 s).** These are our cats, Tangerine and Ami. If one started drinking twice as much water, or using the
litter box twice as often, would you notice? Changes like these are often the first sign of illness, and cats hide
them well.

**2 Problem (14 s).** Most of us are out all day, so we miss them. Smart feeders and litter boxes each watch one spot.
Pet cameras see more, but they stream our homes to the cloud, for a monthly fee.

**3 Solution (13 s).** So we built PawWatch. Cameras watch the food bowl, the water bowl and the litter box. An AI
accelerator at home recognizes the cat and logs every visit. Video never leaves the house.

**4a Visits (17 s).** Here it is on real footage. When the cat stays in a zone for five seconds, PawWatch logs one visit:
when it started, and how long it lasted. The frame is thrown away. Drinking and the litter box work the same way.

**4b Alarm (9 s).** Some spots are off-limits. When Tangerine jumps onto the bed, PawWatch sounds an alarm, and texts
the owner on LINE or Discord.

**4c Dashboard (19 s).** Each visit becomes one row in a local database: no images, no video. The dashboard compares
today with the cat's usual week. In this simulated example, Tangerine used the litter box eight times; her usual is
about three. PawWatch suggests watching her, and considering a vet visit. It never diagnoses.

**4d Report (6 s).** Every evening, a plain-English report reaches the owner's phone, ready to show the vet.

**5 System (18 s).** Today, the prototype runs on a laptop. The target is the ASUS U Gen 300, whose Hailo 10 H chip draws
two and a half watts. Our detector returns the same boxes as ASUS's U Gen 300 demos, so moving over means swapping one
module.

**6 Business (21 s).** We start with owners of cats aged seven or older: two hundred sixty-six thousand homes in Taiwan.
The full kit is fourteen thousand nine hundred N T dollars, paid once, with no subscription: less than half an
emergency visit. Next, vet clinics recommend it for cats with kidney disease. (cut) Later, device makers license PawWatch.

**7 Close (5 s).** PawWatch: know your cat's routine, without sending your home to the cloud.

Check before recording:

- 4c matches `data/alert.db` (8 litter box visits, usual about 3). If the alert day changes, change the numbers here.
- 5 and 6 match the slides: 2.5 W, 266k homes, NT$14,900 Full Kit, NT$30,000+ emergency, the roadmap.
  If @bbwinner changes those slides, change the numbers here.

## Before any recording

- **Quiet screen:** Focus → Do Not Disturb, with Discord allowed. Quit every other app; hide the Dock (System Settings →
  Desktop & Dock → Automatically hide). Nothing personal on screen: no terminal, browser tabs, bookmarks or other Discord servers.
- **Discord:** a dedicated server with one channel, say `#pawwatch`, and the webhook named "PawWatch" with an icon.
  Close the server list's other servers if you can't leave them. In the terminal tab you'll run everything from, before any
  recording starts:
  ```bash
  read -rs DISCORD_WEBHOOK_URL && export DISCORD_WEBHOOK_URL   # paste the URL, Enter; it doesn't show or enter history
  ```
- **⌘⇧5 settings:** Options → Microphone: None; Show Mouse Clicks off. Recordings carry no sound; the alarm is added in the edit.
- One take per recording below is enough; trim in iMovie. Name each file after its letter.

## Recordings

All commands are from the repo root. They're the ones in [Commands.md](Commands.md), shown here in recording order.

**B. Detection window, three clips.** ⌘⇧5 → Record Selected Window, click the window as soon as it opens.
```bash
uv run python -m pawwatch.run data/videos/TangerineEat.mp4 --zones config/zones/cam_food.json --start 2026-10-10T07:30 --fps 5 --device mps --show --db data/scratch.db
uv run python -m pawwatch.run data/videos/AmiDrink.mp4 --zones config/zones/cam_water.json --start 2026-10-10T08:00 --fps 5 --device mps --show --db data/scratch.db
uv run python -m pawwatch.run data/videos/TangerinePee.mp4 --zones config/zones/cam_litter_box.json --start 2026-10-10T06:15 --fps 5 --device mps --show --db data/scratch.db
```

**C. Alarm and the text.** Discord open on the right half of the screen, the detection window on the left.
Start the command, then ⌘⇧5 → Record Selected Portion around both windows. Keep it unmuted: the sound tells you
where the alarm is when you edit.
```bash
uv run python -m pawwatch.run data/videos/TangerineJumpOntoBed.mov --zones config/zones/cam_bed.json --start 2026-10-10T21:40 --fps 5 --device mps --show --db data/scratch.db
```
Discord gets "PawWatch: your cat jumped onto a no-go spot (cam_bed) at 21:40."

**D. Dashboards.** A clean browser window, zoomed so text reads at 1080p (⌘+ once or twice). ⌘⇧5 → Record Selected Window.
Move the mouse slowly; scroll, don't jump.
```bash
uv run python scripts/build_demo.py --device mps
PAWWATCH_DB=data/demo.db uv run streamlit run dashboard/app.py --client.toolbarMode minimal
```
Real day: the page opens on Sat, Oct 10. Scroll through the counts and the timeline, then open "What PawWatch stores".
Ctrl+C, then the alert day:
```bash
PAWWATCH_DB=data/alert.db uv run streamlit run dashboard/app.py --client.toolbarMode minimal
```
Pick Sat, Oct 10 in the Day picker at the top right. Hold on the alert, then on the daily report box (zoomed in the edit).

**E. Report in Discord.** ⌘⇧5 → Record Selected Window on Discord, then run:
```bash
uv run python scripts/send_report.py --db data/alert.db --day 2026-10-10
```

**F. Slides.** Last, once @bbwinner's deck is final. Open `slides/slides.pdf` in Preview, View → Slideshow, and take one
screenshot per slide in the shot list with ⌘⇧3. Stills are sharper than a screen recording and easy to time.

**G. Hook footage.** Nothing to record: the raw clips from `data/videos/` go straight into iMovie.

## Voice-over

QuickTime Player → File → New Audio Recording, one file per part (1, 2, 3, 4a …), so a retake replaces one file.
Built-in mic, a quiet room with soft furnishings, about 30 cm from the laptop, fans quiet (nothing heavy running).
Read part 1 once as a test and listen back on headphones before recording the rest. Leave a second of silence at each end.

## Edit in iMovie

1. New Movie. Lay the voice-over files on the timeline in order, then cut the pictures to them.
2. Slide stills: Crop → Fit, so iMovie's Ken Burns zoom doesn't move them. Hold each for its sentence.
3. Report zoom (4d): Crop → Ken Burns, from the whole dashboard to the report box.
4. Alarm (4b): drag `/System/Library/Sounds/Sosumi.aiff` (Finder → Go → Go to Folder) under the frame where ALARM appears.
   Duck the voice-over there if they overlap.
5. Titles: "Simulated data" and "Ami, our other cat" as lower thirds; the end card as a title on black.
6. Keep the hook's raw footage audio low or off, so it doesn't fight the narration.
7. File → Share → File: 1080p, High quality. Check the length is under 3:00.

## Before uploading

- [ ] Watch it once at full screen: no webhook URL, terminal, notification, or person on screen.
- [ ] "Simulated data" shows on every alert-day shot and on the Discord report.
- [ ] Ami's drinking is never called Tangerine's.
- [ ] Every number matches the slides and the dashboard.
- [ ] Under 3:00.

Then upload to YouTube as unlisted, and send the link to @bbwinner for the slides; add it to the README too.
