#import "template.typ": *

#let todo(body) = text(0.8em, fill: red)[TODO: #body]
// Citations: @R4 etc., keys from refs.yml; numbered [1], [2]... in order of first use
#show cite: set text(0.75em, fill: luma(100))
#let warn = red.darken(20%)
// Cross-reference to another slide: #see(<problem>)[Problem] -> "see Problem, p. 3", linked
#let see(target, name) = link(target)[see #name, p. #context counter(page).at(target).first()]
#show table: set par(leading: 0.5em)

#show: slides.with(
  title: "PawWatch",
  subtitle: "Edge-AI Cat Health Monitor",
  date: [#link("https://github.com/illumeow/PawWatch")[#box(baseline: 0.15em, image("images/github.svg", height: 1em))#h(0.3em)GitHub Repo]],
  authors: ("Jin-Yu Yang", "Zan-Yun Lee", "Wen-Hsiu Lin"),
  institution: [Department of Computer Science and Information Engineering, National Taiwan University],
  layout: "medium",
  ratio: 16 / 9,
  title-color: rgb("#b84722"),
)

#set par(leading: 0.7em, spacing: 1.1em)

= Problem

== Cat hides illness <problem>

// Dense slide: 90% text size so the whole argument fits on one page
#[
#set text(0.9em)

Cats instinctively hide pain and illness; obvious symptoms such as vomiting may appear only
when it is more severe @R1 @R2. Earlier signs show up in daily habits: vets list changes in appetite,
thirst and litter box use as warning signs @R2, and each common disease changes them in its own way:

#table(
  columns: (1.35fr, 2.7fr, 0.55fr, 0.6fr, 0.5fr),
  inset: 4pt,
  align: (left, left, center + horizon, center + horizon, center + horizon),
  [*Disease*], [*How common*], [*Eating*], [*Drinking*], [*Litter*],
  [Kidney disease], [Up to 30–40% of older cats may have it; only 3.6% are diagnosed @R4 @R5], [], [↑], [↑],
  [Hyperthyroidism], [8.7% of cats over 10 @R6 @R7], [↑], [↑], [↑],
  [Diabetes], [About 1 in 200 cats @R8], [↑], [↑], [↑],
  [Urinary tract disease], [A leading reason cats visit vets @R10], [], [], [↑],
)

A 2026 study of 136 cats found those with kidney disease used the litter box about twice as often,
even in early stages @R11. A blocked urinary tract may kill within 24–48 hours; its first sign is many litter box trips @R10.
]

= Solution

// Existing solutions (innovation 30%): why PawWatch when smart devices exist
== Today's smart devices each watch one spot

// Dense slide: 90% text size so the table fits on one page
#[
#set text(0.9em)
#let yes = text(font: "DejaVu Sans", fill: green.darken(30%))[✓]
#let no = text(font: "DejaVu Sans", fill: warn)[✗]

Each smart device on the market watches one spot, so watching food, water and litter takes several devices and apps.

#table(
  columns: (3fr, 0.7fr, 0.7fr, 0.7fr),
  inset: 4pt,
  align: (left, center, center, center),
  [], [*Food*], [*Water*], [*Litter*],
  [Smart feeders], yes, no, no,
  [Smart water fountains], no, yes, no,
  [Smart litter boxes], no, no, yes,
  [Pet cameras (video only, no visit log)], no, no, no,
  [*PawWatch*], yes, yes, yes,
)

However, illness shows up as a *combination*. For example, kidney disease raises both drinking and litter box use @R4,
so a water-only or litter-only device sees half the pattern. Once set up, PawWatch watches all three spots with
one box, and the video never leaves home.
]

== Solution: PawWatch

Owners are out all day, and no single device sees the whole pattern.
*PawWatch* is a vision-based monitoring system: low-cost cameras watch the
food bowl, water bowl and litter box, and an on-device AI accelerator
recognizes the cat and logs every visit. Video never leaves home.

#v(0.5em)

#align(center)[
  #diagram(
    node-stroke: .1em,
    spacing: 1.8em,
    node((0, 0), [Cameras \ food · water · litter]),
    edge("-|>"),
    node((1, 0), [On-device AI \ detects the cat]),
    edge("-|>"),
    node((2, 0), [Visit log]),
    edge("-|>"),
    node((3, 0), [Alerts & \ daily report]),
  )
]

