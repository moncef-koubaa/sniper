HOW TO USE (version 28, 22 October 2026)
1. Do 01_install first (00_START_HERE.md steps 1 to 3): Claude Code, Python 3.12 + libraries, Node.js,
   Word or LibreOffice, Chrome + the Claude extension, the claude.ai connectors. Windows: install.ps1;
   Linux or macOS: bash install.sh.
2. Open PowerShell (Windows) or a terminal (Linux, macOS) in the folder that holds "sniper" (its parent), then:
     claude --chrome
   Accept "trust this folder", type /chrome and choose "Enabled by default" and your campaign profile.
3. Paste everything below the line. If you already filled 02_setup_prompt\answers.json, say so at the end.
   Stuck on any step? Type /ask-me, a space, then paste the step: Claude does it or explains it simpler.
4. The setup locks nothing and deletes nothing: "sniper" stays next to your campaign as its reference copy,
   and you can change the rules and commands later by asking Claude (OPEN INSTALL).
-----------------------------------------------------------------------------------------------------------

PFE CAMPAIGN: SET UP (OR RESTORE) MY INTERNSHIP CAMPAIGN IN CLAUDE CODE, RULES VERSION 24.

WHAT THIS BUILDS
A PFE (final-year internship) campaign run by Claude Code on this PC (Windows, Linux or macOS). Everything
lives in one ROOT folder (default: the folder that holds "sniper"):
  ROOT\campaign\        the workspace: Claude Code is opened here for every campaign run
  ROOT\interviews\      one folder per interview
  ROOT\my documents\    my CV exports, internship agreement templates, recommendations, reports
  ROOT\guides\          the runbook and guides
  ROOT\sniper\    this package, kept as the reference copy (setup prompt, kit, build sources)
The memory of the campaign is campaign\02_tracker\tracker.csv. Each job is a slash command in
campaign\.claude\commands\ that I start by hand. Nothing is scheduled: never create, install or enable a
scheduled task, cron job, routine or automated runner. The rules for every session are campaign\CLAUDE.md.
The full design is in sniper\04_runbook_and_guides\PFE2027_Runbook_Claude_Code.docx; read it first.

PLATFORM
Paths below are written with "\" and shell steps for PowerShell. On Linux or macOS use "/" and the bash
equivalent given with the step. ROOT\.env (written by install.ps1 / install.sh from
ZOK\01_install\.env.example) holds the machine settings: run every Python script with its PYTHON value
(Linux/macOS default ROOT/.venv/bin/python, Windows default %LOCALAPPDATA%\Programs\Python\Python312\python.exe). ROOT\.env and
ROOT\.venv are machine files: never delete them, never lock them, never copy them into the kit.

SOURCE OF THE FILES
- ZOK = the "sniper" folder. ZOK\03_kit holds campaign\, interviews\ and "my documents\" with
  {{PLACEHOLDERS}} in place of personal details. ZOK\PERSONALISE.md explains every placeholder.
- ZOK\02_setup_prompt\fill_placeholders.py fills them from an answers file (answers_TEMPLATE.json shows
  the format) and saves the answers as campaign\00_profile\personalisation_map.json.
- If a kit file is missing, recreate it from the shared
  runbook ZOK\04_runbook_and_guides\PFE2027_Runbook_Claude_Code.docx, never from my own copy in
  ROOT\guides (that copy holds no files): with python-docx, every file sits between a
  paragraph "BEGIN FILE <relative path>" and a paragraph "END FILE"; join the paragraphs in between with
  "\n" and write them as UTF-8 with LF line endings.

RULE ZERO: CAMPAIGN DATA IS SACRED
- Never recreate, reset, re-seed, replace or edit by hand an existing campaign\02_tracker\*.csv,
  id_counter.txt, backups\, 01_sources\source_registry.csv, 00_profile\PROFILE.md, TRACKS.md, KEYWORDS.md,
  DEFENSIBLE_CLAIMS.md, 03_documents\, 04_outbound\<ID>\, 05_reports\, ROOT\interviews\<folder>\.
