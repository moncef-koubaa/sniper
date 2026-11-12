# Phase 0 audit (read only) — 2026-11-12

Scope: everything under `sniper/` at commit `59033bc` plus the pending working-tree edits (snapshotted in
commit `b825f04` on branch `refactor/personal-pfe-system`).

## 1. What the project contains

| Area | Path | What it is | State |
|---|---|---|---|
| Package docs | `README.md`, `00_START_HERE.md`, `MANIFEST.txt`, `PERSONALISE.md`, `VERSION`, `CHANGELOG.md` | Docs for "sniper", a **generic, placeholder-based** PFE campaign kit meant to be installed for any student | Generic; no personal data; never installed for Nermine |
| Installer | `01_install/` | `install.sh` / `install.ps1`, `requirements.txt`, `package.json`, `.env.example` | Generic; works but heavy (Chrome, Gmail connector) |
| Setup prompt | `02_setup_prompt/` | One-time prompt that fills `{{PLACEHOLDERS}}`, `answers_TEMPLATE.json`, `fill_placeholders.py` | Generic; never run (no `answers.json`) |
| Campaign template | `03_kit/campaign/` | `CLAUDE.md` (409 lines, all `{{PLACEHOLDER}}`), 9 commands in `.claude/commands/`, `settings.json`, tracker CSVs + `tracker_tools.py` (1285 lines), `build.py` (DOCX CV/letter builder), `scheduler/` helpers, interview-deck builder | Template only: every CSV has a header row and no data; `PROFILE.md`, `DEFENSIBLE_CLAIMS.md`, `CV_MASTER_V2.md`, `LETTER_MASTER.md` are 3–5-line stubs |
| Guides | `04_runbook_and_guides/` | PDFs/DOCX of the runbook | Generic |
| Build sources | `05_build_sources/` | Scripts that regenerate the kit and the guides | Generic |
| **Nermine's CVs** | `human-cv/` | 14 PDFs (13 unique; `CV_trait_eaux (1).pdf` is byte-identical to `CV_trait_eaux.pdf`) | Real, 1 page each |
| **Nermine's letters** | `human-coverletter/` | 8 PDF cover letters (6 FR-titled files, 4 written in FR, 4 in EN) | Real, 1 page each |

Not present anywhere: a root `CLAUDE.md`, a root `.claude/`, any `.claude/skills/`, any `.claude/agents/`,
any `get-to-know-me` command (the closest equivalent is the one-time prompt **S0 PROFILE** inside
`05_build_sources/one_time_prompts.py`), any LaTeX or DOCX source for Nermine's CVs, any Excel tracker with data,
any transcript / report / certificate / recommendation letter.

## 2. Resume source format (decisive for `/tailor-cv`)

- All 13 CVs: **LaTeX**, compiled with **pdfTeX 1.40.28** in an online editor (`Creator: OpenAI Prism`).
  Two template families, same visual design (Jake's-resume style: centred name, `\titlerule` section headings,
  bold keywords inside bullets, right-aligned dates):
  - **FR family** (`Moumen Nermine` order, US-letter, T1 font encoding → `SFRM/SFBX` fonts): procédés, Énergie,
    Matériaux, Électrochimie, trait_eaux, 5, 6, 7, MaterialsS (EN text but FR template).
  - **EN family** (`Nermine Moumen` order, A4, OT1/CM fonts, italic dates): CV_Process, CV_4, 3_, Electrochemistry.
- **The `.tex` sources are not in the project.** Custom CVs must stay LaTeX → I rebuilt a LaTeX template that
  reproduces the layout (`resumes/library/_template/`) and transcribed each library CV into it. See
  `logs/decisions.md` D-03: drop the original `.tex` files into `resumes/library/<id>/` and they win.
- Cover letters: **Google Docs** exports (`Skia/PDF … Google Docs Renderer`), Times-like serif, justified, A4.
  New letters are therefore produced as `.md` (editable) + `.docx` (open in Google Docs/Word) — no LaTeX.

## 3. Existing commands and skills

