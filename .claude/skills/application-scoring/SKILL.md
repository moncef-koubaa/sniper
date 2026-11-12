---
name: application-scoring
description: The single scoring rubric (0-100, six weighted criteria) shared by /find-contacts and /find-offers, with sub-score anchors, the custom-CV threshold and per-run cap. Use whenever a company or an offer must be scored, ranked, or given a CV decision.
---

# Application scoring

Weights, threshold, cap and colour bands live in `config/scoring.yaml` (Nermine edits them there).
**Claude only judges sub-scores** (0.0–1.0, steps of 0.1) and writes one short note per criterion;
`scripts/score.py` does the arithmetic, ranking, band and CV decision. Never compute totals by hand.

## Workflow
1. For each row, read the offer text (offers) or the company's activity/careers/team pages (companies) and
   `profile/facts.json`.
2. Fill `subscores` and `notes` for the six criteria using the anchors below. Notes ≤ 15 words, factual
   ("asks Aspen Plus + LCA: both hands-on (P3)").
3. Write all rows to a JSON file and run `python3 scripts/score.py rows.json -o scored.json`.
4. Use `score`, `breakdown`, `band`, `rank`, `cv_decision`, `letter_due` from the output as-is.
   The Excel "Score breakdown" column = `breakdown` + " | " + the six notes joined by " / ".

## Anchors (default weights in brackets)

**domain_fit [30]** — overlap of the target's activity with `facts.json → domains` and projects.
1.0 the topic is one of her projects/internship (Li-ion modelling, PEM electrolyser, Aspen process simulation+LCA) ·
0.8 same domain, different object (battery ageing tests, Power-to-X TEA) · 0.6 adjacent domain she studied
(catalyst synthesis, water treatment process design) · 0.4 chemical engineering but outside her domains
(pharma formulation, polymers processing) · 0.2 engineering but not chemistry · 0 unrelated.

**skills_match [20]** — required tools/techniques vs `facts.json → skills/tools` (level).
Score = Σ(required items: hands_on 1.0, trained 0.75, studied 0.5, missing 0) / number of required items;
cap at 0.9 if a *must-have* is missing; companies (no list): use the 3–5 core techniques of the team's work.

**feasibility [15]** — start, duration, location/visa, language.
Start within ±6 weeks of 2027-02-01 (0.4) + duration 4–6 months or flexible within 3–9 (0.3) + location
realistic: EU/CH/UK/Canada host that can sign a foreign convention (0.2) + language FR or EN (0.1).
Subtract 0.2 when the posting says EU nationality / existing work permit required, or start < 10 weeks away.

**hiring_signal [15]** — offers: 1.0 live, dated PFE/master-thesis posting with application route; 0.7 live but
undated/older than 4 months; 0.4 generic "internships" page; 0 closed. Companies: 1.0 current internship
postings in her field; 0.7 a documented history of PFE/master interns or an R&D centre with intern pages; 0.5
R&D activity + growth (funding, new plant) but no intern evidence; 0.3 small firm, no signal.

**contact_quality [10]** — best reachable contact found.
1.0 named process/chemical/R&D engineer or team lead in her domain with **verified** email · 0.8 same person,
pattern-inferred email · 0.7 named supervisor on an offer (application via portal) · 0.6 named HR/campus recruiter
verified · 0.5 named HR inferred · 0.4 generic careers/recruitment email · 0.2 portal only, no name · 0 nothing.

**strategic_value [10]** — fit with `config/scoring.yaml → strategic_sectors` and what it leads to.
1.0 squarely in a strategic sector **and** thesis/hiring pipeline (CEA, IFPEN, Fraunhofer, battery/H2 scale-ups) ·
0.8 strategic sector · 0.6 adjacent sector (water, waste, analytical R&D) · 0.4 neutral · 0.2 routine QC/production.

## Thresholds (config/scoring.yaml)
- `custom_cv_threshold` 75 → `cv_decision = Custom` for the top `max_custom_cvs_per_run` (5); further high scorers
  `Custom (pending)` (send a library CV meanwhile; Notes: "custom CV pending").
- Below threshold → `Library`: choose with the `cv-library` skill (`scripts/pick_cv.py`), one-line reason.
- `cover_letter_threshold` 60 → `/find-offers` drafts a letter when `letter_due` is true.
- Bands: green ≥ threshold, amber 60–(threshold−0.1), grey < 60.

## Consistency rules
- Same evidence → same sub-score across runs; when unsure between two anchors, take the lower.
- Never raise a sub-score because the company is famous; never lower one because the posting is in French.
- A row scored without opening its page gets hiring_signal ≤ 0.4 and a note "page not read".
