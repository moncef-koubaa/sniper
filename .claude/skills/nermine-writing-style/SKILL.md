---
name: nermine-writing-style
description: How Nermine Moumen writes CVs, cover letters and application emails (French and English). Use whenever drafting, tailoring or reviewing any CV, cover letter, spontaneous-application email or follow-up for her PFE search, and whenever /learn-style updates the rules.
---

# Nermine's writing style

Rules extracted on 2026-11-12 from 13 CVs and 8 cover letters (`writing-samples/analysis/` has one note per
document). Rule IDs are stable: cite them in run logs and `changes.md`.

## Files
- `cv-rules.md` — CV-01…CV-21, tailoring TL-01…TL-06, never NV-01…NV-05.
- `cover-letter-rules.md` — CL-01…CL-15, never NV-L1…NV-L5.
- `email-rules.md` — EM-01…EM-12 (no real email samples yet).
- `examples.md` — real excerpts to imitate (2–3 per type and language).
- `checklist.md` — the self-review every draft must pass before it is saved.
- Change history: `logs/style-changes.md` (written by `/learn-style`).

## The rules that matter most

Priority: **hard rules** (CLAUDE.md) > rules marked *always* > *usually* > *variable*.

1. **Facts only from `profile/me.md`**, exact project titles, never a studied technique sold as hands-on (NV-01, NV-02).
2. **CV = one-page LaTeX**, fixed section order, education line followed by a 3-line tailored summary that ends
   with what she is looking for (CV-01, CV-02, CV-04, CV-05).
3. **Bullets: action → tool → object → number**, 10–20 words, impersonal, 2–4 bold keywords; FR nominal
   (« Modélisation… »), EN past tense ("Modeled…") (CV-07…CV-11).
4. **Tailor by swapping projects and promoting matching bullets**, never by adding unsupported keywords (TL-01…TL-05).
5. **Letters: 4 paragraphs** — request (INSAT, specialty, availability, exact offer) → one quantified proof mapped
   explicitly to the offer → the company's concrete strength tied to her profile → one-line motivation; then the
   closing (CL-06…CL-12). No gap sentence (NV-L6).
6. **Real-name salutation** whenever a name exists; generic only with a `GENERIC SALUTATION` flag (CL-04, EM-03).
7. **Availability**: « à partir du 1er février 2027, pour une durée de 6 mois (3 à 9 mois possibles) » (CL-07).
8. **Never mention gaps** in a letter or email: no "new to me", no missing skills; only what she has (NV-L6).
9. **Emails: 120–180 words**, hook + one proof + clear request + CV attached (EM-01…EM-08).
10. **Language** follows the offer/company; FR in feminine forms and French number format (CL-15, CL-05, CV-12).

## How to use
- Drafting: read the rule file for the document type + `examples.md`, draft, then run `checklist.md`.
- Choosing the base CV: see the `cv-library` skill.
- Never edit these files by hand from a command other than `/learn-style` (or `/get-to-know-me` step 7, which
  follows the /learn-style procedure); each edit archives the previous version and logs to `logs/style-changes.md`.