- These hold my decisions: 02_tracker\holds.csv, 01_sources\country_priority.csv, 00_profile\FORM_ANSWERS.md,
  00_profile\personalisation_map.json, 00_profile\interview_deck\profile_deck.json. Install the kit version
  ONLY if the workspace has none.
- Before replacing any config or code file (CLAUDE.md, AGENTS.md, .claude\*, scheduler\*, tracker_tools.py,
  unblock_tools.py, 04_outbound\_gen\run34\build.py, build_deck.js), copy the current one to
  campaign\02_tracker\backups\config_<YYYYMMDD-HHMMSS>\.
- Send nothing, submit nothing, draft nothing in this session.

STEP 0. READ THE STATE (read only)
1. Find ROOT (ask me only if the parent of ZOK is not where I want it). Does ROOT\campaign exist, with
   02_tracker\tracker.csv? Row count by status (python campaign\02_tracker\tracker_tools.py summary).
2. Tools: `claude --version`; ROOT\.env exists; `<PYTHON> -c "import docx, openpyxl, pypdf"`;
   `<PYTHON> ZOK\03_kit\campaign\scheduler\platform_env.py` shows a chrome path and a pdf_engine (word or
   libreoffice; word also needs `import docx2pdf`); `node --version`. Missing: tell me to run
   ZOK\01_install\install.ps1 (Windows) or `bash ZOK/01_install/install.sh` (Linux, macOS) and stop.
3. Chrome: read Local State in the chrome_user_data folder platform_env.py printed (profile.info_cache). List the profiles
   with their signed-in address and whether they hold the Claude extension
   (<profile>\Extensions\fcoeoabgfenejglbffodgkkbkcdhcgfn).
4. Connectors, one read call each: Gmail list_labels (record the account and every label with its id),
   Drive list_recent_files, Calendar list_calendars, Indeed (any tool; if it fails say so: the Hunter then
   uses indeed.* in Chrome).
5. Scheduled tasks: list any task whose name mentions PFE (Windows Task Scheduler; Linux/macOS:
   `crontab -l` and `systemctl --user list-timers`, lines mentioning PFE or campaign). If one exists, tell me to remove it (nothing may
   be scheduled); never remove or create one yourself.
6. Print one STATE line and the path:
   PATH A, RESTORE: ROOT\campaign\02_tracker\tracker.csv exists. Go to STEP 3. (A received package is
   deleted by STEP 6, so a restore or an update always starts from a new package sent by the author.)
   PATH B, NEW CAMPAIGN: it does not. Do STEP 1 and STEP 2.

STEP 1. INTERVIEW ME (PATH B; PATH A only for answers missing from personalisation_map.json)
Ask in ONE message, grouped, for every value answers_TEMPLATE.json lists that you cannot read yourself
(an answers.json I already filled counts as answered). Group the questions:
- Me: full name, nationality, home city, school (short name), university, degree and field, final year,
  graduation month, working languages, grades wording I allow (EN and FR, exactly; or "none"), instruments
  and techniques I have personally operated, software, approved course names my CV may show.
- The PFE: the window (for example February to August 2027), minimum weeks, campaign name.
- Contact: the Gmail account the connector uses (from STEP 0), the contact email and phone printed on my
  CV, LinkedIn.
- Chrome: which profile from STEP 0 is my campaign profile (it must hold the Claude extension).
- Gmail: the label to file campaign mail under (it must exist: if not, tell me to create it in Gmail, then
  read its id with list_labels), labels to leave alone.
- Search: countries in priority order (at least 10), the fields and tracks I want, organisations I must
  never apply to, countries I have already covered.
- Forms: gender, date of birth, postal address (or NEEDS_ANSWER), salary wording EN and FR, diversity
  default, EU/EEA citizen.
Never guess an answer from my name. Passport and ID numbers are never stored. Values I do not have yet
(DEMONSTRATED_EXPERIENCE, KEY_RESULTS_STORY, MY_REPORTS, the interview models, and the interview-prep
examples of my own field: FIELD_CHOICE_QUESTION, FAILURE_QUESTION, TECHNIQUE_ABBREV_EXAMPLE, SKETCH_SHAPES,
SKETCH_AXES_EXAMPLE, SKETCH_FEATURES_EXAMPLE, READING_EXAMPLE, DECK_NOTE_EXAMPLE, drawn from the techniques
in my CV and reports) keep the neutral wording of answers_TEMPLATE.json until S0 PROFILE (STEP 4) gives
you the facts; then propose a value and ask me once. CAMPAIGN_FILE_STEM (the campaign name without spaces,
which names my runbook and Build Guide files) is derived by fill_placeholders.py.
Write the answers to ZOK\02_setup_prompt\answers.json (same keys as answers_TEMPLATE.json).

