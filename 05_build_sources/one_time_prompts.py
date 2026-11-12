"""The one-time campaign prompts (PATH B), Claude Code versions. Used by make_runbook.py."""

S0 = r"""S0 PROFILE. One-time, new campaign only. Follow CLAUDE.md.
Read every source document in ..\my documents\: the master CV, the research and internship reports,
the recommendation letters, the {{SCHOOL}} internship agreement templates. Do not search the web
and do not apply to anything.

Produce four documents, in this order:

1. 00_profile\PROFILE.md
   My verified academic background, coursework (module names), technical skills, instruments and software I
   have personally operated, internships, research, languages, achievements, practical constraints
   (visa, dates, the convention de stage and what its articles commit a host to). For every research and
   internship entry, two separate lines: what the team or project did, and what I personally did. If a
   file is ambiguous about which is which, list it under OPEN QUESTIONS at the end instead of guessing.
   Recompute each year's average from the module marks to prove the readings.

2. 00_profile\DEFENSIBLE_CLAIMS.md
   Every claim a letter may make, with its source, and every claim it must not make (inconsistencies
   between the CV, the reports and the letters, numbers that differ between documents).

3. 00_profile\TRACKS.md
   Six to ten PFE directions my profile genuinely supports. For each: the direction, the three strongest
   pieces of evidence from my files, my honest weaknesses for it, the kinds of organisation that host it,
   and a realistic assessment of my chances against a European or Asian engineering student applying for
   the same thing. Rank by realistic selection probability, not by how interesting the direction is.
   Analytical and materials work must not rank below process engineering unless the evidence says so.

4. 00_profile\KEYWORDS.md
   For each track, search strings in English, French and German (and the local languages of the countries
   in 01_sources\country_priority.csv), split into job titles, project and problem descriptions, and
   technology terms. Include the terms used on company career pages, which differ from job-board terms.

5. 01_sources\SOURCES.md
   At least 60 places to search: national job boards, engineering boards, university and research portals,
   government internship schemes, sector associations, the graduate pages of large employers in my
   tracks, and startup sources: incubator and accelerator portfolios, deep-tech and cleantech startup
   lists, national startup registries. Companies and startups come first in each country (CLAUDE.md
   SEARCH SCOPE); university and research portals stay in. Group by country, starting with the countries in country_priority.csv. Mark which need an account.

Finish with the three things in my profile that most need fixing before applications go out.
Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: 0`."""

INIT = r"""CAMPAIGN INIT. One-time, new campaign only, after S0 and after the kit is installed. Follow CLAUDE.md.

1. Check the folder tree: 00_profile 01_sources 02_tracker (backups) 03_documents 04_outbound
   (_gen\run34\specs) 05_reports (logs). Create what is missing.

2. Create the data files with their header row only, using the constants in 02_tracker\tracker_tools.py:
   - 02_tracker\tracker.csv: tracker_tools.HEADER (40 columns)
   - 02_tracker\blocked.csv: the same 40 columns
   - 02_tracker\responses.csv: tracker_tools.RESPONSES_HEADER
   - 02_tracker\seen.csv: tracker_tools.SEEN_HEADER
   - 02_tracker\id_counter.txt: 0
   - 02_tracker\holds.csv: id,company,reason,release_when,set_on
   Never create these if they already exist.

3. Test tracker_tools: add two dummy rows with add_rows, update_status one, update_fields the other,
   add_response for one, export_xlsx, then remove the dummies with tracker_tools._remove_rows(ids,
   reset_counter_to=0) and remove the dummy responses line with tracker_tools._write(RESPONSES,
   RESPONSES_HEADER, rows_without_it). Show the results.

4. 03_documents\CV_MASTER_V2.md: the master CV in clean structured markdown, section by section, nothing
   added and nothing removed, no GPA, no marks, no ranking.

5. 03_documents\CV_MASTER_V2.docx: a one-page A4 Word version of that CV which follows the paragraph
   contract in the runbook appendix "build.py contract" exactly (paragraph 3 = summary, 5 = instruments,
   10-20 = the three experiences, 22-34 = the three projects, 38 = selected coursework, with the anchors at
   9 and 21). Run build.py on the example spec (renamed to a test ID, in a temporary copy) to prove it:
   CV pages=1.

6. 03_documents\LETTER_MASTER.md: a motivation letter skeleton, the paragraphs that never change marked
   FIXED (the dates / 26 weeks / convention de stage / visa paragraph, the close) and the tailored ones
   marked SLOT, with a note on what evidence each slot needs.

7. 01_sources\source_registry.csv from SOURCES.md, columns: source_name, url, country, type,
   needs_account, last_searched, rows_yielded, notes.

8. 00_profile\personalisation_map.json (build.py reads it; never put personal values in the code): check
   CONTACT_LINE equals the contact line of CV_MASTER_V2, INSTRUMENTS lists the instruments of paragraph 5
   (build.py only reorders them), and COURSES holds the exact English course strings (module names only)
   that the CV may show.

Report what you created and anything in my CV that looks inconsistent or unverifiable. Do not fix it
yourself, list it.
Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: 0`."""

SEED = r"""SEED IMPORT. One-time, new campaign only, after CAMPAIGN INIT. Follow CLAUDE.md.
(EXAMPLE: run it only if your school gave you registers of past placements; otherwise skip it, and delete
the REGISTER ADVANTAGE section of CLAUDE.md through /forever.)
Parse the two {{SCHOOL}} PFE registers (placements of previous years) into tracker rows with
tracker_tools.add_rows.

For each placement relevant to my specialty (all CH students; BIO, IIA and IMI students whose subject
involves analytical chemistry, materials, characterisation, sensing, quality systems, process or water
treatment): company, country, city, department, project_title, supervisor as named, source="{{SCHOOL}} register
<year>", agreement_ok=YES, status=discovered, contact_confidence=UNVERIFIED.
The email addresses in these files are students' {{SCHOOL}} addresses, never host contacts: never import them as
supervisor_email or hr_email. Deduplicate on (company_domain, project_title).

Then write 01_sources\insat_host_patterns.md: students per specialty and year, host countries, hosts
appearing in both years or taking more than one student (standing arrangements, rank them first), and what
that means for where to hunt. Keep the parsing scripts in 01_sources\insat_registers_seed\.

Report how many rows you added and any you skipped.
Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: 0`."""
