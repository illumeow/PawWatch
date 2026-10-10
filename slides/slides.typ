#import "template.typ": *

#let todo(body) = text(0.8em, fill: red)[TODO: #body]
// Citations: @R4 etc., keys from refs.yml; numbered [1], [2]... in order of first use
#show cite: set text(0.75em, fill: luma(100))
#let warn = red.darken(20%)
#show table: set par(leading: 0.5em)

#show: slides.with(
  title: "PawWatch",
  subtitle: "Edge-AI Cat Health Monitor",
  date: datetime.today().display("[year].[month].[day]"),
  authors: ("Jin-Yu Yang", "Zan-Yun Lee", "Wen-Hsiu Lin"),
  institution: [Department of Computer Science and Information Engineering, National Taiwan University],
  layout: "medium",
  ratio: 16 / 9,
  title-color: rgb("#b84722"),
)

#set par(leading: 0.7em, spacing: 1.1em)

= Problem

== Cat hides illness

// Dense slide: 90% text size so the whole argument fits on one page
#[
#set text(0.9em)

Cats instinctively hide pain and illness; obvious symptoms such as vomiting may appear only
when it is more severe @R1 @R2. Earlier signs show up in daily habits: vets list changes in appetite,
thirst and litter box use as warning signs @R2, and each common disease changes them in its own way:

#table(
  columns: (1.35fr, 2.7fr, 0.55fr, 0.6fr, 0.5fr),
  inset: 4pt,
  align: (left, left, center, center, center),
  [*Disease*], [*How common*], [*Eating*], [*Drinking*], [*Litter*],
  [Kidney disease], [Up to 30–40% of older cats may have it; only 3.6% are diagnosed @R4 @R5], [], [↑], [↑],
  [Hyperthyroidism], [8.7% of cats over 10 @R6 @R7], [↑], [↑], [↑],
  [Diabetes], [About 1 in 200 cats @R8 @R9], [↑], [↑], [↑],
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

Watching food, water and litter today takes several devices, brands and apps. 

#table(
  columns: (3.2fr, 0.6fr, 0.6fr, 0.6fr, 1fr),
  inset: 4pt,
  align: (left, center, center, center, center, center),
  [], [*Food*], [*Water*], [*Litter*], [*Video home*], 
  [Pet cameras (Furbo, Petcube) @C1 @C2 @C3], no, no, no, no,
  [Smart litter boxes (Petivity, Litter-Robot, PETKIT) @C4 @C5 @C6], no, no, yes, [–], 
  [Smart fountains (Felaqua Connect) @C7], no, yes, no, [–], 
  [Smart feeders (Petlibro Granary 2) @C11], yes, no, no, no, 
  [*PawWatch*], yes, yes, yes, yes, 
)
#text(0.8em)["Video home" = video stays at home]

However, illness shows up as a *combination*. For example, kidney disease raises both drinking and litter box use @R4,
so a water-only or litter-only device sees half the pattern.
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

== Why run AI at home, not in the cloud

#table(
  columns: (1.1fr, 1.6fr, 1.6fr),
  inset: 6pt,
  [], [*Cloud pet camera*], [*PawWatch*],
  [*Who sees your home video?*],
    [It's uploaded to the company's servers. At one home-camera maker, staff watched customers' private videos. @C8 @P3],
    [No one. Video never leaves home; only events like
     "14:32, drank for 25 s" are stored],
  [*Monthly fee*],
    [Smart features need a plan, typically US\$60–120/yr @C2 @C11],
    [None. No servers to pay for],
  [*Internet goes down*],
    [Some apps stop updating @C6],
    [Keeps logging; alerts are sent once it's back],
  [*Cat jumps on the counter?*],
    [Frames go to the server and back first],
    [The alarm sounds right away, from the box at home],
)

Running 24/7 is cheap: the AI accelerator draws 2.5 W, less than an LED bulb @C13.

= PawWatch System

== Architecture

#todo[system architecture diagram and technology overview]

// 8. Hardware architecture (required: hardware/software architecture)
== Hardware: one host, many fixed cameras
#todo[目前是 AI 生的]

#align(center)[
  #diagram(
    node-stroke: .1em,
    spacing: (2.5em, 1.2em),
    node((0, 0), "Camera: food"),
    node((0, 1), "Camera: water"),
    node((0, 2), "Camera: litter"),
    node((0, 3), "Camera: no-go"),
    node((2, 1.5), [Host + ASUS UGen300 \ (Hailo-10H)], name: <host>),
    node((4, 1.5), "Phone"),
    edge((0, 0), <host>, "-|>", [RTSP / LAN]),
    edge((0, 1), <host>, "-|>"),
    edge((0, 2), <host>, "-|>"),
    edge((0, 3), <host>, "-|>"),
    edge(<host>, (4, 1.5), "-|>", [events only]),
  )
]

- Fixed cameras: zones are drawn once; the cat is large in frame
- UGen300 is an M.2 / USB card in the host, not a standalone computer