STEP 2. CREATE THE FOLDERS (PATH B)
1. Copy ZOK\03_kit\* to ROOT (Windows: robocopy /E; Linux/macOS: cp -a; quote every path): ROOT\campaign, ROOT\interviews,
   ROOT\my documents. Create ROOT\guides empty: my own copies are made at the end of STEP 4.
2. python ZOK\02_setup_prompt\fill_placeholders.py ZOK\02_setup_prompt\answers.json ROOT
   It must end with "placeholders left: 0". A NO VALUE line: ask me for that value, add it, run it again.
3. Write 01_sources\country_priority.csv rows from my country order (rank, country, status pending, runs 0,
   rows_added 0, last_run empty, why: one line each), through Python, header kept.
4. npm install in campaign\00_profile\interview_deck (installs pptxgenjs).
5. Tell me which source documents to put in ROOT\my documents\ and stop only for this: master CV (.docx and
   .pdf), project and internship reports, recommendation letters, the internship agreement templates of my
   school, any register of past placements (goes in campaign\01_sources\insat_registers_seed\). Continue
   when they are there.

STEP 3. INSTALL OR UPDATE THE KIT (PATH A, and PATH B after STEP 2)
PATH A: copy every ZOK\03_kit\campaign file over ROOT\campaign following RULE ZERO (backup first; the
decision files only if missing; data files never), then run fill_placeholders.py with
campaign\00_profile\personalisation_map.json as the answers file. Skip files that are already identical
after filling, so an unchanged settings.json is never rewritten.
- .claude\settings.json: if writing it is refused by Claude Code's safety check, do not work around it:
  print the exact content for me to paste with Notepad (`! notepad ".claude/settings.json"`; Linux/macOS:
  `! nano .claude/settings.json`) and carry on.
- Another user name, Desktop path or operating system: ROOT, WORKSPACE and USER_HOME in the answers cover it; never
  hardcode a path in code (the scripts find their folders from their own location).
- MY GUIDES (PATH A here; PATH B at the end of STEP 4): the guides in ZOK\04_runbook_and_guides are the
  shared copies, with example paths. Make my own copies in ROOT\guides, with this machine's paths and my
  values, from ZOK\05_build_sources (MAP = ROOT\campaign\00_profile\personalisation_map.json):
    PFE_MAP=MAP python render_guides.py ROOT\guides
    PFE_MAP=MAP RUNBOOK_OUT=ROOT\guides RUNBOOK_LOCKED=1 python make_runbook.py
  RUNBOOK_LOCKED=1 makes my runbook a locked copy: no embedded files (no BEGIN FILE / END FILE) and no
  setup prompt in section 4, delivered as ROOT\guides\<CAMPAIGN_FILE_STEM>_Runbook_Claude_Code.pdf (converted
  through Word or LibreOffice; the .docx is deleted, so no Word runbook stays in ROOT\guides). Leave it out only on the author's machine (ROOT\archive\rule snapshots
  exists), whose copy stays full.
  make_runbook.py must print "missing []; mismatched []" (a locked copy also prints "locked copy" and "locked PDF"). Never copy the shared PDFs into ROOT\guides.
  My runbook and Build Guide are named after CAMPAIGN_FILE_STEM (for example PFE2028_Build_Guide.pdf).

