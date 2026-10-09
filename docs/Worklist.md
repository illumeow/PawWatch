# PawWatch hackathon worklist

2026-10-09

Four things are due by 10/14: registration, English slides, English demo video and a GitHub repo. The goal is to submit something solid with the least effort: build only the smallest demoable version of the code and put the effort into the slides and video.

For product purpose, features and design, see [Product description](ProductDescription.md).

## Deliverables (by 10/14)

| Item | Requirement | Notes |
| --- | --- | --- |
| Online registration | Team member details, choose track and participation format | Choose Lightning. For format, the international online group is suggested, so we don't have to go to ASUS HQ on 12/19 if we're finalists |
| English slides | Max 20 content pages | About 12 pages is enough |
| English demo video | Under 3 minutes, uploaded to YouTube as "unlisted" | Film our own cat |
| GitHub repo | Public, with README | Link it in the slides |

## 0. Start recording today (top priority)

- [ ] Fix two or three phones or webcams on the food bowl, water bowl and litter box, and record simultaneously for one or two days (don't move the cameras)
- [ ] Also film a few clips of the cat jumping onto the table or counter

The program reads the recorded video files directly instead of a live webcam. This makes the demo more stable, even if the cat doesn't cooperate.

## 1. Code (MVP)

A laptop is enough; hardware is only shipped after we're shortlisted.

- [ ] **Detection:** use Ultralytics YOLOv8n's off-the-shelf COCO model, keep only class 15 (cat), no training.
- [ ] **Zone config:** write a `zones.json` per camera storing the polygon coordinates of the zone it covers (food bowl, water bowl, litter box or forbidden zone). The program must read several video files or streams at once, and event records get an extra camera column. Whichever polygon the detection box's center falls in is the zone the cat is in.
- [ ] **Event logic:** the cat must stay in the same zone for more than N seconds to count as one "eat / drink / litter" visit. Add debouncing so a flickering box isn't counted twice.
- [ ] **Logging:** store in SQLite, events only (time, zone, duration), no frames. This is the privacy selling point.
- [ ] **Forbidden-zone alarm:** when the cat enters a forbidden zone, play a sound and show a red box on screen. Telegram notifications can be added if wanted.
- [ ] **Anomaly alert:** compare today's count with the 7-day average and alert when it differs a lot. The past 7 days can be fake data, labeled "simulated" in the slides.
- [ ] **Daily report:** a template string is enough. For bonus AI points, have a small model via Ollama (e.g. Qwen 1.5B) write it.
- [ ] **Dashboard:** Streamlit, one page with today's counts, timeline, 7-day trend chart and daily report.
- [ ] **README:** features, architecture diagram, how to run, and how to deploy to UGen300 (Hailo-10H) later.

## 2. English slides (about 12 pages)

★ marks items the official rules require.

1. Cover: PawWatch plus a slogan
2. ★ Problem: cats hide pain well; changes in eating, drinking and litter use are often the earliest signs, but owners are at work during the day and can't see them. Find one or two vet or research sources for this page.
3. Shortcomings of existing solutions: pet cameras need the cloud, a monthly fee and raise privacy concerns; smart litter boxes only cover litter use.
4. ★ Solution: a camera plus an edge AI accelerator tracking eating, drinking and litter use together, plus forbidden-zone alarms.
5. Demo screenshots: detection view and dashboard
6. ★ Hardware and software architecture diagram: camera → UGen300 running YOLO → event engine → SQLite → dashboard and notifications
7. Why on the edge: privacy, no cloud cost, works offline, low power
8. ★ Expected benefits: catch anomalies early, reduce emergency visits and medical costs
9. Business model (35% of the score, most important): license to pet camera and smart litter box makers, partner with vet clinics for remote care, one-time hardware purchase instead of a subscription
10. Market size: number of pet cats in Taiwan and the global pet tech market; research needed for this page
11. Future work: multi-cat identification (which cat ate from which bowl), street-cat TNR tracking (ear-tip recognition)
12. Team, ★ references, ★ GitHub link

## 3. Demo video script (3 minutes)

| Time | Content |
| --- | --- |
| 0:00–0:20 | Opening: your cat + one question ("Would you notice if your cat drank twice as much water today?") |
| 0:20–0:50 | Pain points and shortcomings of existing solutions |
| 0:50–2:10 | Live footage: count ticks up when the cat eats → alarm sounds when it jumps on the table → dashboard → daily report |
| 2:10–2:45 | Architecture diagram and why on the edge |
| 2:45–3:00 | Future work and closing |

The English narration can be generated with TTS; no need to record it ourselves.

## 4. Suggested schedule

| Date | Code | Slides / video |
| --- | --- | --- |
| 10/9 (Fri) | Record cat footage, set up repo, get YOLO detection working | Research market and vet sources |
| 10/10–11 | Zone logic, events, SQLite, alarm | Write slide text |
| 10/12 | Streamlit dashboard, daily report, README | Architecture diagram, slide layout |
| 10/13 | Record screen captures | Edit video, add narration, upload to YouTube |
| 10/14 | Buffer, remember to submit early | Check all links |

Split: two people code, one does the slides (plus research and the architecture diagram). Of the two coders, one does the first half (detection, zones, events, SQLite, alarm) and the other the second half (dashboard, daily report, README); the latter also edits the video and adds narration on 10/13. On the last day all three check everything together.