#v(0.5em)

#cols[
  *What it records*
  - *Visit log:* how often and how long the cat eats, drinks and uses the litter box
  - *No-go zone alarm:* plays a sound when the cat jumps onto the counter
][
  *What it tells you*
  - *Anomaly alert:* $>=$ 2 or $<= 1/2$ times of the cat's 7-day average
  - *Daily report:* a plain-language summary
  - *Dashboard:* today's counts, timeline and 7-day trends
]

== Why run AI at home, not in the cloud <why-edge>

#table(
  columns: (1.1fr, 1.6fr, 1.6fr),
  inset: 6pt,
  [], [*Cloud pet camera*], [*PawWatch*],
  [*Who sees your home video?*],
    [It's uploaded to the company's servers. At one home-camera maker, staff watched customers' private videos @P3],
    [No one. Video never leaves home; only events like
     "14:32, drank for 25 s" are stored],
  [*Monthly fee*],
    [Smart features usually need a paid subscription],
    [None. No servers to pay for],
  [*Internet goes down*],
    [Cloud features stop until it's back],
    [Keeps logging; alerts are sent once it's back],
  [*Cat jumps on the counter?*],
    [Frames go to the server and back first],
    [The alarm sounds right away, from the box at home],
)

Running 24/7 is cheap: the AI accelerator draws 2.5 W, less than an LED bulb @C13.

= PawWatch System

// Architecture (required: hardware/software architecture; feasibility 35%)
== Architecture: video in, events out

#align(center)[
  #set text(0.85em)
  #diagram(
    node-stroke: .1em,
    spacing: (3.4em, 1.1em),
    node((-0.3, 0), [Fixed \ cameras], name: <cam>),
    edge("-|>", [frames]),
    node((1, 0), [YOLO cat detector \ on UGen300], name: <det>),
    edge("-|>", [cat box]),
    node((1.9, 0), [Zone + dwell \ logic], name: <logic>),
    edge("-|>", [visits]),
    node((2.8, 0), [SQLite \ events only], name: <db>),
    node((1.9, 1), [Alarm sound], name: <alarm>),
    edge(<logic>, <alarm>, "-|>", [no-go zone], label-side: left),
    node((2.8, 1), [Dashboard, \ report, alerts], name: <out>),
    edge(<db>, <out>, "-|>"),
    node((1.8, -0.75), text(fill: luma(90))[Home host + ASUS UGen300], stroke: none, name: <hostlabel>),
    node(enclose: (<det>, <logic>, <db>, <out>, <alarm>, <hostlabel>), stroke: (paint: luma(120), dash: "dashed"), inset: 5pt),
    node((4, 1), [Phone], name: <phone>),
    edge(<out>, <phone>, "-|>", [#set par(leading: 0.4em); events \ only]),
  )
]

#[
#set text(0.85em)
- *Detect:* the host decodes each camera's video and the UGen300 runs a stock YOLO model that finds the cat.
  Frames live only in memory and are dropped after inference; nothing saves or uploads them.
- *Turn boxes into visits:* the cat's box is matched to the zones drawn for that camera (food, water, litter, no-go),
  and a visit is logged once the cat stays long enough. A no-go zone rings the alarm right away.
- *Store and report:* each visit is one row in a local SQLite database. The dashboard, anomaly alert and daily report
  read only these rows, so the only thing that can leave the home is an event like "07:30, ate for 31 s".
]

== Hardware: one host, many fixed cameras

#cols(ratio: (1fr, 1.15fr), gutter: 1em)[
  #v(0.5em)
  #align(center)[
    #set text(0.8em)
    #diagram(
      node-stroke: .1em,
      spacing: (2.2em, 0.9em),
      node((0, 0), "Camera: food", width: 7.5em),
      node((0, 1), "Camera: water", width: 7.5em),
      node((0, 2), "Camera: litter", width: 7.5em),
      node((0, 3), "Camera: no-go", width: 7.5em),
      node((1.6, 1.5), [Host \ + UGen300], name: <host>),
      node((1.6, 3.2), "Phone", name: <phone>),
      edge((0, 0), <host>, "-|>"),
      edge((0, 1), <host>, "-|>"),
      edge((0, 2), <host>, "-|>"),
      edge((0, 3), <host>, "-|>"),
      edge(<host>, <phone>, "-|>", [events only], label-side: left),
    )
  ]
][
  #set text(0.85em)
  We mount *fixed cameras*, one at each spot we watch: the food bowl, the water bowl, the litter box and any no-go spot
  such as the kitchen counter. Each camera streams its video over the home network to *one small host computer*
  (a mini PC or Raspberry Pi).

  The *ASUS UGen300* is plugged into the host over USB or M.2. The host decodes the video and hands frames to the
  UGen300, whose Hailo-10H chip (40 TOPS at 2.5 W @C13) runs the cat detector. The host then turns detections into
  visits, stores them and serves the dashboard. Only these events reach the owner's phone.
]

