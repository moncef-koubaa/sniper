---
description: HUNTER run. Covers every available opportunity in one country (no row or search limit), from 01_sources/country_priority.csv, track ALL. An argument overrides.
argument-hint: "[COUNTRY] [TRACK or ALL]"
---
HUNTER RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md. This run finds opportunities. It does not verify contacts, apply, or touch Gmail.

0. CHOOSE THE COUNTRY AND TRACK (I never choose them)
- Track focus is ALL, unless the arguments name a track from 00_profile\TRACKS.md.
- If the arguments name a country, hunt that country and do not change the order file.
- Otherwise read 01_sources\country_priority.csv (rank, country, status, runs, rows_added, last_run, why).
  Take the row with status "active"; if none, the lowest-rank "pending" row, and set it to "active".
- When every row is "exhausted": research the next 15 countries most compatible with my profile
  (working language French or English, visa for a {{NATIONALITY}} student, fit with my tracks, realistic chance),
  leaving out every country already in the file and the countries already hunted before the file existed
  ({{COUNTRIES_HUNTED_BEFORE}}).
  Append them with the next ranks as "pending", each with a one-line why, and take the first.
- Read the previous hunter reports for this country (05_reports\*_hunter_*<country>*.md): continue from the
  sources and tracks they list as remaining.

1. LOAD
tracker.csv, seen.csv, blocked.csv and 01_sources\source_registry.csv. Never add a row whose
(company_domain, project_title) already exists in any of them (tracker_tools.add_rows checks tracker.csv
and seen.csv; check blocked.csv yourself). Skip {{EXCLUDED_ORGS}}.

2. SEARCH THE WHOLE COUNTRY, SOURCE BY SOURCE, TRACK BY TRACK
- Every registry source for this country not searched in the last 7 days.
- Job boards: the claude.ai Indeed connector if it responds, otherwise indeed.<tld> in Chrome with search
  URLs; EURAXESS; the national boards; LinkedIn URLs recorded only.
- Companies first (CLAUDE.md SEARCH SCOPE, changed 20 Oct 2026): industrial companies, SMEs, scale-ups
  and startups in my tracks (their R&D, production, quality and process teams), independent testing labs,
  water and environment operators. Startup sources for the country: incubator and accelerator portfolios,
  deep-tech and cleantech startup lists, the national startup registry, then each company's own careers
  page. An unadvertised company contact (CTO, R&D lead, engineering manager, plant manager) is a row when
  the name and address are verified on a page that was opened.
- Then research institutes and universities (department and group pages, not only job pages), with the
  same rules: never skipped or screened out for being academic.
- Every track in KEYWORDS.md, in the local language as well as English and French. Unadvertised hosts
  count: a named group leader whose work fits is a row.
- For every plausible organisation, open its own careers or internship page rather than trusting the
  aggregator. Aggregator listings for student internships are stale more often than not.
- Subagents (CLAUDE.md PARALLEL WORK): 4 organisations each, JSON rows back. Record each subagent's rows
  (step 5) as soon as it returns, one row at a time. A run cut short by the usage limit loses anything not
  yet recorded.
- The main session runs no WebSearch and no WebFetch itself (changed 17 Oct 2026): every search and every
  page read goes to a subagent. The main session keeps only the Indeed connector, Chrome for my logged-in
  or JavaScript-only boards, launching subagents and the tracker writes. Searching from the main session
  costs about seven times more per call, because its context is many times larger.

3. SCREEN BEFORE RECORDING
Apply CLAUDE.md SCREEN OUT. A screened-out opportunity is still added, status screened_out, reason in notes.

4. EXPAND
For every strong hit: its three nearest competitors, the job board's sister sites, the research group's
collaborators and the companies and startups it works with. {{SCHOOL}} register hosts are anchors: expand around them first.

5. RECORD
Add surviving rows with tracker_tools.add_rows, status discovered (or screened_out), source set,
country and city filled. Fill what you verified; write UNVERIFIED in what you did not. Do not enrich
contacts here. Save each row the moment it is ready (CLAUDE.md TRACKER AFTER EVERY ROW), never only at
the end. Add every new source to source_registry.csv as soon as it yields a row.

6. SOURCES
Update last_searched and rows_yielded in source_registry.csv; add every new source you used.

7. WHEN TO STOP (CLAUDE.md RUN SIZE: no row or search limit)
Cover every available opportunity in the country: every source, every track, every expansion. Keep going
until every source and track for the country is done and the last 20 searches produced no new row. Only
then is the country EXHAUSTED. If the run is cut short (usage limit, full context), the country stays
active and the next run continues from the report's remaining sources and tracks.

8. UPDATE THE ORDER FILE
Back up 01_sources\country_priority.csv to 02_tracker\backups\, then with Python set for this country:
runs +1, rows_added + this run's rows, last_run today, status active or exhausted. (Skip this step when
the country came from the arguments and is not in the file.)

9. REPORT
05_reports\<YYYY-MM-DD>_runNN_hunter_<country>.md (NN = next run number after the highest in 05_reports;
the filename must contain the country in lowercase): rows added, split into company or startup rows and
academic rows (universities, public labs, institutes); if most rows are academic, say so and name the
company and startup sources tried; searches made, rows screened out and why, new sources,
the three strongest finds with one line each, sources and tracks done and remaining, whether the country
is exhausted, and "Country to run next:" (this one again, or the next in the order file).

Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: 0`.
