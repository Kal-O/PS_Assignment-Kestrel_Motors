# Preliminary findings — explainable starting point

Run `python src/pipeline.py` to reproduce these figures.

| Measure | Initial value |
|---|---:|
| Feedback source files | 52 |
| Data-bearing file/sheet candidates | 82 |
| Candidate feedback records | 7,271 |
| Accepted by *current blocking rules* | 7,125 |
| Flagged for review | 146 |
| Accepted records with usable normalized ratings | 7,115 |
| Records with normalized rating <=2 | 1,588 |
| Negative rating proportion of usable accepted records | 22.32% |

**Do not publish the 22.32% as a business-level dissatisfaction rate.** The response sample may be biased, records include mixed survey types, some categorical ratings are converted subjectively, and negative feedback may be in comments despite a higher score.

## Source complications independently observed

- Geelong 2025 uses reverse scoring (`1 = Excellent`, `5 = Poor`), changing later.
- Ringwood changes from a five-point to a ten-point scale *within Q1 2026* and remains ten-point for Q2/Q3.
- Ringwood score conversion is linear `1 + 4*(score10 - 1)/9` and is an analytical approximation, not proven scale equivalence.
- Liverpool Q3 uses US-style month/day/year dates; other sources vary.
- Chermside has a Q1 `FINAL` and `FINAL v2` overlap.
- Essendon uses separate sheets for Sales, Service and Parts without an explicit department column.
- North Queensland file contains two separate dealerships; `ROK` identifies Rockhampton.
- Shepparton records postdate its listed closure date (2026-03-31).
- Toowoomba Q4 2025 is an aggregate table, not individual responses.
- Southport's Google reviews are a separate source type and are not automatically comparable to surveys.
- Some original files contain names, email, mobile numbers, and vehicle registration data. Redaction remains imperfect; candidate must inspect before publishing.

## Keyword exploration — not yet an AI finding

On negative-rating accepted records, basic case-insensitive token-substring keyword matches identified 495 Communication, 332 Waiting & delays, 277 Price & billing, 197 Parts availability, 137 Quality & repairs, and 36 Staff & courtesy **mentions**. Records may appear in multiple groups; substring matches have false positives, may miss paraphrases and can incorrectly tag positive mentions. These counts must **not** be labelled causal negative-feedback drivers until context-sensitive classification and manual evaluation are performed.

## Next business questions

- Which *verified* negative themes are most prominent in each department and region?
- Are changes over time due to real experience differences, survey formats, source coverage or the Shepparton closure?
- Which high-volume dealerships/department themes offer the largest testable opportunities for intervention?
- What *scenario range* of revenue / contribution is plausible under explicit assumptions (not a claimed forecast)?