#[
#set text(0.85em)
*Why fixed cameras:* zones are drawn in pixels, so a camera that never moves needs them drawn only once, at setup.
One camera per spot also keeps the cat large in the frame, which makes detection reliable.
]

// Detection-window screenshot without its bottom caption band (`band` = share of the image height)
#let window-shot(path, height, band) = box(height: height * (1 - band), clip: true, align(top, image(path, height: height)))
// Dashboard screenshot without its blank top margin (`top` = share of the image height)
#let crop-top(path, height, top) = box(height: height * (1 - top), clip: true, move(dy: -height * top, image(path, height: height)))

== Detection: from pixels to "the cat is at the bowl"

#cols(ratio: (1.5fr, 1fr), gutter: 1em)[
  #set text(0.85em)
  *A stock YOLO model, no training.* We use YOLOv8n pretrained on the public COCO dataset, which already has a
  "cat" class. We keep only that class (score $>=$ 0.4). No cat photos were collected and no model was trained or
  fine-tuned, so any home can use it out of the box.

  *Zones are drawn once.* At setup, the owner clicks a polygon around each spot on a still frame
  (`draw_zones.py`); it is saved as one small JSON file per camera.

  *Which zone is the cat in?* We take the highest-scoring cat box and measure how much of it overlaps each zone,
  as a share of the #underline[smaller] of box and zone. The zone with the most overlap wins, if it reaches 20%.
  Measuring against the smaller shape lets a zone hug a small bowl, and a box that only grazes a zone's edge doesn't count.
][
  #figure(
    window-shot("images/detect_eat.jpg", 6.4cm, 0.045),
    caption: text(0.7em)[Detection window: cat box, food zone and visit count],
    supplement: none,
    numbering: none,
  )
]

// Small sketch of the visit rules: one square per sampled frame
#let sample-strip(pattern) = {
  let cell(c) = box(
    width: 0.42em,
    height: 0.9em,
    fill: if c == "#" { rgb("#eb6834") } else { luma(225) },
  )
  stack(dir: ltr, spacing: 1pt, ..pattern.clusters().map(cell))
}

== Event logic: from detections to visits

#[
#set text(0.85em)
The event logic is pure code: it takes $"(video time, zone)"$ pairs and returns visits, so it is tested without a model
or video. Timestamps are *video time* (recording start + frame offset), so recorded footage replays exactly.

#align(center)[
  #grid(
    columns: (auto, auto),
    column-gutter: 0.8em,
    row-gutter: 0.4em,
    align: (right + horizon, left + horizon),
    text(0.85em)[Frames (cat in zone)],
    sample-strip("....##############.....############################......"),
    text(0.85em)[Logged visit],
    stack(dir: ltr, h(4 * (0.42em + 1pt)), box(width: 46 * (0.42em + 1pt) - 1pt, height: 0.9em, fill: rgb("#eb6834"), radius: 2pt, align(center + horizon, text(0.75em, fill: white)[one visit: the 5-frame gap is bridged]))),
  )
]

