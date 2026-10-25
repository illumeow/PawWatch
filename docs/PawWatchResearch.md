# PawWatch slides: research notes

Working notes for the Stage I deck (`slides/slides.typ` on branch `feat/slides`, due 2026-10-14).
We collect broadly first, then filter. Only put claims on slides that have a source here.

Status:
- [x] Step 1: Motivation (narrative below, sections M1–M3)
- [x] Step 2: Existing solutions / competitors (slide 3), sections E1–E3
- [x] Step 3: Market (slide 13), sections K1–K4
- [x] Step 4: Business model (slide 14), first draft; cost of late care (slide 12) not done
- [ ] Step 5: write into `slides.typ`, all sources on slide 16 References

Decisions so far:
- Drop the "1/3 of cats don't see a vet yearly" stat (2008, too old).
- Highlight urethral obstruction (can kill in < 24–48 h) as a red callout on slide 2b (not a separate focus slide).
- CKD: show both numbers (estimated 30–40% vs. diagnosed 3.6%).
- Differentiation story = **disease patterns need integration** (D1) + **nothing new for the cat** (D2). Other points (privacy, no subscription, cost, offline, no-go) are supporting; still deciding which to keep.
- "Cheaper" is not claimed up front; use "no subscription" and "extra spot = ~$20 camera".

---

## Deck outline (proposed, pending team OK)

Change vs. current `slides.typ`: move "Existing solutions" **after** the product intro. Reason: "why PawWatch when products exist" only makes sense once the audience knows what PawWatch does, and D1/D2 compare against our features.

| # | Slide | Story beat | Content source |
|---|---|---|---|
| 1 | Hook | "Would you notice if your cat drank twice as much water today?" | existing |
| 2 | Cats hide illness | Problem | M1 |
| 3 | Behavior is the early warning | Behavior ↔ disease; red callout: urethral obstruction | M2 |
| 4 | PawWatch: one box watches every spot | Solution: features (visit log, anomaly alert, no-go alarm, daily report, dashboard) | existing slide 4 + M3 bridge |
| 5 | A day with PawWatch | Scenario | existing |
| 6 | Why PawWatch, when smart devices exist? | (a) disease = a pattern across spots → only integration sees it (D1); (b) nothing new for the cat (D2); (c) supporting points TBD | E1, E4 |
| 7 | It works today | Demo screenshots | existing |
| 8–11 | Hardware, software, fits the chip, why edge | Tech | existing (+ D3–D6 on "why edge") |
| 12 | Expected benefits | | existing |
| 13 | Market | | Step 3 |
| 14 | Business model | | existing + Step 4 |
| 15 | Roadmap | | existing |
| 16 | Future work | | existing |
| 17 | Team, references, code | | all refs |
| 18 | Closing | "Video never leaves the box." | existing |

18 pages ≤ 20 limit.

### Slide 6 draft: Why PawWatch, when smart devices exist?

Left: **Today** — a smart feeder, a smart fountain, a smart litter box, a camera: 4 devices, 4 apps, each sees one spot. [C1, C4, C7, C11]
Right: **PawWatch** — one box sees the whole pattern.

| Disease | Pattern | Single-spot device sees |
|---|---|---|
| Kidney disease | drinking ↑ + urinating ↑ | half |
| Diabetes | eating ↑ + drinking ↑ + urinating ↑ | a third |
| Hyperthyroidism | eating ↑ (+ drinking ↑) | part |

Bottom line: **Nothing new for your cat**: keeps its own bowl and litter box; smart boxes need days to weeks of acclimation. [P1, P2]

---

## Narrative (motivation)

