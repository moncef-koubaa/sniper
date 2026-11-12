---
description: Learn from Nermine's edits. Give it a draft and her edited version (or new samples in writing-samples/); it diffs them, extracts lasting patterns and updates the writing-style rule files, archiving the old version and logging every change.
argument-hint: "<draft path> <edited path>  |  new  (= analyse new files in writing-samples/)"
---
LEARN-STYLE RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md. Writes only: `.claude/skills/nermine-writing-style/*`, `writing-samples/analysis/*`,
`logs/style-changes.md`, `logs/run_<today>.md`, `_archive/<today>/…`. Never asks questions.

## 0. Inputs
- Two paths → **diff mode**: A = my draft, B = Nermine's edited version (PDF, DOCX, TEX, MD, TXT; extract text with
  `scripts/ingest.py`-style tools: `pdftotext -layout`, `unzip -p x.docx word/document.xml`, …).
- `new` or no argument → **new-samples mode**: `python3 scripts/ingest.py --dry-run` and keep the `new` entries under
  `writing-samples/`.
- Also copy B (diff mode) into `writing-samples/<cvs|cover-letters|emails>/` with a dated name so it becomes a sample.

## 1. Archive first
Copy the whole `.claude/skills/nermine-writing-style/` folder to `_archive/<today>/.claude/skills/nermine-writing-style/`
(if that folder already exists today, suffix `_2`, `_3`).

## 2. Diff / analyse
- Diff mode: `diff <(fold -w 100 A.txt) <(fold -w 100 B.txt)` plus a sentence-level comparison. Classify every
  change: wording (verb/noun choice, connector), structure (order, paragraph split), length, salutation/closing,
  formatting (bold, number format), content (fact added/removed — check it against me.md), correction (typo).
- New-samples mode: write one analysis note per new document in `writing-samples/analysis/` in the same format as
  the existing notes (type, language, target, layout, section order, bullet stats via
  `python3 scripts/style_stats.py <file>`, structure, notes) and update `INVENTORY.md`.

## 3. Keep only lasting patterns
A change becomes a rule only if it is (a) a pattern — appears twice or more in this diff, or contradicts a rule that
is not *hard*, or matches what other samples do; and (b) not target-specific (a fact about one company is not a
style rule). One-off fixes (a typo, one fact) → no rule change; note them in the log only.
If B contains a fact absent from me.md → do not learn it as style; add it to `profile/open-questions.md` ("new fact
seen in your edit — run /get-to-know-me with the source").

## 4. Update the rule files directly
- Edit an existing rule when the pattern refines it; add a new rule with the next free ID (never reuse an ID) when
  it is new; for a reversed preference, rewrite the rule and add "(changed <date>, was: …)".
- Adjust strength by counting samples: always ≥ 80 %, usually 50–80 %, variable < 50 % or target-dependent.
- Add 1 short real excerpt to `examples.md` if it is a better anchor than an existing one (keep 2–3 per type/language).
- Update `checklist.md` when a rule is added or removed, and the top-10 list in `SKILL.md` if priorities changed.
- **Hard rules from CLAUDE.md are never weakened** by a sample; a contradiction is logged as such.

## 5. Log
Append to `logs/style-changes.md` one block per run:
```
## <today> — /learn-style <mode> (<files>)
| Rule | Change | Before | After | Evidence |
| CL-12 | strength usually→variable | … | … | B ¶5 drops "salutations distinguées" |
Not learned (one-off): …
Revert: copy _archive/<today>/.claude/skills/nermine-writing-style/ back.
```
Append a summary to `logs/run_<today>.md`. Final message: rules added / edited / strengthened / weakened, one line each.
