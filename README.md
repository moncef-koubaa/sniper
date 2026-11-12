# PFE 2027 — Nermine Moumen

A personal Claude Code system for finding a 6-month PFE (from 1 February 2027) in **France and Germany**, in
process engineering, electrochemistry/batteries, hydrogen, LCA and related fields. It builds a cited profile from
your documents, writes in your style, finds offers and companies, scores them with one rubric, tailors LaTeX CVs and
drafts letters and emails. **It never sends anything**: you send.

Rules for every session: [CLAUDE.md](CLAUDE.md). What changed in the refactor: [logs/audit.md](logs/audit.md),
[logs/decisions.md](logs/decisions.md). The old generic "sniper" kit is still here, untouched, in `01_install/` …
`05_build_sources/` and `03_kit/` (reference only); the previous README is in `_archive/2026-11-12/README.md`.

## USAGE

Open Claude Code in this folder (`claude`), then type a command.

| Command | What it does | Example | Output |
|---|---|---|---|
| `/get-to-know-me` | Reads every new document in `profile/inbox/` and `writing-samples/` (hash-based: only new files), updates your cited profile | `/get-to-know-me` · `/get-to-know-me --full` · `/get-to-know-me ~/Downloads/releve_notes.pdf` | `profile/me.md`, `profile/facts.json`, `profile/open-questions.md`, `logs/run_<date>.md` |
| `/find-offers` | Searches posted PFE / master-thesis offers, checks they are live, dedups, scores, picks or builds the CV, drafts a letter for every offer ≥ 60 | `/find-offers "batteries, hydrogène" France,Germany 15` | `outputs/offers/offers_<date>.xlsx`, `outputs/letters/*.md/.docx/.pdf`, `resumes/custom/…` |
| `/find-contacts` | Spontaneous applications: finds companies, public professional contacts (verified vs pattern-inferred emails), scores, drafts one email per company to a named person | `/find-contacts batteries,hydrogen France,Germany 10` | `outputs/contacts/contacts_<date>.xlsx`, `resumes/custom/…` |
| `/tailor-cv` | One custom one-page LaTeX CV from the closest library CV (called automatically for scores ≥ 75) | `/tailor-cv "Air Liquide" --lang fr --url https://…` | `resumes/custom/<date>_<Company>/` (source.tex, PDF, changes.md) |
| `/learn-style` | Learns from your edits: give it my draft and your corrected version, or drop new samples in `writing-samples/` | `/learn-style outputs/letters/X_fr.md ~/Desktop/X_fr_final.docx` · `/learn-style new` | updated rules in `.claude/skills/nermine-writing-style/`, `logs/style-changes.md` |

### Reading the spreadsheets
- Row 2 is your top priority (sorted by **Score**, 0–100). **Score breakdown** shows the points per criterion and the
  reason for each. Green ≥ 75 (custom CV built), amber 60–74, grey < 60; in the offers sheet a red row means the
  deadline is within 7 days.
- **Email confidence**: `verified` = the address is printed on the source page (URL in Sources); `inferred` = built
  from a confirmed company pattern — not verified. `GENERIC SALUTATION` in Notes = no named person was found.
- **Status** is a dropdown (To send / Sent / Followed up / Replied / Rejected / Interview): update it yourself.
  After you apply, add a line to `config/applied.csv` so later runs skip that company/offer.

### Changing the threshold and weights
Edit `config/scoring.yaml`: `weights` (must sum to 100), `custom_cv_threshold` (default 75),
`max_custom_cvs_per_run` (5), `cover_letter_threshold` (60), `strategic_sectors`. Check with
`python3 scripts/score.py --selftest`. Countries, sectors, keywords, sources and exclusions are in
`config/search.yaml` (currently France + Germany; other countries are commented out).

### Adding a CV to the library
1. Copy the closest folder in `resumes/library/` to a new `<id>/` folder and edit `source.tex` (or drop your own
   `.tex` there — your originals always win over my rebuilt sources).
2. `python3 scripts/build_cv.py resumes/library/<id> --png` → must print `"ok": true` (one page, no overflow).
3. Add an entry to `resumes/library/index.yaml` (focus, keywords, language, best_for).
Also drop the PDF in `writing-samples/cvs/` and run `/learn-style new` so its style is learned.

### Adding documents about you
Drop anything (transcripts, internship reports, certificates, recommendation letters, LinkedIn export, scans) into
`profile/inbox/` and run `/get-to-know-me`. Answer the questions in `profile/open-questions.md` the same way (write the
answer under the question, then re-run).

## Layout
```
CLAUDE.md                      rules + pointers
.claude/commands/              get-to-know-me, find-contacts, find-offers, tailor-cv, learn-style
.claude/skills/                nermine-writing-style, application-scoring, cv-library
.claude/agents/                company-researcher (parallel company research, returns JSON)
profile/                       inbox/, processed/manifest.json, me.md, facts.json, open-questions.md
writing-samples/               cvs/, cover-letters/, emails/, analysis/
resumes/library/               10 LaTeX CVs + index.yaml + _template/nermine-cv.sty
resumes/custom/                generated CVs (one folder per company)
outputs/                       contacts/, offers/, letters/
config/                        scoring.yaml, search.yaml, applied.csv
scripts/                       ingest, score, pick_cv, build_cv, cv_blocks, build_letter, build_xlsx,
                               check_links, validate_emails, check_claims, style_stats
logs/                          audit, decisions, run_<date>, style-changes
_archive/<date>/               copies of anything replaced
```

## Requirements
Python 3 with `openpyxl`, `pyyaml`; poppler (`pdftotext`, `pdfinfo`, `pdftoppm`); a LaTeX distribution with
`pdflatex` (TinyTeX works); LibreOffice for DOCX/PDF letters; `host` (DNS) for email checks. Optional: `tesseract-ocr`
for scanned documents.
