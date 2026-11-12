---
description: Posted PFE offers — search configured sources for PFE / stage de fin d'études / master-thesis internships starting around Feb 2027 in Nermine's domains, extract and verify each offer, dedup, score, pick/build the CV, draft cover letters (score >= 60) and write outputs/offers/offers_<date>.xlsx. Never applies or sends.
argument-hint: "[keywords/domains] [countries] [max offers, default 30]   e.g. /find-offers \"batteries, hydrogène\" France 10"
---
FIND-OFFERS RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md, skills `application-scoring`, `nermine-writing-style`, `cv-library`. Never asks, never applies,
never logs in (JobTeaser/LinkedIn/Indeed: reached via web-search results only, URL recorded). Working files in
`outputs/offers/work_<date>/`.

## 0. Parameters
Keywords/domains, countries, max offers (default `config/search.yaml → defaults.find_offers.max_offers` = 30).
Sources = `config/search.yaml → offer_sources` with `enabled: true`. Record everything in the run log.

## 1. Search
For each enabled source × domain keyword × country (FR and EN labels from `keywords.offer_labels`):
- career sites with a search URL → WebFetch the search/listing page; others → WebSearch
  `site:<domain> (stage fin d'études OR PFE OR "master thesis") <keyword> 2027`.
- Keep postings that are internships of 4–6 months (3–9 acceptable) for final-year engineering / M2 students,
  starting between Dec 2026 and Apr 2027 (or unspecified "début 2027"). Skip `exclusions.offer_terms`
  (alternance, CDI, PhD…). Stop collecting at ~1.5 × max.
- Log every source as `used`, `no result`, or `blocked (login/captcha/robots)`.

## 2. Extract (open each offer page)
title, company, team/lab, location, start date, duration, pay (if listed), language of the posting, required skills
& tools (list), contacts named on the offer (name, role, email if printed), application method (portal URL / email /
form) and deadline, direct link, date published. Unknown → empty. Read the offer page itself, not only the snippet.

## 3. Verify live
`python3 scripts/check_links.py --json work_<date>/links.json`; drop dead links. On the page: "offre pourvue",
"closed", "expired", past deadline → drop (log as closed).

## 4. Dedup
Against `config/applied.csv` and every earlier `outputs/offers/offers_*.xlsx`: same company (normalised) **and**
similar title (token Jaccard ≥ 0.5 after removing stop words, or same reference number) = duplicate → drop, log.
Also dedup within the run (same offer on two job boards → keep the company-site URL).

## 5. Score
Rubric from the scoring skill with the offer text as the requirements (skills_match = Σ levels over the required
list; hiring_signal from posting freshness; contact_quality from the named contact). Save `rows.json` → run
`python3 scripts/score.py work_<date>/rows.json -o work_<date>/scored.json`. Keep the top `max` offers.

## 6. CV decision
`Custom` → `/tailor-cv` procedure with the offer's required skills + title as keywords and its language;
`Custom (pending)` → library CV + Notes "custom CV pending"; `Library` → `scripts/pick_cv.py` + one-line reason.

## 7. Cover letters (letter_due = score ≥ cover_letter_threshold, default 60)
Write `outputs/letters/<Company>_<Short-title>_<lang>.md` in the offer's language following
`cover-letter-rules.md` (CL-01…CL-15) and the examples: exact offer title in the Objet/Subject; salutation to the
named contact on the offer (all named supervisors, like CL03) — otherwise generic + Notes `GENERIC SALUTATION`;
¶1 request + availability (offer dates if stated); ¶2 one proof mapped to the requirements; ¶3 the team's concrete
strength (from the offer or the team page, cite the URL in Notes); gap sentence for each must-have she lacks
(CL-10); ¶4 one line; closing CL-12. Then:
- `python3 scripts/build_letter.py outputs/letters/<file>.md` → ok (250–390 words, 1 page; .docx + .pdf created).
- `python3 scripts/check_claims.py outputs/letters/<file>.md` → ok.
- `checklist.md` (letter part).

## 8. Excel
`work_<date>/run.json` with `kind: "offers"` and one object per offer with the Offers columns of
`scripts/build_xlsx.py`: Score breakdown (`breakdown` + " | " + notes), Key requirements, My matching evidence
(me.md facts with project/internship IDs), Gaps (honest), CV decision, CV file, Cover letter file, Contact on offer,
Application method, Link to post, Date found (today), Status "To send", Deadline as YYYY-MM-DD when known. Run
`python3 scripts/build_xlsx.py work_<date>/run.json outputs/offers/offers_<date>.xlsx` (sorted by score, row 2 = top
priority, deadlines ≤ 7 days highlighted). Reopen with openpyxl: sorted, ranks 1..n, every letter_due row has a
Cover letter file.

## 9. Log and report
Append to `logs/run_<today>.md`: parameters, sources used/blocked, counts (found, closed/dead, duplicates, kept,
letters, custom CVs built/pending), validation results. Final message: top 5 (rank, score, title, company, deadline,
CV decision, letter file) and the xlsx path.