| Command | What it does | Reads | Writes | Broken / generic | Decision |
|---|---|---|---|---|---|
| `/pfe-hunter` | Country-by-country search for opportunities, all tracks | tracker.csv, seen.csv, country_priority.csv, source_registry.csv, TRACKS.md | tracker rows via tracker_tools | All `{{PLACEHOLDER}}`; depends on empty TRACKS/KEYWORDS; no scoring rubric (free-text `match_score`); no Excel output per run | **Replace** → `/find-offers` (posted offers) + `/find-contacts` (companies); keep its source list ideas in `config/search.yaml` |
| `/pfe-checker` | Verifies contacts/offers, scores rows | tracker.csv, TRACKS.md | tracker rows | Generic; scoring is ad hoc; mixes verification and scoring | **Merge** → contact verification rules go into `/find-contacts` + `scripts/validate_emails.py`; offer liveness into `/find-offers` + `scripts/check_links.py`; scoring into `application-scoring` skill |
| `/pfe-applier` | Builds DOCX CV+letter, fills portals, **sends emails** (50/day cap) | tracker, specs JSON, CV_MASTER_V2.docx | Gmail drafts + **sent mail**, portals | Conflicts with the new rule "never send anything"; DOCX master ≠ her LaTeX CVs; portal automation | **Replace** → `/tailor-cv` (LaTeX, same source format) + letters drafted inside `/find-offers`/`/find-contacts`; no sending |
| `/pfe-send`, `/pfe-send-held` | Sends Gmail drafts | Gmail, tracker | sent mail | Sending is out of scope now | **Retire** (archived, not ported) |
| `/pfe-inbox` | Reads Gmail, replies, follow-ups | Gmail | tracker, Gmail | Auto-replies conflict with "never send"; needs Gmail connector | **Retire** for now (archived); Status/Follow-up columns in the Excel sheets replace its tracking role |
| `/pfe-cleanup` | Monthly tracker archiving | tracker CSVs | archive CSVs | Tied to the old tracker | **Retire** (dedup now uses `config/applied.csv` + previous sheets) |
| `/pfe-interview-prep` | Interview prep pack | Gmail, tracker, reports | interviews/ | Generic but valuable; out of this refactor's scope | **Keep in legacy kit** (unchanged); can be ported later onto `profile/me.md` |
| `/ask-me` | Explains a setup step | sniper guides | nothing | Fine | **Keep in legacy kit** (unchanged) |
| S0 PROFILE (one-time prompt) | Builds PROFILE.md / DEFENSIBLE_CLAIMS.md / TRACKS.md / KEYWORDS.md | `my documents/` | 00_profile/ | One-shot, no incremental ingestion, no citations per fact, no facts.json | **Replace** → `/get-to-know-me` (incremental, hashed, cited, hands-on vs studied split) |
| `tracker_tools.py` | CSV tracker library + `export_xlsx` | tracker CSVs | CSV/XLSX | Works, but schema is the old pipeline's | **Keep in legacy kit**; new pipelines use `scripts/build_xlsx.py` (columns required by the brief) |
| `build.py` | DOCX CV/letter builder | CV_MASTER_V2.docx | DOCX/PDF | Wrong source format for her CVs | **Replace** → `scripts/build_cv.py` (LaTeX compile + 1-page check) |
| Skills / agents | — | — | — | None exist | **New**: 3 skills + 1 agent |

## 4. Mapping current → target structure

| Current | Target | How |
|---|---|---|
| `human-cv/*.pdf` | `writing-samples/cvs/` (all 13 unique) + `resumes/library/<id>/` (LaTeX source + PDF) + `resumes/library/index.yaml` | copied (originals left in place) |
| `human-coverletter/*.pdf` | `writing-samples/cover-letters/` | copied (originals left in place) |
| S0 PROFILE + `00_profile/*.md` stubs | `/get-to-know-me` → `profile/me.md`, `profile/facts.json`, `profile/open-questions.md`, `profile/processed/manifest.json` | rebuilt |
| `03_kit/campaign/CLAUDE.md` | root `CLAUDE.md` (personal, ~150 lines) | rewritten; the "never invent", contact-confidence and login/CAPTCHA rules carried over |
| `/pfe-hunter` + `/pfe-checker` | `/find-offers`, `/find-contacts`, `.claude/agents/company-researcher.md` | rebuilt |
| `/pfe-applier` + `build.py` | `/tailor-cv` + `scripts/build_cv.py` | rebuilt (LaTeX) |
| free-text `match_score` | `application-scoring` skill + `config/scoring.yaml` + `scripts/score.py` | new |
| `01_sources/source_registry.csv` (empty) | `config/search.yaml` | new, populated |
| tracker CSVs (empty) | `config/applied.csv` + `outputs/*/…xlsx` | new |
| — | `nermine-writing-style` skill, `/learn-style`, `cv-library` skill | new |
| `01_install … 05_build_sources`, `03_kit/` | **left in place, untouched** (legacy reference kit) | nothing deleted; root `README.md` archived to `_archive/2026-11-12/` before being rewritten |

## 5. Risks noticed during the audit

1. **Honesty conflicts across her own documents** (details in `profile/open-questions.md`):
   - MIP project: CV_4 (17 Sep) says *"Reviewed … Evaluated three drug delivery case studies"*; later CVs say
     *"Synthèse et caractérisation d'un MIP …"*; the CEA Saclay letter says *"hands-on experience with sol-gel-type
     nanomaterial synthesis"*.
   - UTC letter: *"hands-on experience with Raman spectroscopy and SEM, developed during a literature review project"*.
   - SEGULA RMSE result is stated as "202,13 → 40,5 mV" in some CVs and "80 %" in others (consistent: −80 %).
   - AGIL dates: 07/2025–07/2025 (Sep CVs) vs 07/2025–08/2025 (11 Nov CV).
   - Availability: CEA letter says "janvier/février **2026**" (typo); others 2027.
2. The git remote `origin` points to GitHub (`sniper` package repo, which advertises "holds no personal data").
   This refactor commits personal data **on a local branch only**. Nothing has been pushed (D-01).
3. `tesseract` (OCR) is not installed; no scanned documents exist yet, so this only matters for future inbox files (D-06).