// 9. Software pipeline (required: hardware/software architecture; feasibility 35%)
== Software: video in, events out
#todo[目前是 AI 生的]

#align(center)[
  #diagram(
    node-stroke: .1em,
    spacing: 2em,
    node((0, 0), "Frames"),
    edge("-|>"),
    node((1, 0), [YOLO cat detector \ (UGen300)]),
    edge("-|>"),
    node((2, 0), [Zones + dwell \ event logic]),
    edge("-|>"),
    node((3, 0), [SQLite \ events only]),
    edge("-|>"),
    node((4, 0), [Dashboard, report, \ alerts]),
  )
]

- Detector contract `(label, score, box)`: laptop backend today, Hailo backend is a swap
- Stock COCO YOLOv8, precompiled for Hailo-10H: no training, no conversion
- Frames are discarded after inference

// 10. Fits the chip (feasibility 35%, hardware integration award)
== The load fits the chip
#todo[目前是 AI 生的]

#table(
  columns: (1fr, 1fr),
  inset: 8pt,
  [Needed], [3 cameras × 5 fps = *15 inferences/s*],
  [Laptop (M3 Pro CPU, YOLOv8n 640)], [49 fps measured],
  [Hailo-10H (YOLOv8n)], [#todo[published fps, cite source]],
)

#todo[Stage II plan: port to UGen300, measure fps and power]

= Impact and Business

== Expected benefits

#todo[目前是 AI 生的]

- *Owners:* catch changes early instead of when symptoms are obvious
- *Vets:* objective at-home records after surgery or before a follow-up

#cols[
  #callout(title: "Without PawWatch", color: warn)[
    The cat uses the litter box twice as often while the owner is at work. Nobody notices
    until symptoms are obvious.
  ]
][
  #callout(title: "With PawWatch", color: green.darken(30%))[
    Litter box visits reach 2× the 7-day average: an alert the same day suggests watching
    the cat or seeing a vet, with the daily report in hand.
  ]
]

*Outcomes:* 
- Stage I, a working prototype on recorded video and open-source code on GitHub\;
- Stage II, the detector on the *UGen300* with measured fps and power.

== Market: more cats, older cats, growing pet tech

#todo[目前是 AI 生的, 感覺留下 more cats?]

#cols(ratio: (1fr, 1.25fr))[
  - *Taiwan:* 1.74 M cats, +33% in two years, now more than dogs @K-a
  - *Older cats:* Japan's average cat lifespan hit 15.79 years @K-d
  - *Pet tech:* US\$15.6 B (2025) → US\$52.9 B (2035), 12% a year; health is the largest segment @K-f
][
  #table(
    columns: (auto, 1fr, auto),
    inset: 5pt,
    [], [*Who*], [*Value / yr*],
    [TAM], [Global pet tech, health segment @K-f], [US\$4.4 B],
    [SAM], [Taiwan cat homes with a cat 7+: ≈ 460 k], [NT\$4.6 B],
    [SOM], [1% of SAM in 3 years: ≈ 4,600], [NT\$46 M],
  )
  #text(0.65em)[Assumptions: 1.5 cats per home → 1.16 M homes @K-a\; 40% have a cat 7+ (Japan proxy, 44%) @K-e\; NT\$10k per home (assumed); US\$1 ≈ NT\$32.]
]

Next: Taiwan → Japan (9 M cats) @K-d → US (53 M cat households) @K-c

== Business model: ride on hardware people already buy
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
- Today's kit: UGen300 US\$299 + host + 3 × \~US\$20 cameras ≈ US\$430–500 @C12 @C13 @C14 @C15

// 15. Roadmap + future work (business 35%: feasibility of the plan; innovation 30%)
== What's next: from prototype to product

#todo[目前是 AI 生的]

#cols(ratio: (1fr, 1fr, 1fr), gutter: 1em)[
  #callout(title: "Stage I (now)")[
    - Laptop prototype on recorded video
    - Visit log, anomaly alert, daily report, dashboard, no-go alarm
  ]
][
  #callout(title: "Stage II (11/6–12/4)")[
    - Port the detector to the UGen300
    - Measure fps and power
    - On-device LLM daily report
  ]
][
  #callout(title: "After the contest")[
    - Pilot with real cats at home
    - Multi-cat identification
    - Pan-tilt cameras; auto-detect bowls and litter box
    - Street-cat TNR tracking (ear tips)
  ]
]

== Code and references

#todo[其實應該可以全部丟 Appendix 吧]

*Code:* #link("https://github.com/illumeow/PawWatch")[github.com/illumeow/PawWatch]

*References:* numbered markers such as [1] on each slide refer to the full list in the appendix:
veterinary research and guidelines, product and price pages, and market data.

= Appendix


== Other

感覺能放一些截圖？或是前面放不下的圖表 blah blah blah

== References

#set text(0.7em)
#set par(leading: 0.55em, spacing: 0.8em)
#columns(2, gutter: 1.2em, bibliography("refs.yml", style: "ieee"))