#table(
  columns: (auto, 1fr),
  inset: 4pt,
  align: (horizon, ),
  [*Minimum dwell*], [A visit counts after 5 s in one zone, so walking past a bowl isn't a meal.\ No-go zones need only 1 s: a quick jump still counts.],
  [*Gap tolerance*], [The cat may vanish for up to 5 s (turning, hidden by the litter box rim) without splitting one visit into two.],
  [*Live writes*], [A visit is stored as soon as it qualifies and its end moves forward while the cat stays, so the dashboard follows a live camera.],
  [*Alarm*], [Every frame in a no-go zone calls the alarm at once; a 30 s cooldown gives one sound per jump, not per frame.],
)
]

== Storage and outputs: what the owner sees

#cols(ratio: (1.35fr, 1fr), gutter: 1em)[
  #set text(0.8em)
  *One table is the whole record.* Each visit is one row in local SQLite:
  `camera, zone, start, end, duration, simulated`. A second table logs when each camera was recording, so hours
  with the camera off are never read as "didn't drink".

  *Anomaly alert.* For each of food, water and litter, today's count is compared with the cat's own average over the
  previous 7 days, #underline[over the same hours], so a normal morning isn't flagged for a missing dinner. An alert needs both $>= 2$  or $<= 0.5$ times the average #underline[and] a difference of at least 3 visits, so 1 vs. 0 is not an alert.

  *Daily report and alarm.* Template sentences turn the counts into plain language. Wording suggests watching the cat
  or seeing a vet, never a diagnosis. No-go jumps play a sound on the host and can send a text message (never a frame).
][
  #figure(
    crop-top("images/dashboard_real_day.png", 6.6cm, 0.085),
    caption: text(0.7em)[Dashboard: today's counts, timeline, 7-day trend],
    supplement: none,
    numbering: none,
  )
]

= Impact and Business

// Expected benefits (required by the rules): one page each for the cat, the owner, and vets + broader
== Benefits for the cat: problems caught early, a safer home

// Dense slide: 85% text size so both columns fit on one page
#[
#set text(0.85em)

// Side note: plain gray rule, quieter than a callout
#let note(title, body) = block(
  inset: (left: 0.8em, y: 0.3em),
  stroke: (left: 1.5pt + luma(180)),
  text(fill: luma(70))[#text(weight: "bold", title) \ #body],
)

#cols[
  *Catch problems early*
  - *Early signs of many diseases*: appetite, thirst and litter use change before obvious symptoms

  - *Emergencies in hours, not days*: an urgent change shows up in that evening's report, not after days of guessing
][
  *A safer, calmer home*
  - *No-go zones*: an alarm scares the cat off, and the owner gets a LINE or Discord text right away

  - *Less stress*: the cat is observed at home, unhandled, so the record shows its normal behavior
]

#v(5em)

#note[Example: the litter box][
  Kidney disease doubles litter use even at early stages @R11, yet most cases go undiagnosed @R4 @R5.
  Found early, it is treatable: a kidney diet cut uremic crises from 26% to 0% in a 45-cat trial @R12.
  A blocked urethra also shows as many litter box trips, and can kill within 24–48 hours @R10
]
]

== Benefits for the owner: rest assured, wherever you are

// Dense slide: 85% text size so both columns fit on one page
#[
#set text(0.85em)

#cols(ratio: (1.15fr, 1fr))[
  - *Peace of mind:* at work, on a business trip or in hospital, the cat is watched all day. Alerts reach the phone over LINE or Discord.

  - *Facts instead of guesses:* 55.5% of owners did not recognize more thirst as a sign of dehydration @R17. PawWatch counts every visit for them.

  - *One box, no subscription:* costs less than most products on the market. Pay once rather than subscribe monthly.

  - *Privacy:* video never leaves home.
][
  *Earlier is cheaper*
  #callout(title: "Caught early", color: green.darken(30%))[
    A senior cat check-up: NT\$3,000–8,000 @C16
  ]
  #callout(title: "Caught late", color: warn)[
    Emergency treatment can cost NT\$30,000 or more at a 24-hour hospital @C15
  ]
]
]

== Benefits for vets and beyond

// Dense slide: 85% text size so both columns fit on one page
#[
#set text(0.85em)

