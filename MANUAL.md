# PFE Application System — User Manual & Onboarding Guide

This manual explains what the system does, how to install it, how to use it every week, and how to hand it over to
someone new. The quick command list is in [README.md](README.md) → USAGE; the rules every session follows are in
[CLAUDE.md](CLAUDE.md).

---

## 1. What the system is

A folder that Claude Code works in. You type a slash command (`/find-offers`, `/find-contacts`, …) and Claude:

1. knows you — a cited profile built from your own CVs, letters and documents (`profile/me.md`);
2. writes like you — style rules learned from your past CVs and cover letters (writing-style skill);
3. finds opportunities — posted PFE offers and companies for spontaneous applications, in France and Germany;
4. ranks them — one scoring rubric out of 100, with the reason for every point;
5. prepares the application — a CV (ready-made or tailored, one page, LaTeX), a cover letter or an email draft;
6. hands you a spreadsheet — sorted by priority, with everything you need to send.

**What it never does:** send an email, submit a form, log in to a site, invent a fact about you, present a guessed
email address as verified, or mention a gap in your profile. **You** review and send everything.

### The pipeline at a glance

```
your documents ──► /get-to-know-me ──► profile/me.md (facts, cited)  ─┐
your CVs+letters ─► writing-style rules + CV library ─────────────────┤
                                                                      ▼
            /find-offers  (posted offers)          /find-contacts  (spontaneous)
                 │ search → verify live → dedup → score (0-100) → CV decision
                 │                                     │
          score ≥ 75 → /tailor-cv (custom CV)    below → best library CV
          score ≥ 60 → cover letter              every company → email draft
                 ▼                                     ▼
     outputs/offers/offers_<date>.xlsx    outputs/contacts/contacts_<date>.xlsx
                                 ▼
                     YOU review, edit, send, update Status
                                 ▼
             /learn-style learns from your edits; config/applied.csv grows
```

---

## 2. Installation (once per computer)

Tested on Linux. On Windows, use **WSL2 (Ubuntu)** for an identical setup, or native Windows once the three
Windows fixes are applied (path separator in `build_cv.py`, UTF-8 file reading, MX lookup without `host`).

| Tool | Why | Linux / WSL install |
|---|---|---|
| Claude Code | runs the commands | see claude.com/claude-code |
| Python 3 + `openpyxl`, `pyyaml` | scripts, Excel files | `sudo apt install python3-openpyxl python3-yaml` |
| Poppler (`pdftotext`, `pdfinfo`, `pdftoppm`) | read PDFs, preview CVs | `sudo apt install poppler-utils` |
| LaTeX (`pdflatex`) | build CVs | `sudo apt install texlive-latex-extra texlive-fonts-recommended` (or TinyTeX) |
| LibreOffice | letters → DOCX/PDF | `sudo apt install libreoffice` |
| `host` (dnsutils) | email domain checks | `sudo apt install dnsutils` |
| Tesseract (optional) | scanned documents | `sudo apt install tesseract-ocr tesseract-ocr-fra` |

**Check the install** (from the project folder):

```bash
python3 scripts/score.py --selftest                     # → selftest ok
python3 scripts/build_cv.py resumes/library/process_fr   # → "ok": true
python3 scripts/ingest.py --dry-run                      # → JSON report, no error
```

Then open Claude Code in the folder (`claude`) and type `/` — the five commands must appear in the list.

---

## 3. Onboarding someone

There are two cases. Pick the one that matches.

### Case A — the same person on a new computer (or a teammate helping her)

1. Copy the whole folder (or `git clone` it from a **private** repository — see §10).
2. Install the tools (§2) and run the three checks.
3. Read, in this order: this manual → `profile/open-questions.md` → the latest `outputs/*/…xlsx`.
4. Done: the profile, style rules, CV library and history travel with the folder.

### Case B — a new person who wants their own system

The system is personalised: the profile, writing samples, CV library, style rules and history all belong to the
current owner. A new person keeps the **engine** and replaces the **data**. Plan about 2 hours.

