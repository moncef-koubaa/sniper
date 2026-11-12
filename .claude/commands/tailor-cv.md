---
description: Build a custom one-page LaTeX CV for one company or offer, from the closest library CV, using only facts from profile/me.md. Called by /find-contacts and /find-offers for rows scoring at or above the threshold; can be run alone.
argument-hint: "<company or offer name> [--lang fr|en] [--keywords \"k1, k2\"] [--url <offer url>] [--row <json file>]"
---
TAILOR-CV RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md and the skills `nermine-writing-style` (cv-rules.md) and `cv-library`. Writes only
`resumes/custom/<YYYY-MM-DD>_<Company>/` and a line in `logs/run_<today>.md`.

## 1. Input
- From a pipeline: the row JSON (company/offer, language, extracted keywords, requirements, score breakdown).
- Standalone: company/offer name (+ `--url`): read the offer or company page with WebFetch and extract 8–15 target
  keywords (tools, techniques, domain nouns, the job title) in the target's language. `--lang` overrides the language.
- `<Company>` in paths: ASCII, spaces → `-` (e.g. `Air-Liquide`). Folder exists already → suffix `_2`.

## 2. Choose the base
`python3 scripts/pick_cv.py --lang <lang> "<keywords + requirement text>"` → base = `choice` (same language as the
target; never translate a CV from scratch if a library CV in that language exists — if none exists in that language,
take the closest one in the other language and translate it bullet by bullet, keeping structure and LaTeX).
Copy `resumes/library/<base>/source.tex` to the new folder as `source.tex`.

## 3. Tailor (edit the copied LaTeX only)
Allowed moves, in this order (cv-rules TL-01…TL-06):
1. **Title line and summary** (CV-03, CV-05): pick the 3 courses closest to the target from me.md §2; rewrite the
   « Orientée vers … » sentence with the target's activity in Nermine's words; last sentence « À la recherche d'un
   PFE de 6 mois à partir de février 2027. » (or the target field).
2. **Projects** (TL-01): keep 3–4, most relevant first; swap in a project from me.md §4 with its exact title and
   bullets built from its me.md facts (reuse Nermine's own bullet wording from `writing-samples` / other library
   sources whenever it exists — search them with grep before writing a new bullet).
3. **Bullets**: reorder; reword toward target keywords **only where the fact supports it** (e.g. "battery modelling"
   → "modélisation électrochimique de cellule Li-ion"); choose absolute vs relative results (TL-04); move bold
   keywords to the target's terms (CV-10).
4. **Skills** (CV-18): put the target's group first; within a group, order items by target relevance. Never add a
   tool/technique absent from me.md §5–7. A §5c item stays in the skills list as is; it never moves into a bullet as
   something she did.
5. **Space** (TL-06) if it runs over one page.
Forbidden: any fact, number, tool, employer, date or title not in me.md; `[assumed]` facts; changing the LaTeX
preamble/layout; second page (unless the base has two).

## 4. Build and verify
1. `python3 scripts/build_cv.py resumes/custom/<date>_<Company> --out Moumen_Nermine_CV_<Company>.pdf --png`
   → must print `"ok": true` (1 page, no overfull box, no missing glyph). Not ok → fix (TL-06) and rebuild, max 4 tries;
   still failing → keep the library CV for this row and log the failure.
2. Open `preview.png` with the Read tool and check visually: nothing cut at the bottom, no line overflowing into the
   date column, bold not overused.
3. `python3 scripts/check_claims.py resumes/custom/<date>_<Company>/source.tex` → must be ok (or every flag
   explained in changes.md as a false positive).
4. Run `checklist.md` (CV part).

## 5. changes.md (same folder)
```
# Custom CV — <Company> — <offer title or "spontaneous"> — <date>
Base: resumes/library/<base>/source.tex (pick_cv reason: …)
Target keywords: …
Language: fr|en · Pages: 1 · build_cv ok · check_claims ok
## Changes vs base
- Summary: … → …
- Projects: removed P?, added P? (reason) ; order …
- Bullets: <entry> bullet n reworded "…" → "…" (keyword …) [rule TL-02]
- Skills: …
## Facts used (me.md sections)
- … [src: …]
```

## 6. Return
To the caller: `{"cv_file": "resumes/custom/<date>_<Company>/Moumen_Nermine_CV_<Company>.pdf", "base": "<id>",
"ok": true}`. Standalone: print the same and the path of changes.md.
