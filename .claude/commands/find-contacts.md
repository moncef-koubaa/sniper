---
description: Spontaneous applications — find companies that fit Nermine's profile, research public professional contacts (verified vs pattern-inferred emails), score them, draft a personalised email to the best contact, pick or build the CV, and write outputs/contacts/contacts_<date>.xlsx. Never sends anything.
argument-hint: "[sectors] [countries] [n companies, default 20] [fr|en|auto]   e.g. /find-contacts batteries,hydrogen France,Germany 10"
---
FIND-CONTACTS RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md, skills `application-scoring`, `nermine-writing-style`, `cv-library`. Never asks questions, never
sends, never logs in. Working files go in `outputs/contacts/work_<date>/` (JSON), deliverable in
`outputs/contacts/contacts_<date>.xlsx`.

## 0. Parameters
Parse sectors, countries, N (default `config/search.yaml → defaults.find_contacts.companies` = 20) and language
(default auto). Missing → defaults from `config/search.yaml`. Record them in the run log.

## 1. Exclusion list
Load `config/applied.csv` (company + company_domain), every earlier `outputs/contacts/contacts_*.xlsx` (sheet
Companies, column Company/Website) and `config/search.yaml → exclusions`. Normalise names (lowercase, no legal form,
no accents) and domains.

## 2. Find candidate companies (≈ 1.5 × N)
WebSearch per sector × country with FR/EN keywords from search.yaml, e.g. « centre R&D batteries France stage
ingénieur », "electrolyser manufacturer Germany R&D", "bureau d'études génie des procédés", lists of
start-ups/cleantech clusters, engineering firms (EPC), process industry sites, battery/H₂/energy companies, labs that
take interns. Prefer organisations with R&D or process engineering on site in the target country. Drop excluded ones.

## 3. Research (parallel)
Split candidates into batches of 3–4 and launch `company-researcher` agents in parallel (Agent tool,
`subagent_type: company-researcher`), each with its batch and the exclusion reminder. They return JSON; you write
everything. Keep the best N by apparent fit (a company with no reachable contact at all is dropped unless fewer
than N remain).

## 4. Score
For each company build `{"key", "subscores", "notes"}` with the six anchored criteria of the scoring skill
(offer-less: hiring_signal from intern history/R&D; contact_quality from the best contact found), save
`work_<date>/rows.json`, run `python3 scripts/score.py work_<date>/rows.json -o work_<date>/scored.json`.

## 5. Primary contact, language, email draft
- Primary contact = best-ranked reachable person: chem_eng verified > chem_eng inferred > hr verified > hr inferred
  > ceo (small firms) > careers address. Record `Email confidence` = that address's confidence.
- Language: company's working language (CLAUDE.md); `--lang` overrides.
- Draft the email to that person **by name** following `email-rules.md` (EM-01…EM-12): subject pattern; 120–180
  words; one specific hook from the researcher's `hooks` (with its URL in Sources); one proof point from me.md that
  matches the company; clear request (PFE from 1 Feb 2027, 6 months, 3–9 possible — or a referral); CV attached.
  Generic careers address only → « Madame, Monsieur, » / "Dear Hiring Team," and Notes `GENERIC SALUTATION`.
- Run `checklist.md` (email part); check `wc -w` of the body.

## 6. CV decision
From `scored.json`: `Custom` → run the `/tailor-cv` procedure for that company (keywords = activity + hooks +
required_skills_guess); `Custom (pending)` → library CV now + Notes "custom CV pending"; `Library` →
`python3 scripts/pick_cv.py --lang <lang> "<activity + skills>"` and write the one-line reason in Notes.
CV file = custom PDF or `resumes/library/<id>/original.pdf`.

## 7. Validate
- `python3 scripts/validate_emails.py work_<date>/contacts.json` (every contact with an email): fix every hard
  problem — a "verified" address not found on its page becomes `inferred` (if a pattern source exists) or is removed.
- `python3 scripts/check_links.py --json work_<date>/urls.json` (websites, sources, hook URLs; LinkedIn is only
  format-checked). Replace or drop dead URLs.
- Every row has an Email subject and an Email body draft; `python3 scripts/check_claims.py` on a text file holding
  all drafts → ok (or explain each flag).

## 8. Excel
Build `work_<date>/run.json` with `kind: "contacts"`, `companies` (one object per company, keys = the Companies
columns in `scripts/build_xlsx.py`: Score breakdown = `breakdown` + " | " + notes; Why it fits = 1 line; Sources =
URLs joined by newline; Status "To send") and `contacts` (long format: Company, Name, Role, Category Chem-Eng / HR /
Careers / CEO / Other, Email, Confidence, Source URL, LinkedIn URL). Run
`python3 scripts/build_xlsx.py work_<date>/run.json outputs/contacts/contacts_<date>.xlsx` (it sorts, ranks, formats,
adds the README sheet and re-opens the file). Then reopen it with openpyxl and assert: rows sorted by Score desc,
Rank 1..n, every Email body draft non-empty.

## 9. Log and report
Append to `logs/run_<today>.md`: parameters, search queries used, sources read/blocked, counts (candidates,
researched, kept, contacts found by category and confidence, custom CVs built/pending), validation results, files.
Final message: the top 5 rows (rank, score, company, primary contact + confidence, CV decision) and the xlsx path.
