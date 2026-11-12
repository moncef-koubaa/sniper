---
name: cv-library
description: Decide which CV Nermine sends for a given company or offer — a ready-made library CV (resumes/library/index.yaml) or a custom one built by /tailor-cv — and explain the choice in one line. Use in /find-contacts, /find-offers and /tailor-cv, and whenever a CV is added to the library.
---

# CV library: pick vs build

## Library
`resumes/library/index.yaml` lists 10 ready-made one-page LaTeX CVs (FR: process, energy, materials,
electrochemistry, water, waste, analytical; EN: process, materials, electrochemistry). Each folder has `source.tex`
(the base for any custom CV), `source.pdf`, `original.pdf` (Nermine's own PDF) and `preview.png`.
"CV1 Process & Energy Engineering" = `process_fr` / `process_en`; "CV2 Materials Science & Functional Chemistry" =
`materials_fr` / `materials_en`.

## Decision (per company/offer row, after scoring)
1. Language = language of the target (CLAUDE.md).
2. `score ≥ custom_cv_threshold` (config/scoring.yaml, default 75) **and** fewer than `max_custom_cvs_per_run`
   custom CVs built in this run → **Custom**: run `/tailor-cv` with the row; its base is the library CV that
   `pick_cv.py` ranks first.
   Over the cap → **Library** CV now, CV decision `Custom (pending)`, Notes `custom CV pending`. Highest scores get
   the custom slots first.
3. Otherwise → **Library**: `python3 scripts/pick_cv.py --lang <fr|en> "<offer text or company activity + keywords>"`
   and use `choice`. You may override the script's pick only with a reason grounded in index.yaml `best_for`
   (e.g. a hydrogen offer scoring equal on process_en and electrochem_en → electrochem_en if it asks for
   electrochemical measurements). Write the one-line reason in the sheet, e.g.
   `Library: electrochem_en — battery ageing offer; best overlap (battery, comsol, electrochemistry)`.
4. CV file column: the PDF path to attach — library: `resumes/library/<id>/source.pdf` (or `original.pdf` if
   Nermine prefers her own export; default `original.pdf` because it is her exact document); custom:
   `resumes/custom/<date>_<company>/Moumen_Nermine_CV_<Company>.pdf`.

## Adding a CV to the library
1. Copy the closest folder to `resumes/library/<new_id>/`, edit `source.tex` (facts from `profile/me.md` only,
   rules in the writing-style skill), or put Nermine's own `.tex` there.
2. `python3 scripts/build_cv.py resumes/library/<new_id> --png` → must print `"ok": true`.
3. Add an entry to `index.yaml` (id, name, sample, language, paper, focus, projects, keywords, best_for).
4. A successful custom CV that Nermine sent and liked can be promoted the same way.
