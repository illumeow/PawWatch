# Product description: PawWatch

PawWatch is an in-home cat health monitor: cameras plus an edge AI accelerator (UGen300) automatically log how often the cat eats, drinks and uses the litter box, and raise an alarm when the cat jumps onto a forbidden zone. Video is processed only on the device: no cloud, no monthly fee.

## Why it's needed

- Cats instinctively hide pain and illness; changes in eating, drinking and elimination are often the earliest signs.
- Owners at work during the day can't see these changes, and by the time symptoms are obvious, time has often been lost.
- Existing pet cameras need the cloud, a monthly fee and raise privacy concerns; smart litter boxes only see litter use.

## Target users

| Who | Need | What PawWatch provides |
| --- | --- | --- |
| Working owners | Away all day, want to know the cat is fine | Daily log, anomaly notifications |
| Households with senior or chronically ill cats | Need long-term observation | 7-day trends, a daily report to bring to the vet |
| Veterinary clinics | Want to know how the cat is doing at home after surgery or before a follow-up | Objective eat / drink / litter records |
| Pet camera and litter box makers | Want AI features without paying cloud costs | Licensable edge software |

## Key features

1. **Eat / drink / litter log:** draw boxes around the food bowl, water bowl and litter box on screen; when the cat stays inside long enough, one visit is logged, with time and duration.
2. **Anomaly alerts:** push a notification when today's count differs a lot from the 7-day average, e.g. twice as many litter box visits as usual. It only prompts the owner to watch or see a vet; it does not diagnose.
3. **Forbidden-zone alarm:** play a sound and notify when the cat jumps onto the counter or dining table, or gets near cables.
4. **AI daily report:** turn the day's log into a plain-language summary, e.g. "Mochi drank water 6 times today, 2 more than usual."
5. **Dashboard:** one page with today's counts, a timeline and 7-day trends.

## Usage scenario

Nothing to do before leaving in the morning. In the afternoon the phone shows: "Mochi has used the litter box 9 times today; usually it's 4." After work the owner opens the dashboard, looks at the trend, decides to see the vet, and brings the daily report for the doctor.

## How it works

1. Each fixed camera streams over the home LAN to the host, which hands frames to the UGen300 to run YOLO cat detection.
2. The program determines which zone the cat is in and for how long, and produces events.
3. Events are stored in a local SQLite database; frames are discarded after use.
4. The dashboard, daily report and notifications are all generated from the event data.

## Hardware architecture

One host with a UGen300 receives streams from several fixed cameras over the home LAN; all computation happens on this host. The UGen300 is an accelerator card (M.2 or USB), not a standalone computer, and must be plugged into the host.

(The original doc embedded a hardware architecture diagram here: 3 cameras, 1 host.)

| Component | Role | Notes |
| --- | --- | --- |
| Fixed-lens network cameras ×N | Each points at one zone (food bowl, water bowl, litter box or forbidden zone) | Stream RTSP over the LAN; disable the vendor's cloud upload |
| Host (mini PC or single-board computer) | Receives streams, decodes, event logic, SQLite, dashboard | The UGen300 plugs into this |
| UGen300 (Hailo-10H) | Runs YOLO cat detection | The host passes frames to it for inference |
| Phone | Receives notifications, views the dashboard | Receives events only, never video |

### Why fixed cameras

- Zones are drawn in screen coordinates; with a fixed camera the zones stay aligned, so they're drawn once at install time.
- One camera per zone makes the target larger in frame, so detection is more accurate.
- Each camera has its own zone config file, and event records carry an extra "camera" field.
- Future extensions: preset positions for pan-tilt cameras (one zone set per angle), or automatic detection of bowl and litter box positions.

## Design principles

- **Privacy first:** store events only; never store or transmit video.
- **No monthly fee:** computation is local, so there's no cloud cost.
- **Works offline:** keeps logging when the internet is down.
- **Works out of the box:** the user only draws a few zones on screen.

## Current limitations

The MVP can't tell multiple cats apart, so multi-cat households get combined records. Individual identification is a future feature and shares its technology with street-cat TNR tracking.
