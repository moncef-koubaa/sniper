# Decisions log

Every default I picked without asking. Format: **what** · why · how to change it.

## 2026-11-12 — refactor run

- **D-01 Git: work on a local branch, never push.** All steps are committed on `refactor/personal-pfe-system`.
  The remote `origin` is the public-facing `sniper` package repo, and this branch now contains personal data
  (CVs, letters, profile). · Why: you asked for a commit per step, and pushing personal data is irreversible. ·
  Change: push only after deciding where the personal repo should live (e.g. a private repo:
  `git remote add personal <url> && git push personal refactor/personal-pfe-system`).
- **D-02 The legacy kit stays in place.** `01_install/ … 05_build_sources/`, `03_kit/` are untouched; the new
  system lives at the project root. The only file overwritten is the root `README.md` (archived first in
  `_archive/2026-11-12/README.md`). The pending edits I found were snapshotted in commit `b825f04`. · Why: never
  delete; the kit is still a useful reference (interview prep, ask-me). · Change: move the kit into `_archive/`
  yourself when you no longer need it.
- **D-03 CV sources rebuilt in LaTeX.** The `.tex` sources of your CVs are not in the project. I wrote a template
  matching the PDFs' layout (`resumes/library/_template/`) and transcribed each library CV into it word for word.
  · Why: custom CVs must be built from the same source format (LaTeX), never re-typed in another format. ·
  Change: put your original `.tex` in `resumes/library/<id>/source.tex` (same file name) — every command uses it.
- **D-04 Letters are produced as Markdown + DOCX**, not LaTeX. · Why: your letters are Google Docs exports. ·
  Change: edit `scripts/build_letter.py`.
- **D-05 Originals in `human-cv/` and `human-coverletter/` are copied, not moved.** · Why: never delete. · Change:
  delete those two folders yourself once you are happy with `writing-samples/`.
- **D-06 No OCR engine installed.** `tesseract` is missing. `/get-to-know-me` falls back to Claude reading the
  image directly (Read tool) and logs it. · Change: `sudo apt install tesseract-ocr tesseract-ocr-fra`.
- **D-07 The "hands-on" status of the MIP project and the literature-review projects is treated conservatively**
  (see `profile/open-questions.md` Q-01/Q-02). CVs may reuse your own most recent wording verbatim, but letters and
  emails never upgrade a "studied" item into "hands-on experience". · Change: answer Q-01/Q-02 in
  `profile/open-questions.md`, then run `/get-to-know-me --full`.
- **D-08 Library = the newest CV per focus (10 CVs); 3 superseded versions stay as samples only** (CV08, CV11,
  CV13). Library sources were transcribed word for word with four normalisations, listed in each `source.tex`
  header: summary as a paragraph (CV-04), official project titles (CV-17), "manger" → "Chair/manager" typos fixed,
  French `%` spacing. · Change: edit `resumes/library/index.yaml`.
- **D-09 Library CV attached = `original.pdf`** (your own export) rather than the rebuilt `source.pdf`. · Why: it is
  exactly what you wrote. · Change: cv-library skill step 4.
- **D-10 `config/applied.csv` pre-filled with the 8 letters; `date_applied` = unknown, `status` = applied.** · Change:
  fill dates/outcomes in the CSV (Q-17).
- **D-11 Source IDs in `me.md` are short codes (CV01, CL04 …) with a legend table** instead of full file names in
  every tag. · Why: readability; the legend maps each code to its file. · Change: none needed.