| # | Point we want the audience to take away | Section | Slide (proposed) |
|---|---|---|---|
| 1 | Cats hide pain and illness | [M1](#m1-cats-hide-illness) | 2 "Cats hide illness" |
| 2 | But their behavior changes: eating, drinking and litter use reflect disease, and this is measurable | [M2](#m2-behavior-reflects-disease) | 2b (new) "Behavior is the early warning" |
| ★ | Highlight: a blocked urinary tract shows up as frequent litter trips and can kill in under 48 h | [M2.4](#m24-highlight-urethral-obstruction) | focus slide or red callout on 2b |
| 3 | So we monitor these behaviors continuously at home, instead of relying on owners' eyes or 6-monthly check-ups | [M3](#m3-so-continuous-home-monitoring) | bridge into slide 4 (Solution) |

Slide count: the deck has 16 pages now; adding 2b (+ an optional focus slide) keeps it ≤ 20.

---

## M1. Cats hide illness

**Claim for slide:** Cats instinctively hide pain and illness, so problems are noticed late.

| Finding | Source |
|---|---|
| Cats are notorious for hiding pain and are often undertreated (fewer painkillers than dogs). This motivated the Feline Grimace Scale. | [R1] Evangelista et al., *Sci Rep* 2019; reported by [Univ. of Calgary news, 2020](https://ucalgary.ca/news/cats-faces-reveal-their-hidden-pain) |
| Cats tend to stay quiet when something is wrong; the behavior comes from wild ancestors avoiding showing weakness to predators. It delays care. | [R2] [VCA Animal Hospitals](https://vcahospitals.com/resources/conditions-cat/recognizing-signs-of-illness-in-your-cat) |
| Obvious signs (vomiting, breathing changes) tend to appear only when illness is more severe. | [R2] |

Best single citation: R1 (peer-reviewed). R2 adds the "why" (prey instinct).

---

## M2. Behavior reflects disease

**Claim for slide:** The earliest visible signs of common cat diseases are changes in eating, drinking and litter box use, exactly what PawWatch logs.

### M2.1 Vets name these behaviors as the warning signs

| Finding | Source |
|---|---|
| Warning signs to watch: more or less appetite or thirst, more time in the litter box, more or less urine than usual. | [R2] VCA |
| 77-week study of 32 cats: the 3 most common sickness behaviors were vomiting, eliminating outside the litter box and eating less (78–88% of all sickness behaviors). | [R3] Stella, Lord & Buffington, *JAVMA* 2011; [OSU news](https://news.osu.edu/even-healthy-cats-act-sick-when-their-routine-is-disrupted/) |

Note on R3: the study is about stress triggering sickness behaviors, not about diseases. Use it only for "these are the behaviors that show a cat is unwell", not for "these predict disease".

### M2.2 Each behavior maps to common diseases (with numbers)

| Behavior PawWatch logs | Disease | How common | How often the sign appears | Source |
|---|---|---|---|---|
| Drinking ↑, urinating ↑ | Chronic kidney disease (CKD) | May affect ≥30–40% of cats over 10; leading cause of death in UK cats 5+ (>13% of deaths) | PU/PD is listed as a sign that should trigger CKD investigation | [R4] ISFM guidelines 2016 |
| | | Diagnosed: 3.6% of cats 9+ in UK practices (more conservative) | | [R5] Conroy et al. 2019 |
| Eating ↑ (with weight loss), drinking ↑ | Hyperthyroidism | 8.7% of cats aged 10+ | In 462 untreated cats: increased appetite 55%, PU/PD 33%, weight loss 92% | [R6] Stephens et al. 2014; [R7] Peterson et al. 2016 |
| Drinking ↑, urinating ↑, eating ↑ | Diabetes | 0.58% (≈1 in 200), mostly older cats | Classic triad | [R8] O'Neill et al. 2016; [R9] Merck Animal Health |
| Litter visits ↑, straining | Lower urinary tract disease (FLUTD) | A leading reason cats visit vets | More frequent urination attempts is a core sign | [R10] Cornell Feline Health Center |

CKD numbers: **decided to show both** as a contrast.
- Estimated: may affect up to 30–40% of cats over 10 [R4]
- Diagnosed: only 3.6% of cats 9+ have a CKD diagnosis in UK practice records [R5]
- Wording rule: no source says "the gap = undiagnosed cats", so present it as our reading, e.g. "Estimated vs. diagnosed: many cases may never be caught." Keep "may". Also note the age cutoffs differ (10+ vs. 9+) and the populations differ; say "older cats" on the slide, keep exact ages in the citation.
- Slide line: **"Up to 30–40% of older cats may have kidney disease [R4]. Only 3.6% are diagnosed [R5]."**

### M2.3 Measured evidence: litter box data separates CKD cats (strongest support)

[R11] Langenfield-McCoy et al., "Enhancing Detection of Chronic Kidney Disease Through Smart Litter Box Monitoring", *Animals* 2026; 16(9):1319 (Purina + Ohio State). [Paper](https://www.mdpi.com/2076-2615/16/9/1319) · [Press release](https://newscenter.purina.com/2026-08-31-Feline-Elimination-Patterns-Linked-to-Kidney-Disease-Demonstrated-Through-Smart-Litter-Box-Monitor)

- 136 cats, smart litter box with load sensors + ML.
- CKD cats urinated about **twice as often** (4.6 vs. 2.3 events/week, p < 0.001) and produced about twice the urine weight (1007 vs. 470 g over 7 days).
- These differences were already visible in early CKD (IRIS stages 1–2).
- Model: weighted F1 ≈ 90% on validation.
- Caveats: small CKD group (13 train, 7 validation); authors say it is a screening aid, not a diagnostic tool; it did not test detection timing against diagnosis.

Slide line: "A 2026 study found cats with kidney disease visit the litter box twice as often, already in early stages." [R11]

Also relevant for Step 2: this is a competitor (litter only, load sensors). PawWatch covers food + water + litter with one camera system.

### M2.4 Highlight: urethral obstruction

| Finding | Source |
|---|---|
| A blocked urinary tract is "an absolute emergency"; the cat passes little or no urine. | [R10] Cornell |
| Time from complete obstruction to death may be **less than 24–48 hours**. Male cats are at higher risk. | [R10] Cornell |
| Sign PawWatch can catch: many litter box visits in a short time. | [R10] (frequent urination attempts) |

Slide idea: a `#focus[...]` slide or a red callout:
> **A blocked cat can die within 48 hours.** The first sign: many short trips to the litter box. [R10]

This also gives the best demo story: "Tangerine used the litter box 9 times today; usually 4" (already in slide 5).

---

## M3. So: continuous home monitoring

**Claim for slide:** Owners are away all day and check-ups are months apart; behavior needs to be watched continuously at home.

| Finding | Source |
|---|---|
| CKD has no simple early marker; guidelines recommend check-ups every 6 months for cats over 7. (= at best a snapshot twice a year) | [R4] ISFM |
| Routine check-ups are periodic snapshots that may miss early CKD signs; continuous home monitoring may help notice changes earlier. | [R11] Purina press release |
| Owners at work can't see daily changes. | Our argument (no source needed; matches product doc) |

Bridge sentence into slide 4: "PawWatch watches food, water and litter all day, compares today with the cat's own week, and tells the owner when something changes. It never diagnoses."

---

## Draft slides (motivation)

**Slide 2: Cats hide illness**
- Cats instinctively hide pain and illness [R1, R2]
- Obvious symptoms often appear only when illness is advanced [R2]
- Owners are at work all day; vet check-ups are months apart [R4]

**Slide 2b: Behavior is the early warning**

| What changes | Could signal | How common |
|---|---|---|
| Drinking ↑ | Kidney disease, diabetes, hyperthyroidism | Kidney disease: up to 30–40% of older cats, only 3.6% diagnosed [R4, R5] |
| Eating ↑ | Hyperthyroidism | 8.7% of cats over 10 [R6] |
| Litter visits ↑ | Urinary disease, kidney disease | CKD cats: 2× litter visits, even in early stages [R11] |

Red callout: **A blocked urinary tract can kill within 48 hours. The first sign is frequent litter trips.** [R10]

---

## References (motivation)

| ID | Citation | Link |
|---|---|---|
| R1 | Evangelista MC et al. Facial expressions of pain in cats: the development and validation of a Feline Grimace Scale. *Sci Rep*. 2019. | https://ucalgary.ca/news/cats-faces-reveal-their-hidden-pain |
| R2 | VCA Animal Hospitals. Recognizing Signs of Illness in Your Cat. | https://vcahospitals.com/resources/conditions-cat/recognizing-signs-of-illness-in-your-cat |
| R3 | Stella JL, Lord LK, Buffington CAT. Sickness behaviors in response to unusual external events in healthy cats and cats with feline interstitial cystitis. *JAVMA*. 2011;238(1):67–73. | https://pubmed.ncbi.nlm.nih.gov/21194324/ |
| R4 | Sparkes AH et al. ISFM Consensus Guidelines on the Diagnosis and Management of Feline Chronic Kidney Disease. *J Feline Med Surg*. 2016. | https://journals.sagepub.com/doi/10.1177/1098612x16631234 |
| R5 | Conroy M, Brodbelt DC, O'Neill D, Chang Y, Elliott J. Chronic kidney disease in cats attending primary-care practice in the UK: a VetCompass study. *Vet Rec*. 2019. | https://rvc-repository.worktribe.com/OutputFile/1382711 |
| R6 | Stephens MJ et al. Feline hyperthyroidism reported in primary-care veterinary practices in England. *Vet Rec*. 2014. | https://rvc-repository.worktribe.com/output/1404762 |
| R7 | Peterson ME, Castellano CA, Rishniw M. Evaluation of body weight, body condition, and muscle condition in cats with hyperthyroidism. *J Vet Intern Med*. 2016;30(6):1780–1789. | https://pmc.ncbi.nlm.nih.gov/articles/PMC5115195/ |
| R8 | O'Neill DG et al. Epidemiology of diabetes mellitus among 193,435 cats attending primary-care veterinary practices in England. *J Vet Intern Med*. 2016. | https://www.rvc.ac.uk/vetcompass/news/epidemiology-of-feline-diabetes-mellitus |
| R9 | Merck Animal Health. Diabetes in cats: FAQ. | https://www.merck-animal-health-usa.com/mkt/pet-diabetes-month/cats-faq-2 |
| R10 | Cornell Feline Health Center. Feline Lower Urinary Tract Disease. | https://vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/feline-lower-urinary-tract-disease |
| R11 | Langenfield-McCoy et al. Enhancing Detection of Chronic Kidney Disease Through Smart Litter Box Monitoring. *Animals*. 2026;16(9):1319. | https://www.mdpi.com/2076-2615/16/9/1319 |

Extra (not used yet): hyperthyroidism signs page, [iCatCare](https://icatcare.org/articles/hyperthyroidism-in-cats).

---

## Step 2: Existing solutions (slide 3)

### Narrative

| # | Point | Section |
|---|---|---|
| 1 | The market already sells "smart" cat devices, so the need is real | E1 |
| 2 | But each device watches **one spot** (litter OR water OR a camera that only streams), and most smart features live in the cloud / behind a subscription | E1, E2 |
| 3 | Research shows cameras can recognize cat eating, and litter data can flag disease; nobody combines these into one local system | E3 |
| 4 | PawWatch: one box, all spots (food, water, litter, no-go), video stays home, no subscription | → slide 4 |

### E1. Products

Prices are US list prices as seen on 2026-10-10; promos change often, so round them on the slide.

| Product | Maker | What it watches | Smart features need… | Video / data | Price | Source |
|---|---|---|---|---|---|---|
| Furbo 360° Cat Camera | Tomofun (**Taiwan**) | Live view, meow alerts, treat toss. **No** eat/drink/litter tracking | Furbo Nanny subscription for smart alerts, daily recap, video history (3 days on Standard) | Cloud clips | Camera ~$54 (promo; list $184) + Nanny $6.99–9.99/mo, +$2/mo per extra camera | [C1], [C2] |
| Petcube cameras | Petcube | Live view, bark/meow, pet vs. person | Petcube Care for cloud video history (3 or 90 days), smart alerts, video filters | Cloud video | Subscription (price on their site) | [C3] |
| Petivity Smart Litterbox Monitor | Purina | **Litter only**: weight, urination, defecation per visit, up to 5 cats; alerts on changes | No subscription listed | App + monthly email reports | $129.99 | [C4] |
| Litter-Robot 4 | Whisker | **Litter only**: visits, weight (cat ID by weight), duration | Free app: basics; Whisker+ for daily recap, trends, behavior patterns (1 year included in bundle) | App | ~$907 bundle | [C5] |
| Litter-Robot 5 Pro | Whisker | Litter + camera with AI face recognition | Camera AI + video streaming are Whisker+ features | Cloud | (not checked) | [C5] |
| PETKIT Purobot Ultra | PETKIT | **Litter only**: visits, duration, weight, photos of stool/clumps; 180° camera with livestream | "Care+" upgrade for enhanced health monitoring (details not stated) | App stops updating when offline | (not listed) | [C6] |
| Sure Petcare Felaqua Connect | Sure Petcare (MSD Animal Health) | **Water only**: how often, when, how much; per cat via microchip | Requires the Sure Petcare Hub + app; no subscription mentioned | Hub connects to home router | (not listed) | [C7] |

| SureFeed Microchip Pet Feeder Connect | Sure Petcare | **Food only**: scale under the bowl → when and how much each cat eats; per cat via microchip | Needs the Sure Petcare Hub | Hub → router | $179.99 (review 2019; Hub extra) | [C10] |
| Petlibro Granary 2 series | Petlibro | **Food only**: built-in scale estimates amount eaten, duration, frequency, speed. Vision models add a 1080p camera, recognize up to 10 cats | Petlibro Care **from $59.99/yr** for some health tracking; Video Cloud **$119.99/yr** for recording | Cloud for video | $129.99–249.99 (Vision $189.99) | [C11] TechCrunch, 2026-10-06 |

**Correction: smart feeders DO track eating by weight** (SureFeed Connect, Petlibro Granary 2). So "nobody monitors food" is false. The true claim is: **no single product covers food + water + litter**; each is a separate device.

Not checked: PETKIT feeders/fountains (probably similar).

Takeaways:
- **Fragmented:** to watch food + water + litter today you need 3 devices from different brands/apps (e.g. a smart feeder + Felaqua ≈ ? + Petivity $130 + a camera with a subscription). Good slide visual: "3 devices, 3 apps" vs. "1 box".
- **Cameras don't do health:** Furbo/Petcube are for watching and alerts (meow, bark); they don't log eating, drinking or litter use.
- **Cloud + subscription is the norm** for camera smart features (Furbo Nanny, Petcube Care, Whisker+).
- **Local angle:** Furbo is made by a Taiwanese company (Tomofun) → good for a Taiwan market slide later.

### E1b. Is PawWatch cheaper? (cost check)

Short answer: **not clearly cheaper up front**, because the UGen300 alone is ~$299. It wins on **no subscription** and **cheap extra spots**.

PawWatch bill of materials (3 spots: food+water, litter, no-go):

| Part | Price | Source |
|---|---|---|
| ASUS UGen300 (USB, Hailo-10H, 8 GB) | $299 MSRP (reseller $289); Taiwan NT$6,380; 2.5 W typical | [C12] SHI; [C13] iThome |
| Host: Raspberry Pi 5 4GB (or the owner's existing PC → $0) | $85 MSRP as of Feb 2026; Pi prices rose again in Apr 2026, so assume ~$85–110 | [C14] Notebookcheck |
| 3 × indoor Wi-Fi camera with RTSP (e.g. Tapo C110) | ~$12.50–30 each (4-pack deal was $49.99 in 2024) | [C15] Slickdeals |
| **Total** | **≈ $430–500 one-time**, $0/yr (≈ $340–390 if the owner already has a PC) | |

Competitor stack to cover the same three spots + a camera:

| Device | One-time | Per year | Source |
|---|---|---|---|
| Smart feeder (Petlibro Granary 2) | $130 | $60 (Petlibro Care, for health tracking) | [C11] |
| Smart fountain (Felaqua Connect + Hub) | price not found (verify) | – | [C7] |
| Litter monitor (Petivity) | $130 | – | [C4] |
| Pet camera (Furbo 360° Cat) | $54–184 | $84–120 (Nanny) | [C1], [C2] |
| **Total (without Felaqua)** | **≈ $315–445** | **≈ $145–180/yr** | |

3-year view: competitor stack ≈ $750–985 (+ Felaqua) vs. PawWatch ≈ $430–500. Rough, depends on promos.

Honest framing for the slide:
- ✗ Don't say "cheaper" without qualification; up front it's about the same.
- ✓ "**No subscription**: one-time hardware, the AI runs at home."
- ✓ "**Each extra spot is a ~$20 camera**, not another $130–180 smart device." (One UGen300 serves many cameras; slide 9 shows 3 cameras × 5 fps fits.)
- ✓ For the business slide: in a licensing model (camera makers, or ASUS PCs with NPUs), the accelerator cost is shared or already in the device, so the marginal cost is just software.

### E2. Privacy concern with cloud pet cameras

| Finding | Source |
|---|---|
| Pet cameras record video and audio of the home; footage typically goes to the cloud ("someone else's computer"). Owners should check retention and law-enforcement access policies. Risks after purchase: company shuts down, stops security updates, or is acquired. | [C8] Mozilla Foundation, 2021 |

Use for the "No cloud" column and for slide 10 (Why on the edge). A consumer survey with a % would be stronger; not found yet.

### E3. Research

| Finding | Source |
|---|---|
| A fixed camera + pose estimation (DeepLabCut) classified cat sitting / lying / **eating** with 93.7% accuracy. Shows camera-based recognition of cat eating is feasible. Didn't cover drinking or litter. | [C9] Fujimori et al., IEEE GCCE 2020 |
| Load-sensor litter box + ML separated CKD cats from healthy ones (see R11). Litter only, no camera. | [R11] |

Gap to state on the slide: research does one behavior at a time; products do one spot at a time; nobody runs **food + water + litter + no-go on one local edge device**.

### E4. Positioning: what PawWatch can claim (differentiators)

Headline idea: **integration** is the core, backed by 3 supporting points.
Tagline candidate: *"One box. Every spot. Nothing new for your cat. Nothing leaves your home."*

| # | Differentiator | Why it matters (evidence) | Refs | Strength |
|---|---|---|---|---|
| D1 | **Integration: sees patterns across spots** | Diseases show up as *combinations*: kidney disease = drinking ↑ **and** urinating ↑ (PU/PD); diabetes = drinking + urinating + eating ↑; hyperthyroidism = eating ↑ (55%) with PU/PD (33%). A water-only or litter-only device sees half the pattern. Also 1 timeline / 1 app instead of 3–4 apps from different brands. | R4, R7, R9; C1, C4, C7, C11 | ★★★ main point |
| D2 | **Non-invasive: the cat keeps its own bowl and litter box** | Cats are particular about litter type and box location; bad experiences in or near the box can cause house-soiling. Smart litter boxes need an acclimation period (a few days to a week, some cats several weeks; keep the old box beside it). PawWatch only adds a camera on the wall. | P1, P2 | ★★★ strong, few competitors can say this |
| D3 | **Privacy: video never leaves home** | Ring (Amazon): every employee and contractor could view every customer video; one viewed thousands, incl. cameras in bedrooms and bathrooms; hackers took over accounts. Ring paid $5.6M in refunds (FTC, 2023). About 1 in 4 Americans worry smart cameras can be hacked. Pet cameras' footage typically goes to the cloud. | P3, P4, C8 | ★★ |
| D4 | **No subscription** | Smart features of competitors are paywalled: Furbo Nanny $84–120/yr, Petlibro Care $60/yr + Video Cloud $120/yr, Whisker+, Petcube Care. | C2, C3, C5, C11 | ★★ |
| D5 | **Cheap to add spots, low power** | Each extra spot = a ~$20 camera; one UGen300 serves several cameras (3 × 5 fps = 15 inferences/s); UGen300 draws 2.5 W typical. | C13, C15; slide 9 | ★★ |
| D6 | **Works offline** | PETKIT's app stops updating usage data without a network. PawWatch logs locally and keeps working when the internet is down. | C6 | ★ |
| D7 | **No-go zone alarm** | None of the products checked (cameras, feeders, fountains, litter boxes) alerts when the cat jumps onto the counter or table. Not health; a "daily-life" bonus feature. | E1 table (absence) | ★ (say "among products we reviewed") |

Suggested use:
- Slide 3 (existing solutions): table or visual showing fragmentation → D1
- Slide 4 (solution): tagline + D1, D2
- Slide 10 (why edge): D3, D4, D5, D6
- Slide 13 (business): D4, D5

Wording guardrails:
- D1: don't say PawWatch detects diseases; say it "sees the pattern" and suggests a vet visit.
- D2: P1 doesn't mention automatic litter boxes specifically; the argument is "cats are sensitive to box changes" (P1) + "smart boxes need acclimation" (P2). Don't claim smart boxes cause house-soiling.
- D7: "among products we reviewed", since we didn't check every camera.

### What competitors do better (be ready for judges' questions)

| They have | PawWatch MVP | Our answer |
|---|---|---|
| Per-cat ID (weight, microchip, face) | Can't tell cats apart | Future work (already on slide 15) |
| Amounts (ml water, g urine) | Counts and durations only | Frequency is what R11 found most significant (2× visits); amounts can come later from a scale |
| Finished consumer hardware | Prototype | Stage II on UGen300; licensing to camera makers (slide 13) |

### Draft slide 3: Existing solutions fall short

Option A (keep the table, fix the columns):

| | Food | Water | Litter | No-go alarm | Video stays home | No subscription |
|---|---|---|---|---|---|---|
| Pet cameras (Furbo, Petcube) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ (smart alerts) |
| Smart litter boxes (Petivity, Litter-Robot, PETKIT) | ✗ | ✗ | ✓ | ✗ | – | varies |
| Smart fountains (Felaqua Connect) | ✗ | ✓ | ✗ | ✗ | – | ✓ |
| Smart feeders (SureFeed Connect, Petlibro Granary 2) | ✓ (weighs) | ✗ | ✗ | ✗ | ✗ (Vision: cloud video) | varies (Petlibro Care $60/yr) |
| **PawWatch** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

"–" = no video. Check: does any pet camera have a no-go/zone alert? Not verified; if unsure, drop that column.

Option B (visual): left "Today: 3 devices, 3 apps, cloud + subscription" (icons of litter box, fountain, camera) → right "PawWatch: 1 box, every spot, video never leaves home".

### References (Step 2)

| ID | Citation | Link |
|---|---|---|
| C1 | Furbo. Furbo 360° Cat Camera product page. Accessed 2026-10-10. | https://furbo.com/us/products/furbo-360-cat-camera |
| C2 | ThePricer. How much does a Furbo subscription cost? | https://www.thepricer.org/how-much-does-furbo-subscription-cost/ |
| C3 | Petcube. What is Petcube Care membership. | https://petcube.com/support/article/petcube-care-membership/ |
| C4 | Petivity (Purina). Product list. | https://www.petivity.com/llms.txt |
| C5 | Whisker. Litter-Robot 4 Insights Bundle. | https://www.whisker.com/litter-robot-4-insights-bundle |
| C6 | PETKIT. Purobot Ultra product introduction (PDF). | https://ipet.ch/media/file_attachments/attachment/PETKIT_PUROBOT_ULTRA_-_Product_Introduction.pdf |
| C7 | Sure Petcare. Felaqua Connect. | https://www.surepetcare.com/en-us/felaqua-connect |
| C8 | Ehrenkranz M. How To (Responsibly) Spy On Your Pets. Mozilla Foundation, 2021. | https://www.mozillafoundation.org/en/blog/how-responsibly-spy-your-pets |
| C9 | Fujimori S, Ishikawa T, Watanabe H. Animal Behavior Classification Using DeepLabCut. IEEE GCCE 2020. | https://www.ams.giti.waseda.ac.jp/data/pdf-files/2020_GCCE_fujimori.pdf |
| C10 | Tech Advisor. Sure Petcare Microchip Pet Feeder review (2019). | https://www.techadvisor.com/article/720358/sure-petcare-microchip-pet-feeder-review.html |
| C11 | TechCrunch. Petlibro's new AI-powered feeder is a game changer for multi-cat homes. 2026-10-06. | https://techcrunch.com/2026/10/06/petlibros-new-ai-powered-feeder-is-a-game-changer-for-multi-cat-homes/ |
| C12 | SHI. ASUS UGen300 USB AI module listing. | https://texas.gs.shi.com/product/52158156/ASUS-UGEN300-USB-AI-MODULE-HAILO-10H-8-GB-LPDDR4-USB-3.1-GEN2 |
| C13 | iThome. ASUS UGen300 press release (NT$6,380, 2.5 W, 40 TOPS). | https://www.ithome.com.tw/pr/175676 |
| C14 | Notebookcheck. Raspberry Pi 5 now costs up to $205 due to RAM crisis. 2026-02-02. | https://www.notebookcheck.net/Raspberry-Pi-5-now-costs-up-to-205-due-to-RAM-crisis.1218213.0.html |
| P1 | AAFP & ISFM. Feline House-Soiling: Useful Information for Cat Owners. 2014. | https://catvets.com/wp-content/uploads/2024/01/HouseSoiling-B&W.pdf |
| P2 | Whisker. Acclimate your cat to Litter-Robot. | https://www.whisker.com/acclimate-your-cat |
| P3 | Malwarebytes. Ring agrees to pay $5.6 million after cameras were used to spy on customers. 2024-04-25 (FTC charges, May 2023). | https://www.malwarebytes.com/nl/blog/news/2024/04/ring-agrees-to-pay-5-6-million-after-cameras-were-used-to-spy-on-customers |
| P4 | CE Pro. Despite growth of smart devices, Americans are growing wary of security, privacy concerns (CraftJack survey). 2024-01-22. | https://www.cepro.com/news/despite-growth-of-smart-devices-americans-are-growing-wary-of-security-privacy-concerns/132844/ |
| C15 | Slickdeals. TP-Link Tapo C110 4-pack deal (2024). | https://slickdeals.net/f/17777847-4-pack-tp-link-tapo-c110-3mp-indoor-wi-fi-security-camera-with-night-vision-50-free-s-h-49-99 |

## Step 3: Market (slide 13)

### Narrative

| # | Point | Section |
|---|---|---|
| 1 | Cats are the fastest-growing pet: Taiwan's cats just overtook dogs | K1 |
| 2 | Cats are getting older → more chronic disease (ties back to M2) | K2 |
| 3 | Pet tech is a big, fast-growing market; health is its largest segment | K3 |
| 4 | Our reachable market, bottom-up (TAM / SAM / SOM) | K4 |

### K1. Cat population

| Finding | Source |
|---|---|
| **Taiwan**: ~1.74 M pet cats in 2025, up **32.8%** from 1.31 M in 2023; **cats outnumber dogs (1.46 M) for the first time**. Multi-cat households are increasing. Reason given: more single people and small urban homes. | [K-a] Ministry of Agriculture survey via PTS / CTEE, 2026-04-20 |
| Taiwan cat registration became mandatory with fines from 2026-01-01 (66.5% registered). | [K-b] Newtalk, 2026-04-20 |
| **US**: ~53 M cat-owning households in 2025 (≈39% of households), +5% YoY. | [K-c] APPA 2026 Cat Report via PetfoodIndustry, 2026-09-15 |
| **Japan**: ~9.06 M pet cats (2023). | [K-d] Asia News Network, 2024 |

Slide line: **"Taiwan: 1.74 M cats, +33% in two years, now more than dogs."** [K-a]

### K2. Cats are ageing

| Finding | Source |
|---|---|
| Japan: average cat lifespan hit a record **15.79 years** (2023). | [K-d] |
| Japan: **44.4%** of cats were over 7 years old (2015). | [K-e] GlobalPETS, 2018 (older data, no primary source named; use with care) |
| Japan: about **60% of cat owners took their cat to the vet once or not at all** in the past year (JPFA survey 2023). | [K-d] |

Taiwan senior-cat share: not found. Use Japan as a proxy and say so.
The 60% stat is a good replacement for the dropped 2008 US stat; it fits M3 ("check-ups are rare").

### K3. Pet tech market (top-down)

| Finding | Source |
|---|---|
| Global pet tech: **US$15.6 B (2025) → US$52.9 B (2035), CAGR 12%**. | [K-f] Global Market Insights |
| **Pet healthcare** is the largest application segment: **US$4.4 B** (2025). | [K-f] |
| Asia Pacific is the fastest-growing region (CAGR 13.9%); North America is largest (US$8.6 B). | [K-f] |
| Asian startups already sell AI cat health tools (Rabo Catlog collar, Carelogy pain app), showing demand in the region. | [K-d] |

Caveat: market-research firms disagree a lot on pet tech size; quote one firm and name it.

### K4. TAM / SAM / SOM (bottom-up, Taiwan first)

TAM/SAM/SOM in one line: **TAM** = everyone who could ever want it; **SAM** = the part we can actually reach with this product; **SOM** = what we can realistically win in ~3 years.

Assumptions (state them on the slide or in the appendix):
- A1: ~1.5 cats per cat household → Taiwan ≈ 1.74 M / 1.5 ≈ **1.16 M cat households**. (No official household count found; dog households are only 1.2 pp more than cat households.)
- A2: ~40% of households have a cat 7+ (Japan proxy, 44% [K-e]).
- A3: price per household ≈ NT$10,000 (kit or licensed device). See business model.
- A4: 1 USD ≈ NT$32.

| Level | Definition | Households | Value |
|---|---|---|---|
| TAM | Global pet tech healthcare segment | – | US$4.4 B/yr [K-f] |
| SAM | Taiwan cat households with a cat 7+ | 1.16 M × 40% ≈ **460 k** | × NT$10k ≈ **NT$4.6 B** (≈ US$145 M) |
| SOM | 1% of SAM in 3 years | ≈ **4,600** | ≈ **NT$46 M** (≈ US$1.4 M) |

Expansion story: Taiwan → Japan (9 M cats, oldest cats) → US (53 M cat households).

### References (Step 3)

| ID | Citation | Link |
|---|---|---|
| K-a | PTS News / Commercial Times. Ministry of Agriculture 2025 (ROC 114) household dog and cat survey. 2026-04-20. | https://news.pts.org.tw/article/804498 ; https://www.ctee.com.tw/news/20260420700862-430104 |
| K-b | Newtalk. 114年家犬貓調查. 2026-04-20. | https://newtalk.tw/news/view/2026-04-20/1030714 |
| K-c | PetfoodIndustry. Report: Cat ownership grows to 53 million U.S. households (APPA 2026 Cat Report). 2026-09-15. | https://www.petfoodindustry.com/pet-food-market/market-trends-and-reports/news/15834866/report-cat-ownership-grows-to-53-million-us-households |
| K-d | Asia News Network. Japan's ageing cats feeling paw-sitive effects of AI healthcare. 2024-06-04. | https://asianews.network/japans-ageing-cats-feeling-paw-sitive-effects-of-ai-healthcare |
| K-e | GlobalPETS. Japanese pet market. 2018. | https://globalpetindustry.com/article/japanese-pet-market/ |
| K-f | Global Market Insights. Pet Tech Market report. | https://gminsights.com/industry-analysis/pet-tech-market |

---

## Step 4: Business model (slide 14)

### How to think about it (5 questions)

A business model just answers:
1. **Who pays?** (customer)
2. **For what?** (what they get)
3. **How much, how often?** (one-time / per unit / monthly)
4. **Why us instead of alternatives?** (our differentiators D1–D7)
5. **How do we reach them?** (channel, first customer)

Concrete example (Furbo): owners pay ~$54–184 once for the camera (Q1–3) + $84–120/yr for Nanny alerts; reached through Amazon and pet stores (Q5).

### Our problem with selling to owners directly

PawWatch's hardware costs ~US$430–500 (≈ NT$14–16k) because of the UGen300 [E1b]. Selling a consumer kit at a profit means a price above competitors' devices. So **direct-to-owner is not the best first model**.

### Three options

| | B2B license (makers) | Vet clinic plan | Direct to owners |
|---|---|---|---|
| Who pays | Device makers: pet cameras, NAS / home hubs, PCs with NPU, ASUS UGen ecosystem | Vet clinics (pass cost to owners) | Cat owners |
| What they get | PawWatch edge software: cat detection + visit log + alerts + report, runs on their hardware | Rental kits for at-home monitoring after surgery / for chronic cases; daily reports in a clinic view | Box + cameras |
| Price idea | US$3–10 per device sold (license) | e.g. NT$1,000–2,000 per kit per month | one-time kit |
| Why us | Adds a health feature without cloud cost (D3, D4); hardware-agnostic detector contract | Objective eat/drink/litter data between visits; ~60% of owners rarely visit vets [K-d] → clinics want to stay connected | No subscription, nothing new for the cat (D2, D4) |
| Reach | (not on slides for now; see Decision) | (not on slides for now) | Later |
| Risk | Long sales cycle | Small volume | High BOM today |

### Decision (2026-10-10)

- Keep **B2B license as a revenue model** on slide 14, but **generic**: "device makers (pet cameras, home hubs, PCs with edge AI)". **Do not name companies** (no ASUS / Tomofun / NAS brands as partners) and **do not mention outreach or partnerships**.
- **Vet clinic plan** stays as a model; no named clinic.
- **Direct to owners** stays as a later option.
- Prices are not shown as numbers (no source); describe the *form* only: per-unit license, monthly clinic plan, one-time purchase.

Slide 14 table (reorder the existing one):

| Customer | Offer | Revenue |
|---|---|---|
| Device makers (pet cameras, home hubs, PCs with edge AI) | PawWatch edge software on their hardware: no cloud cost for them | Per-unit license |
| Vet clinics | At-home monitoring kits for post-surgery and chronic cases (e.g. kidney disease) | Monthly rental per kit |
| Cat owners | Box + cameras, no subscription | One-time purchase |

One line under the table: "Licensing lets PawWatch ride on hardware people already buy, so the UGen300 cost doesn't land on one product." Unit cost line: "Today's kit: UGen300 US$299 + host + 3 × ~US$20 cameras ≈ US$430–500." [C12–C15]

Go-to-market line (no partners): "Stage II: port to UGen300 → measure fps and power → pilot with real cats at home."

Feasibility point (already on the software slide, keep as is): the detector returns `(label, score, box)`, the same format as ASUS's UGen300 demos, so moving from laptop to UGen300 swaps one component. The Hailo backend is **not written yet**: say "designed to swap", not "runs on UGen300".