STEP 4. ONE-TIME CAMPAIGN PROMPTS (PATH B only)
Run the three prompts of the runbook section "One-time campaign prompts", in order, each as its own job in
this session: S0 PROFILE, CAMPAIGN INIT, SEED IMPORT (SEED IMPORT only if I gave registers of past
placements; otherwise skip it and say so). CV_MASTER_V2.docx must follow the paragraph contract in the
runbook appendix "build.py contract". Then fill the profile-derived answers (STEP 1) in answers.json, copy
CLAUDE.md and .claude\commands\*.md from ZOK\03_kit\campaign over ROOT\campaign again (fill_placeholders.py
only changes text that is still a placeholder, so the neutral wording of the first fill would otherwise stay;
nothing has edited these files since STEP 2), and run fill_placeholders.py again: the deck's shared slides go in 00_profile\interview_deck\profile_deck.json
(replace every EXAMPLE text with facts from PROFILE.md and DEFENSIBLE_CLAIMS.md, same structure).
Last, make my guides (STEP 3, MY GUIDES).

STEP 5. SMOKE TEST (read only, or on temporary copies)
1. `python campaign\02_tracker\tracker_tools.py summary` works; tracker_tools.export_xlsx() writes
   tracker.xlsx (PermissionError: Excel has it open, say so).
2. `python campaign\scheduler\gate.py test` prints "gate self-check ok"; `python campaign\scheduler\preflight.py`
   prints {"ok": true, ...} or the problems to list for me.
3. build.py on a temporary copy of campaign\03_documents and campaign\04_outbound\_gen\run34 with
   specs\EXAMPLE_PFE-0001.json renamed PFE-9999.json (and a temporary copy of 00_profile\personalisation_map.json):
   CV pages=1, Letter pages=1. Delete the copy.
4. node campaign\00_profile\interview_deck\build_deck.js on the example deck spec, output to the temp folder
   (%TEMP% on Windows, /tmp on Linux/macOS):
   it prints "wrote ... slides". Delete the output.
5. No "{{" left in ROOT\campaign (fill_placeholders.py --check), no path that names another person's folders.
6. Exactly 9 command files are in campaign\.claude\commands\: the eight /pfe- commands and ask-me.md.
   /forever and /magic are the author's only and never installed: if forever.md or magic.md is in
   campaign\.claude\commands\ or ~\.claude\commands\ (%USERPROFILE% on Windows), delete those two files there. Tell me
   to type / in a new session opened in ROOT\campaign and check the nine appear.

STEP 6. FINISH: OPEN INSTALL (PATH B, and PATH A; last step)
This is a customisable install (changed 12 Nov 2026): nothing is locked and nothing is deleted. ROOT\sniper
stays next to the campaign as the reference copy; ROOT\.env and ROOT\.venv stay as they are.
1. Gate: every STEP 5 check passed (placeholders left 0), ROOT\guides holds my runbook
   <CAMPAIGN_FILE_STEM>_Runbook_Claude_Code.pdf and both guide PDFs, campaign\.claude\commands holds exactly
   the 9 command files, and campaign\00_profile\personalisation_map.json exists. Anything missing: list it
   and tell me to run the setup again once it is fixed.
2. Keep my answers with the campaign: copy ZOK\02_setup_prompt\answers.json to campaign\00_profile\answers.json.
3. Lock nothing (no attrib +R, no chmod a-w) and delete nothing (not sniper, not its .zip, not the Recycle
   Bin or Trash).
4. Tell me that the rules (CLAUDE.md) and the commands (.claude\commands) are mine to change: I ask for a
   change in plain words in a session opened in ROOT\campaign, and settings.json makes Claude Code ask me
   before each edit of those files (CLAUDE.md, OPEN INSTALL).

STEP 7. FIRST RUN (by me)
Do not run any command yourself and do not schedule anything. Tell me to open a new session in
ROOT\campaign and type /pfe-inbox (or /pfe-hunter on a brand-new campaign), then check: the report path,
permission denials (fix by adding the tool to "allow"), and proof the tracker changed only through
tracker_tools (new backups, row count not lower).

END WITH
- the STATE line before and after, and which path (A or B) ran;
- files installed, files kept, backup folder path, placeholders left (must be 0);
- smoke test results, one line each;
- the STEP 6 result: gate passed or what is missing; answers.json copied;
- what I still have to do, as clicks and commands (extension: "On all sites" and "Act without asking";
  /chrome: Enabled by default and the campaign profile; any refused step; missing source documents);
- which command to run first.

MY ANSWERS:
