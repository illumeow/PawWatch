#import "template.typ": *

// Stage I proposal deck, due 2026-10-14. Official rules:
// - English, max 20 content pages (appendix not counted).
// - Must cover: context and problem, solution (tools, tech, method),
//   hardware/software architecture, expected benefits, references + GitHub link.
// - Scoring: innovation 30%, business potential and feasibility 35%,
//   practical value 25%, storytelling and visuals 10%.
// Each slide below notes the criterion it serves. Red TODOs are placeholders.

#let todo(body) = text(0.8em, fill: red)[TODO: #body]

#show: slides.with(
  title: "PawWatch",
  subtitle: "Edge-AI Cat Health Monitor",
  date: datetime.today().display("[year].[month].[day]"),
  authors: ("illumeow", "meander", "Wen-Hsiu, Lin"),
  institution: [Department of Computer Science and Information Engineering, National Taiwan University],
  layout: "medium",
  ratio: 16 / 9,
  title-color: none, // e.g. rgb("#c2410c") to change the accent color
)

// 1. Hook (storytelling 10%)
#focus[Would you notice if your cat \ drank twice as much water today?]


// 2. Problem (required: context and problem; practical value 25%)
== Cats hide illness

- Cats instinctively hide pain and illness
- Changes in eating, drinking and litter use are often the earliest signs
- Owners are at work all day and can't see these changes
- By the time symptoms are obvious, time has been lost

#todo[1–2 vet or research sources, e.g. urinary / kidney disease and litter frequency]

// 3. Existing solutions (innovation 30%)
== Existing solutions fall short

#table(
  columns: (1.4fr, 1fr, 1fr, 1fr, 1fr),
  inset: 8pt,
  align: center + horizon,
  [], [Eat / drink / litter], [No cloud], [No monthly fee], [No-go zone alarm],
  [Pet cameras], [–], [✗], [✗], [–],
  [Smart litter boxes], [Litter only], [–], [–], [✗],
  [*PawWatch*], [✓], [✓], [✓], [✓],
)

#todo[check each cell against 2–3 real products; name them in References]


// 4. Solution (required: solution; practical value 25%)
== PawWatch: one box watches food, water, litter and no-go zones

#cols[
  + *Visit log:* cat stays in a zone long enough → one visit, with time and duration
  + *Anomaly alert:* today vs. 7-day average ("2× litter visits")
  + *No-go zone alarm:* sound + notification on counter or table
  + *Daily report:* plain-language summary to bring to the vet
  + *Dashboard:* today's counts, timeline, 7-day trend
][
  #callout(title: "Never a diagnosis")[
    Alerts suggest watching the cat or seeing a vet.
  ]
  #todo[product photo or hero image]
]

// 5. Usage scenario (storytelling 10%, practical value 25%)
== A day with PawWatch

#todo[timeline graphic: morning (nothing to set up) → 15:00 phone alert
  "Tangerine used the litter box 9 times today; usually 4" → evening dashboard
  → vet visit with the daily report]

// 6. Demo screenshots (feasibility 35%)
== It works today

#cols[
  #todo[detection screenshot from A: boxes, zones, count, red alarm box]

  Caption: "Running on laptop · YOLOv8n · target: ASUS UGen300"
][
  #todo[dashboard + daily report screenshot from B]

  7-day history is *simulated*; today is real footage.
]

Demo video: #todo[YouTube unlisted link]


// 7. Hardware architecture (required: hardware/software architecture)
== Hardware: one host, many fixed cameras

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

// 8. Software pipeline (required: hardware/software architecture; feasibility 35%)
== Software: video in, events out

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

// 9. Fits the chip (feasibility 35%, hardware integration award)
== The load fits the chip

#table(
  columns: (1fr, 1fr),
  inset: 8pt,
  [Needed], [3 cameras × 5 fps = *15 inferences/s*],
  [Laptop (M3 Pro CPU, YOLOv8n 640)], [49 fps measured],
  [Hailo-10H (YOLOv8n)], [#todo[published fps, cite source]],
)

#todo[Stage II plan: port to UGen300, measure fps and power]

// 10. Why edge (innovation 30%)
== Why on the edge

#cols[
  - *Privacy:* video never leaves the home; only events are stored
  - *No monthly fee:* no cloud compute
][
  - *Works offline:* keeps logging when the internet is down
  - *Low power:* #todo[Hailo-10H power figure, cite]
]

#todo[proof shots: airplane mode while running; DB rows with no images]


// 11. Expected benefits (required: expected benefits; practical value 25%)
== Expected benefits

- Owners: catch changes early instead of when symptoms are obvious
- Vets: objective at-home records after surgery or before a follow-up
- Lower cost: fewer emergency visits #todo[source for cost of late vs. early care]

// 12. Market (business 35%)
== Market

#todo[number of pet cats in Taiwan (cite)]

#todo[global pet tech / smart pet device market size and growth (cite)]

#todo[TAM / SAM / SOM, or a simple bottom-up estimate]

// 13. Business model (business 35%: the most important slide)
== Business model

#table(
  columns: (1fr, 1.4fr, 1.2fr),
  inset: 8pt,
  [Customer], [Offer], [Revenue],
  [Pet camera and litter box makers], [Licensed edge software], [Per-unit license],
  [Vet clinics], [At-home monitoring after surgery or for chronic cases], [Rental / clinic plan],
  [Owners], [Box + cameras, no subscription], [One-time purchase],
)

#todo[pricing, unit cost (host + UGen300 + cameras), go-to-market: which customer first]

// 14. Roadmap (business 35%: feasibility of the plan)
== Roadmap

#todo[Stage I (now): laptop prototype · Stage II (11/6–12/4): UGen300 port, on-device
  LLM daily report · Later: multi-cat ID, vet clinic pilot]

// 15. Future work (innovation 30%)
== Future work

- Multi-cat identification: which cat ate from which bowl
- Street-cat TNR tracking (ear-tip recognition), same technology
- Pan-tilt cameras with preset positions; auto-detect bowls and litter box
- On-device LLM daily report on the UGen300

// 16. Team, references, GitHub (required: references + GitHub link)
== Team, references and code

#cols[
  *Team*
  - meander: vision pipeline
  - illumeow: dashboard, alerts, report
  - Wen-Hsiu, Lin: research, slides

  *Code:* #todo[public GitHub link]
][
  *References*
  #todo[vet / research sources, market data, Hailo benchmark, competitor products]
]

#focus[PawWatch \ #text(0.6em)[Video never leaves the box.]]