**Step 1 — Make a clean copy (never work on top of someone else's data).**
Copy the folder, then move the previous owner's data into an archive inside the copy, so nothing is lost by accident:

```bash
D=_archive/$(date +%F)_previous-owner
mkdir -p "$D"
for p in profile writing-samples resumes/custom outputs logs human-cv human-coverletter \
         config/applied.csv .claude/skills/nermine-writing-style; do
  [ -e "$p" ] && mkdir -p "$D/$(dirname "$p")" && mv "$p" "$D/$p"
done
```

Then delete that archive from the copy once you have checked it (it holds the previous owner's personal data and must
not be shared further). Keep `resumes/library/_template/` — move only the CV folders inside `resumes/library/`
(and empty `index.yaml`'s `cvs:` list).

**Step 2 — Recreate the empty folders and the files the engine needs.**

```bash
mkdir -p profile/inbox profile/processed writing-samples/{cvs,cover-letters,emails,analysis} \
         resumes/custom outputs/{contacts,offers,letters} logs
printf 'company,company_domain,offer_title,country,city,date_applied,channel,language,cv_used,letter_file,status,source,notes\n' > config/applied.csv
```

**Step 3 — Personalise the rules (search-and-replace the previous owner's details).**

| File | What to change |
|---|---|
| `CLAUDE.md` | title, "Who I am", contact line, availability dates, domains |
| `config/search.yaml` | countries, sectors, keywords, sources, exclusions |
| `config/scoring.yaml` | `strategic_sectors`, `feasibility.ideal_start`, durations; weights if wanted |
| `.claude/skills/<name>-writing-style/` | create it with the new name (Step 5 fills it); then replace `nermine-writing-style` by the new name in `CLAUDE.md`, `README.md` and the four commands `find-contacts`, `find-offers`, `learn-style`, `tailor-cv` |
| `scripts/build_cv.py`, `scripts/build_letter.py` | output file names (`Moumen_Nermine_CV_…`) |
| `.claude/skills/application-scoring`, `cv-library`, `.claude/agents/company-researcher.md`, the commands | the owner's name where it appears (`grep -rn "Nermine" .claude scripts`) |

Tip: ask Claude Code to do this step — "Personalise this system for <name>: replace every reference to the previous
owner using MANUAL.md §3 Case B, archive before editing." It follows the archive rule automatically.

**Step 4 — Feed the profile.** Put everything about the new person into the right folders:

| Put in | What |
|---|---|
| `writing-samples/cvs/` | every CV version they ever wrote (PDF, DOCX, TEX) |
| `writing-samples/cover-letters/` | every cover letter, FR and EN |
| `writing-samples/emails/` | application emails (paste into `.txt`/`.eml`) |
| `profile/inbox/` | transcripts, internship reports, certificates, recommendation letters, LinkedIn export, scans |

Then run `/get-to-know-me --full`. Read `profile/me.md` and `profile/open-questions.md` **with the person**: correct
every wrong fact, answer the questions under each entry, and re-run `/get-to-know-me`.
The most important answers: which techniques they really operated (hands-on) vs only studied, nationality/visa,
target countries, start date and duration.

**Step 5 — Learn their style.** Run `/learn-style new`. It writes one analysis note per sample and builds the
numbered rules (CV-xx, CL-xx, EM-xx). Open `.claude/skills/<name>-writing-style/SKILL.md` with the person and check
the top-10 rules sound like them.

**Step 6 — Build their CV library.**
- If their CVs are LaTeX: put each `.tex` in `resumes/library/<id>/source.tex`.
- If not: ask Claude to "rebuild each CV in resumes/library from writing-samples/cvs using the LaTeX template, word
  for word". (Custom CVs are always built from the library sources, so a library is required.)
- For each: `python3 scripts/build_cv.py resumes/library/<id> --png` → `"ok": true`, then add an entry to
  `resumes/library/index.yaml` (focus, keywords, language, best_for).

**Step 7 — Dry run together.** `/find-offers <their domains> <country> 5` and `/find-contacts <sector> <country> 3`.
Open both spreadsheets with the person, walk through §6 and §7 below, and send nothing until they have reviewed
one complete application end to end.

**Onboarding done when:** the checks of §2 pass, `me.md` has no wrong fact, the style rules were validated by the
person, the library builds, and one test run was reviewed together.

---

## 4. The commands

| Command | Use it when | Typical call | Takes | Writes |
|---|---|---|---|---|
| `/get-to-know-me` | you add documents, or answer an open question | `/get-to-know-me` · `--full` re-reads all | 5–20 min | `profile/me.md`, `facts.json`, `open-questions.md` |
| `/find-offers` | weekly, to catch new postings | `/find-offers "batteries, hydrogène" France,Germany 15` | 20–60 min | `outputs/offers/offers_<date>.xlsx`, letters, custom CVs |
| `/find-contacts` | weekly or every two weeks, for spontaneous applications | `/find-contacts batteries,hydrogen Germany 10` | 20–60 min | `outputs/contacts/contacts_<date>.xlsx`, custom CVs |
| `/tailor-cv` | you want a custom CV for one target outside a run | `/tailor-cv "Air Liquide" --lang fr --url https://…` | 3–10 min | `resumes/custom/<date>_<Company>/` |
| `/learn-style` | after you edited a draft, or added samples | `/learn-style outputs/letters/X_fr.md ~/Desktop/X_final.docx` · `/learn-style new` | 5 min | style rules, `logs/style-changes.md` |

Arguments are optional; missing ones come from `config/search.yaml`. Each run appends to `logs/run_<date>.md`.

---

## 5. A typical week

| When | Do |
|---|---|
| Monday | `/find-offers` (default countries). Open the sheet, send the green rows first, and any row highlighted red (deadline ≤ 7 days). |
| Wednesday | `/find-contacts` for one sector + one country. Send the emails you approve. |
| After sending | In the sheet: Status → *Sent*, Date sent, Follow-up date (+10 working days). Add a line per application to `config/applied.csv`. |
| When you edit a draft a lot | `/learn-style <draft> <your version>` so the next drafts need fewer edits. |
| New document (grades, certificate, report) | drop it in `profile/inbox/`, run `/get-to-know-me`. |

---

## 6. Reading the spreadsheets

Both files: row 2 = top priority; frozen header; filters on every column; a README sheet repeats the weights.

| Column | Meaning |
|---|---|
| **Score** | 0–100. Green ≥ 75 (custom CV built), amber 60–74, grey < 60. |
| **Score breakdown** | points per criterion (Domain /30, Skills /20, Feasibility /15, Hiring /15, Contact /10, Strategic /10) then the one-line reason for each. If you disagree with a reason, that is the thing to fix (profile or config). |
| **CV decision** | *Custom* (built for this target) · *Custom (pending)* (over the per-run cap; library CV meanwhile) · *Library* (reason in Notes). |
| **CV file / Cover letter file** | the exact files to attach. |
| **Email confidence** (contacts) | **verified** = the address is printed on the page in *Sources*; **inferred** = built from the company's confirmed format, *not verified* — double-check before sending; empty = no address found. |
| **Primary contact / Email subject / Email body draft** (contacts) | who to write to and the ready draft (plain text, 120–180 words). |
| **Gaps (honest)** (offers) | private note for you about what the offer asks that you lack. Never copied into a letter. |
| **Notes** | anything to check before sending: `GENERIC SALUTATION`, uncertain names, deadlines, assumptions. |
| **Status** | dropdown you maintain: To send / Sent / Followed up / Replied / Rejected / Interview. |

---

## 7. Before you press "send" (human checklist)

1. Open the **CV PDF** — one page, right language, nothing that isn't true.
2. Read the **letter or email** aloud once. Edit freely; then feed your version to `/learn-style`.
3. **Salutation** uses a real name? If Notes says `GENERIC SALUTATION`, a quick look on the team page may find one.
4. **Email confidence**: if *inferred*, consider the careers address or the portal instead.
5. **Notes** column: resolve every "CHECK BEFORE SENDING".
6. **Deadline** and application method (portal vs email) as stated in the row.
7. After sending: Status, Date sent, Follow-up date, and one line in `config/applied.csv`.

---

## 8. Customising

| I want to… | Edit | Then |
|---|---|---|
| change which offers get a custom CV | `config/scoring.yaml` → `custom_cv_threshold` | `python3 scripts/score.py --selftest` |
| allow more custom CVs per run | `max_custom_cvs_per_run` | — |
| get letters for more/fewer offers | `cover_letter_threshold` | — |
| weigh domain fit vs feasibility differently | `weights` (sum must be 100) | selftest |
| add countries / sources / keywords | `config/search.yaml` | — |
| never see a company again | `config/search.yaml` → `exclusions.organisations`, or a line in `applied.csv` | — |
| change how letters are written | edit a draft and run `/learn-style`; or ask Claude to change a rule (it archives and logs) | check `logs/style-changes.md` |
| add or fix a fact about me | drop the source document in `profile/inbox/` or answer in `open-questions.md` | `/get-to-know-me` |
| add a ready-made CV | `resumes/library/<id>/source.tex` + `index.yaml` | `python3 scripts/build_cv.py resumes/library/<id> --png` |

---

## 9. The rules the system always follows

(Full list in `CLAUDE.md`.)

- Every fact in a CV, letter or email comes from `profile/me.md`; `[assumed]` facts are never stated.
- Techniques only *studied* are never presented as *hands-on*.
- No gap is ever mentioned in a letter or email.
- Nothing is sent, submitted, or logged into. No LinkedIn scraping.
- Emails are *verified* only when printed on a public page; otherwise *inferred* from a confirmed pattern, or absent.
- Nothing is deleted or overwritten: replaced files go to `_archive/<date>/`.
- Missing information never blocks a run: Claude picks a default and records it in `logs/decisions.md`.

---

## 10. Files, history and privacy

```
CLAUDE.md, README.md, MANUAL.md   rules, quick usage, this manual
.claude/commands/                 the five commands
.claude/skills/                   writing style, scoring, CV library
.claude/agents/                   company-researcher (parallel research)
profile/                          inbox/ → me.md, facts.json, open-questions.md
writing-samples/                  your CVs, letters, emails + analysis notes
resumes/library/ | custom/        ready-made CVs (LaTeX) | generated CVs
outputs/                          offers/, contacts/ spreadsheets, letters/
config/                           scoring.yaml, search.yaml, applied.csv
scripts/                          the deterministic tools Claude calls
logs/                             audit, decisions, run_<date>, style-changes
_archive/<date>/                  previous versions of anything replaced
```

- **Git:** commit after a run if you like history (`git add -A && git commit -m "run <date>"`).
- **Privacy:** the folder contains personal data (CVs, phone, grades). Push only to a **private** repository you
  control. The `origin` remote of the original package is public-facing — do not push personal branches there.
- When onboarding someone else, never give them a copy that still contains the previous owner's data (§3 Case B, Step 1).

---

## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| A command doesn't appear after `/` | Claude Code must be opened in this folder; check `.claude/commands/` exists. |
| `build_cv.py` prints `"ok": false` with `pages: 2` or overfull boxes | Normal during tailoring — Claude shortens bullets and rebuilds. Running it yourself: shorten the longest bullet or drop the 4th project. |
| `pdflatex` / `soffice` / `pdftotext` not found | Tool missing or not on PATH (§2). |
| Excel file "locked" / PermissionError | Close it in Excel/LibreOffice and re-run the step. |
| A run stopped half-way (usage limit, closed terminal) | Re-run the same command; finished outputs are kept, the log says what was done. |
| Most offers are "dead" | Normal: job boards keep stale pages. The run only keeps live offers; widen keywords or countries. |
| A draft states something untrue | Fix the fact in `profile/me.md` via `/get-to-know-me` (or open-questions), then re-draft — never patch only the letter. |
| Letters drift from your style | Run `/learn-style` on your corrected versions; review `logs/style-changes.md`. |
