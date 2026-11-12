---
description: Build or refresh Nermine's full, cited profile (profile/me.md, facts.json, open-questions.md) from every document in profile/inbox/ and writing-samples/. Incremental; --full re-reads everything.
argument-hint: "[--full] [extra file or folder paths ...]"
---
GET-TO-KNOW-ME RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md. This run reads documents and writes only: `profile/me.md`, `profile/facts.json`,
`profile/open-questions.md`, `profile/processed/`, `logs/run_<today>.md`, and (step 7) the writing-style skill
via the /learn-style procedure. It never searches the web and never asks questions.

## 1. Archive
Copy the current `profile/me.md`, `facts.json`, `open-questions.md` to `_archive/<today>/profile/` (skip files
that don't exist).

## 2. Incremental ingestion
Run `python3 scripts/ingest.py $ARGUMENTS` (pass `--full` through if given; extra paths are scanned too).
It hashes every file in `profile/inbox/` and `writing-samples/{cvs,cover-letters,emails}/`, skips hashes already
`ingested` in `profile/processed/manifest.json`, extracts text to `profile/processed/text/`, and prints JSON:
`new` (class, language, pages, text_file), `duplicates`, `needs_visual_read`.
- `needs_visual_read` (images/scans, no tesseract): open each with the Read tool (PDF: `pages` parameter), transcribe
  the text yourself into `profile/processed/text/<sha12>__<name>.txt`, and log "visual read" for it.
- Correct the class if the guess is wrong: cv, letter, email, transcript, report, certificate, recommendation, other.
- Nothing new and no `--full`: say so, write the log line, stop.

## 3. Read and extract facts
Read every new text file completely (reports: all pages). For each fact note: section, wording, `[src: <ID> p.N]`.
Register each new file in the Source legend table of `me.md` with the next free ID (CVnn, CLnn, EMnn, TRnn
transcript, RPnn report, CEnn certificate, RCnn recommendation, LInn LinkedIn, OTnn other) and its date.

## 4. Merge into `profile/me.md` (keep its section order)
1 identity & contact · 2 education (ranks, grades, courses) · 3 internships (company, dates, supervisor, tasks,
tools, results — what *I* did vs what the team did) · 4 academic projects (exact official titles FR/EN, methods,
quantified results) · 5 lab techniques **5a hands-on / 5b trained / 5c studied — never merge these** · 6 software
& programming · 7 standards · 8 languages · 9 extracurriculars & leadership · 10 references (who vouches for what)
· 11 career goals & preferences · 12 constraints (start, duration, mobility, visa).
Rules:
- Every fact keeps its `[src: …]`. Deduplicate: same fact from several files → one line, all sources.
- A technique moves from 5c to 5a only with a document that shows *me operating it* (report method section,
  internship certificate, TP report). A CV skills list is not evidence of operation.
- Conflicts: keep the most recent or most official source (official > report > CV > letter; newer > older), mark
  `[conflict]` in me.md and add/update a Q-entry in open-questions.md.
- Exact project titles: an official title (report cover, transcript) beats a CV title; record older variants.
- A gap answered by a new document: remove `[assumed]`, cite the source, close the Q-entry (move it to a
  "Resolved" section with the date).

## 5. Gaps without blocking
For each important gap (preferred countries, visa, domains to avoid, grades, referees, certificates…): infer the
most likely answer from the documents or the seed context in CLAUDE.md, write it in open-questions.md as
**gap → default assumed → evidence → how to change it**, and tag it `[assumed]` in me.md.

## 6. Regenerate `profile/facts.json`
Same schema as now (identity, constraints, languages, skills[name, category, level hands_on|trained|studied,
evidence, keywords], tools, projects[id, title_fr, title_en, nature, results, keywords, domains], experience,
domains{key: label, evidence, strength 0–1}, standards, gaps_named_in_letters). Every entry must exist in me.md.
Validate: `python3 -c "import json;json.load(open('profile/facts.json'))"`.

## 7. Writing samples → style
If new files were CVs, letters or emails from `writing-samples/`: write their analysis notes in
`writing-samples/analysis/` and update the style rules exactly as `/learn-style` step "new samples" describes; also
add new CVs to `resumes/library/` + `index.yaml` (cv-library skill) and new letters to `config/applied.csv`.

## 8. Close
- `python3 scripts/ingest.py --mark <sha256 ...>` for every file whose facts were merged.
- Append to `logs/run_<today>.md`: documents read (ID, class, method), facts added/changed (count + the important
  ones), conflicts found, assumptions made/resolved.
- Final message: counts, the 3 most important open questions, files written.