#cols[
  *Vets*
  - *A complete history*: a dated, detailed record can facilitate diagnosis

  - *Recovery after treatment*: home data tracks recovery status
][
  *Resources*
  - *Low power*: all-day watching costs little energy

  - *No internet demand*: Everything runs locally (except Discord / Line alerts and records)
]
]
//

// *Outcomes:* 
// - Stage I, a working prototype on recorded video and open-source code on GitHub\;
// - Stage II, the detector on the *UGen300* with measured fps and power.

// Bottom-up TAM / SAM / SOM in Taiwan: households × kit price, arithmetic shown beside each tier
== Market: 266k Taiwan homes with an older cat <market>

#let tier(width, shade, name, homes, value) = context align(center, block(
  width: width,
  inset: (y: 0.6em),
  radius: 3pt,
  fill: accent.get().lighten(shade),
  text(0.9em, fill: white)[*#name* · #homes homes · *#value*],
))

#grid(
  columns: (1.1fr, 1fr),
  column-gutter: 1.2em,
  row-gutter: 1em,
  align: horizon,
  tier(100%, 0%, "TAM", [1.02~M], [NT\$10.2~B]),
  [9.85 M households @K-c × 10.4% keep cats @K-b],
  tier(80%, 20%, "SAM", [266~k], [NT\$2.7~B]),
  [× 26% of dogs and cats are 7 or older @K-d: the age when chronic disease becomes common],
  tier(60%, 40%, "SOM", [5.3~k], [NT\$53~M]),
  [× 2% of SAM reached in years 1–3 (our assumption)],
)

#v(1em)

- *Price:* NT\$10,000 per kit, a working assumption (#see(<business-model>)[Business model])
- *Sanity check:* the SOM is about one kit per animal hospital per year (about 1,800 hospitals @K-e)
- *Tailwind:* 1.74 M pet cats, up 33% in two years @K-a; global pet tech may grow from US\$15.6 B (2025)
  to US\$52.9 B (2035) @K-f


== Business model: ride on hardware people already buy <business-model>
#todo[目前是 AI 生的, 完全不知道這啥]

#table(
  columns: (1.2fr, 1.6fr, 0.9fr),
  inset: 6pt,
  [*Customer*], [*Offer*], [*Revenue*],
  [Device makers (pet cameras, home hubs, PCs with edge AI)], [PawWatch edge software on their hardware: no cloud cost for them], [Per-unit license],
  [Vet clinics], [At-home monitoring kits after surgery and for chronic cases (e.g. kidney disease)], [Monthly rental per kit],
  [Cat owners], [Box + cameras, no subscription], [One-time purchase],
)

- Licensing spreads the UGen300 cost: it doesn't land on one product
- One UGen300 serves every camera in the home, so each extra spot is only a camera

= Appendix


== Detection screenshots

#let shot(path, band, caption) = figure(
  window-shot(path, 4.4cm, band),
  caption: text(0.7em, caption),
  supplement: none,
  numbering: none,
)

#align(center + horizon)[
  #grid(
    columns: 3,
    column-gutter: 0.8em,
    align: bottom,
    shot("images/detect_litter.jpg", 0.078)[Tangerine in the litter zone],
    shot("images/detect_drink_ami.jpg", 0.045)[Ami at the water bowl],
    shot("images/detect_bed_alarm.jpg", 0.052)[No-go zone: box turns red, alarm rings],
  )
]

Each window shows the cat box with its score, the camera's zones and the visits counted so far. The windows
are only displayed; frames are never written to disk.

== Dashboard with an anomaly alert (simulated data)

#cols(ratio: (1fr, 1.1fr))[
  #set text(0.85em)
  This dashboard runs on *simulated* data only, to show what an alert looks like: a day where the litter box
  count reaches at least twice the cat's 7-day average.

  The alert names the change and the usual count, and suggests keeping an eye on the cat or seeing a vet.
  It never names a disease.
][
  #figure(
    crop-top("images/dashboard_real_day.png", 6.6cm, 0.085),
  )
]

== References

#set text(0.7em)
#set par(leading: 0.55em, spacing: 0.8em)
#columns(2, gutter: 1.2em, bibliography("refs.yml", style: "ieee"))
