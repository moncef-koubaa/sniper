"""Builds <CAMPAIGN_FILE_STEM>_Runbook_Claude_Code.docx (PFE2027 for the shared copy) from the kit, the setup prompt and the one-time prompts.
Every kit file is embedded between "BEGIN FILE <path>" and "END FILE" paragraphs so a new session can
recreate it. Run: python make_runbook.py  (then it re-extracts every file and checks it matches).
Reads sniper\\03_kit\\campaign and 02_setup_prompt, writes 04_runbook_and_guides (RUNBOOK_OUT overrides: a file,
or a folder, where the file is named after CAMPAIGN_FILE_STEM of PFE_MAP).
PFE_MAP=<personalisation_map.json> fills the placeholders: a filled-in copy for a new user (the author's own runbook
in guides is built from campaign\\_runbook\\make_runbook.py, never from this file).
RUNBOOK_LOCKED=1 makes a locked copy for a user set up from sniper: no embedded file contents and no setup prompt,
delivered as PDF (converted through Word or LibreOffice, see platform_env.py, then the .docx is deleted)."""
import os, sys, re
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
ZOK = os.path.dirname(HERE)                        # ...\sniper
KIT = os.path.join(ZOK, '03_kit', 'campaign')
SETUP = os.path.join(ZOK, '02_setup_prompt', 'PFE_CLAUDE_CODE_SETUP_PROMPT.md')
# PFE_MAP=<campaign\00_profile\personalisation_map.json> fills the {{KEY}} placeholders: a personal copy of the runbook
import json
FILL = json.load(open(os.environ['PFE_MAP'], encoding='utf-8')) if os.environ.get('PFE_MAP') else {}
def fill(s):
    return re.sub(r'\{\{([A-Z][A-Z0-9_]*)\}\}',
                  lambda m: FILL[m.group(1)] if isinstance(FILL.get(m.group(1)), str) else m.group(0), s)
LOCKED = os.environ.get('RUNBOOK_LOCKED') == '1'   # locked install: nothing to rebuild the package from
OUT = os.environ.get('RUNBOOK_OUT') or os.path.join(ZOK, '04_runbook_and_guides', 'PFE2027_Runbook_Claude_Code.docx')
if os.path.isdir(OUT):
    OUT = os.path.join(OUT, (FILL.get('CAMPAIGN_FILE_STEM') or 'PFE2027') + '_Runbook_Claude_Code.docx')
sys.path.insert(0, HERE)
import one_time_prompts as otp

NAVY = RGBColor(0x12, 0x35, 0x5B)
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(1.8); sec.top_margin = sec.bottom_margin = Cm(1.6)
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(4)
for name, size in (('Heading 1', 16), ('Heading 2', 13), ('Heading 3', 11.5)):
    h = doc.styles[name]; h.font.name = 'Calibri'; h.font.size = Pt(size); h.font.color.rgb = NAVY

def shade(par, fill):
    ppr = par._p.get_or_add_pPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), fill); ppr.append(shd)

def P(text='', bold=False, italic=False, size=None, color=None, align=None, after=None):
    p = doc.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    return p

def rich(text):
    """paragraph with **bold** segments"""
    p = doc.add_paragraph()
    for i, part in enumerate(re.split(r'\*\*', text)):
        r = p.add_run(part); r.bold = i % 2 == 1
    return p

def bullets(items):
    for t in items:
        p = doc.add_paragraph(style='List Bullet')
        for i, part in enumerate(re.split(r'\*\*', t)):
            r = p.add_run(part); r.bold = i % 2 == 1

def table(rows, widths=None, header=True):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.text = ''
            r = c.paragraphs[0].add_run(str(val)); r.font.size = Pt(9)
            if header and i == 0:
                r.bold = True
                tcpr = c._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear'); shd.set(qn('w:fill'), 'E2EAF2'); tcpr.append(shd)
            if widths: c.width = Cm(widths[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def code_lines(text, marker_begin=None, marker_end=None, size=7.5):
    def line(s, fill='F2F4F6', bold=False):
        p = doc.add_paragraph(); pf = p.paragraph_format
        pf.space_after = Pt(0); pf.space_before = Pt(0); pf.line_spacing = 1.0
        r = p.add_run(s); r.font.name = 'Consolas'; r.font.size = Pt(size); r.bold = bold
        r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')
        shade(p, fill); return p
    if marker_begin: line(marker_begin, 'D6E0EA', True)
    for s in text.split('\n'):
        line(s)
    if marker_end: line(marker_end, 'D6E0EA', True)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def read(rel):
    with open(os.path.join(KIT, rel), encoding='utf-8-sig', newline='') as f:
        return f.read().replace('\r\n', '\n').rstrip('\n')

def embed(rel, note=None):
    doc.add_heading(rel.replace('/', '\\'), level=3)
    if note: P(note, italic=True, size=9)
    if LOCKED:
        P('Contents not included in a locked install.', italic=True, size=9)
    else:
        code_lines(read(rel), f'BEGIN FILE {rel}', 'END FILE')

KIT_FILES = []
for base, dirs, files in os.walk(KIT):
    for f in files:
        if f == 'README.md' or f.endswith('.docx'):   # binary template and folder notes are not embedded
            continue
        KIT_FILES.append(os.path.relpath(os.path.join(base, f), KIT).replace('\\', '/'))
KIT_FILES.sort()

# ------------------------------------------------------------------ title
P('{{CAMPAIGN_NAME}} Campaign Runbook', bold=True, size=24, color=NAVY, after=2)
P('Claude Code edition · version 33 (rules version 30)', bold=True, size=14, color=NAVY, after=2)
P('Every step, in order, with the exact prompt for each, every script, and the architecture.', italic=True)
P('{{FULL_NAME}} · {{SCHOOL}}, {{UNIVERSITY}} · PFE window {{PFE_WINDOW}} · Revised 31 October 2026', size=9.5)
if LOCKED:
    P('Locked copy for a campaign set up from sniper: it explains the system but holds no file contents '
      'and no setup prompt. Rules and commands change only when the author sends a new package.', size=9.5)
else:
  P('Part of sniper, the transfer package. With the setup prompt (02_setup_prompt) and the Build Guide it is '
  'the complete kit: a new Claude Code session can rebuild the whole system from that one folder. Everything '
  'between "BEGIN FILE" and "END FILE" is a file of the system, copied exactly (placeholders such as '
  '{{FULL_NAME}} are filled by the setup).', size=9.5)

# ------------------------------------------------------------------ 1
doc.add_heading('1. How the system works', level=1)
P('Everything lives in one folder, {{ROOT}}: campaign\\ (the workspace), interviews\\, my documents\\, '
  'guides\\, sniper\\ (this package) and archive\\. Claude Code runs inside {{WORKSPACE}}: every session '
  'opened there loads CLAUDE.md, the rules, automatically.')
P('A session is disposable. It does one job, then ends. Nothing carries between sessions, and nothing needs '
  'to, because the memory of the campaign is a file, not a chat: 02_tracker\\tracker.csv. Every opportunity is '
  'one row. Every run reads the tracker, works on some rows, writes the result back through tracker_tools.py, '
  'writes a report in 05_reports, and stops.')
P('discovered (found, nothing verified) → enriched (contact, visa and agreement checked, scored) → queued '
  '(documents written, draft ready) → applied (sent or submitted) → acknowledged, interview, offer, rejected, '
  'no_response. Side exits: screened_out and expired (dead, their key goes to seen.csv so they are never found '
  'again), blocked (needs a human, moved to blocked.csv, the manual queue).', bold=True, size=10)
P('Each job is a slash command that {{FIRST_NAME}} starts by hand in Claude Code. Nothing is scheduled. No run has a '
  'row, search, subagent or spending limit; the only caps are on email (50 cold emails a day, 15 follow-ups and '
  '10 Group 2 replies per Inbox run). Every command updates the tracker right after each row it works on.')
doc.add_heading('Architecture', level=2)
table([
    ['Layer', 'What', 'Where'],
    ['Rules', 'Who I am, what the PFE must be, never-do list, sending, forms, holds, writing, browser method', 'CLAUDE.md'],
    ['Jobs', '9 slash commands in a received kit, one job each (8 pfe-* runs, /ask-me); the author\'s own campaign also has /forever and /magic', '.claude\\commands\\*.md'],
    ['Permissions', 'Allowed tools; sending allowed, forward asks, trash/spam/share denied', '.claude\\settings.json'],
    ['Memory', 'tracker.csv (truth), responses.csv, seen.csv, blocked.csv, holds.csv, backups\\', '02_tracker\\'],
    ['Tools', 'tracker_tools.py (every tracker write), unblock_tools.py (manual queue)', '02_tracker\\'],
    ['Facts', 'PROFILE, DEFENSIBLE_CLAIMS, TRACKS, KEYWORDS, FORM_ANSWERS', '00_profile\\'],
    ['Sources', 'source_registry.csv, country_priority.csv, {{SCHOOL}} registers and host patterns', '01_sources\\'],
    ['Documents', 'CV_MASTER_V2 (.md/.docx), LETTER_MASTER; build.py makes each CV + letter', '03_documents\\, 04_outbound\\'],
    ['Helpers', 'gate.py (which commands have work), preflight.py (machine check), snapshot.py (mirror to a folder you name). Nothing is scheduled.', 'scheduler\\'],
    ['Outside world', 'Chrome profile "{{CHROME_PROFILE}}" + Claude in Chrome; Gmail, Drive, Calendar, Indeed connectors', 'claude.ai / Chrome'],
], widths=[2.4, 9.6, 5.4])
doc.add_heading('Locked install (18 Oct 2026)', level=2)
P('A campaign set up from sniper is locked. The last step of the setup (STEP 6 LOCKDOWN) keeps the '
  'user\'s own files (answers.json goes to 00_profile, any file of theirs left in the package goes to my '
  'documents\\from sniper), marks CLAUDE.md, the commands, settings.json and the guides read-only, then '
  'deletes the sniper folder and its .zip for good (never through the Recycle Bin, and only their '
  'entries are cleared from it). It matches exact names only, because sniper is a common word: the folder '
  'leaf must be sniper, and only sniper.zip and its browser copies such as sniper (1).zip (and the old name zok ellougha.zip) are '
  'deleted, never another file whose name starts with sniper. /forever and /magic are the author\'s only and are never installed. The '
  'LOCKED INSTALL paragraph of CLAUDE.md and deny rules in settings.json make Claude refuse any change to the '
  'rules, commands, runbook or guides. Rules change only when the author sends a new package. Nothing '
  'personal is ever deleted, and the campaign data stays the user\'s to change.')
doc.add_heading('Running the commands (manual, no limits)', level=2)
table([
    ['Command', 'How much it covers', 'Asks first'],
    ['/pfe-hunter [country] [track]', 'Every available opportunity in the country, every source and track, until the country is exhausted', 'no'],
    ['/pfe-checker [n or ALL]', 'As many rows as you choose; no maximum', 'yes: how many rows (10, 25, 50, ALL or any number)'],
    ['/pfe-applier [n email] [n portal]', 'As many applications as you choose, by email, portal or both; no maximum. Started without a method or number, it asks first, before anything else, even when an unfinished PROGRESS file exists (that file then only skips IDs already done)', 'yes: which method(s); for Portal, which portal(s) from a list with eligible rows per portal; then how many applications of each (10, 25, 50, ALL or any number)'],
    ['/pfe-inbox', 'All PFE mail; follow-ups max 15 and Group 2 replies max 10 per run (email caps)', 'no'],
    ['/pfe-send-held', 'Cap-held drafts, within 50 cold emails a day', 'no'],
    ['/pfe-send', 'Group 3 decisions, held drafts and DRAFT_ONLY drafts', 'yes: each send'],
    ['/pfe-cleanup', 'Monthly archive of dead rows', 'no'],
    ['/pfe-interview-prep <email>', 'One interview', 'interactive'],
    ['/forever <change>', 'Author only, not in a received kit. Changes a rule permanently: campaign rules and commands, and sniper (kit templates, setup prompt, runbook, guides, build sources, VERSION, CHANGELOG), the guide copies in guides\\, the author\'s own runbook (built separately from campaign\\_runbook, never from this package), a rule snapshot and memory, in one run', 'only if the change is ambiguous'],
    ['/magic [command]', 'Author only, not in a received kit. Guided review of one command: maps it into tasks with line numbers, walks you through each (keep, change, remove, explain more, stop), checks the changes against CLAUDE.md and applies the approved ones through /forever. No tracker data, Gmail, Chrome or portals', 'yes: which command, then each task'],
    ['/ask-me <step>', 'Help on one step of the setup or a guide that a new user is stuck on: they paste the step after the command, and Claude does it if it can (checks, install.ps1, winget, opening files) or explains it again as tiny numbered steps in simple words, with the check that shows it worked. Works in any folder (install.ps1 copies it to the user\'s .claude\\commands). Never signs in, types a password or writes tracker data', 'only if no step was pasted'],
], widths=[4.6, 8.4, 4.4])
bullets([
    'No row, search, subagent or spending cap on any run (changed 6 Oct 2026). Typing a number or ALL after /pfe-checker answers the row question in advance; after /pfe-applier, a number or ALL followed by a method (20 email, ALL portal, 15 email 10 portal) answers both Applier questions, while a bare number still asks for the method (changed 14 Oct 2026). Portal sites typed after the word portal (10 portal jobs.veolia.com) answer the portal question; portal alone still asks it (changed 17 Oct 2026). The word draft (20 email draft) makes the Applier build the documents and Gmail drafts without sending them; /pfe-send then sends only the ones approved (changed 28 Oct 2026).',
    'Every command writes the tracker through tracker_tools / unblock_tools right after each row and each action, never at the end. A run cut short by the plan usage limit or a full context keeps everything done so far; the next run resumes.',
    'Every report says how many rows the run covered and how many eligible rows remain.',
])
doc.add_heading('Countries', level=2)
P('01_sources\\country_priority.csv ranks the countries by fit with my profile (written by the setup from my '
  'answers, at least 10). The Hunter stays on one country, run after run, through all its sources and '
  'tracks (track ALL), with no row or search limit, until it is exhausted (every source and track done and the last 20 searches found no new row), then takes the next. '
  'After the last one it researches the next 15 itself and appends them. Already hunted before this file: '
  '{{COUNTRIES_HUNTED_BEFORE}}.')
doc.add_heading('Sending, forms and holds', level=2)
bullets([
    '**Sent automatically** with send_message on a finished draft: applications (Applier, /pfe-send-held), follow-ups (Inbox, max 15), Inbox Group 2 replies (max 10). Only when all five checks pass: swap test and banned words; verified address never emailed before; not held; CV and letter attached (checked on one full-reload read of the Gmail Drafts list in Chrome, not get_draft); fewer than 50 cold emails today. Not Applier draft-mode drafts (DRAFT_ONLY): only /pfe-send sends those, the ones approved.',
    '**Never automatic:** replies about interviews, offers, salary, contracts, visa or legal questions. They are A/B/C drafts for /pfe-send.',
    '**Unpaid or low-paid offers (added 10 Oct 2026):** I have no personal or {{SCHOOL}} funds. A host that would take me unpaid or with a very low allowance is negotiated, never declined, and no draft says I fund myself. The drafts first look up the pay for that position in that country or Europe and the anchors (Spain visa proof about 600 EUR/month, France intern minimum about 630 EUR/month in 2026, Erasmus+ KA171 traineeship grants), then ask for one concrete monthly figure (up to the average plus 200 to 300 EUR when the host has the means), tied to an external requirement such as the visa proof of means, with alternatives: partial allowance, housing, a grant, a project contract. Figures and sources go in the report.',
    '**Forms** are filled from FORM_ANSWERS.md and submitted. A required question with no truthful answer there (passport or ID, GPA, numeric salary, postal code, legal visa declaration...) → blocked.csv as NEEDS_ANSWER.',
    '**Never attempted:** CAPTCHAs, account creation, passwords, LinkedIn Easy Apply, Indeed Apply → BLOCKED.',
    '**Holds:** holds.csv lists rows nothing automatic may touch; only {{FIRST_NAME}} removes lines. Automatic holds: every row of a company with an interview, offer or Group 3 thread; every address already emailed.',
    '**Referrals:** a reply naming another person with an address adds a new tracker row in /pfe-inbox, address from the email, source naming the referrer and the original row. The Applier works these rows first among email rows, as cold emails under every send check, and the letter and email cite the referrer as the person who suggested the contact, unless the referrer refused. An auto-reply naming a replacement contact adds the row but cites nobody. A redirect to a portal, a job board or a shared address is not a referral. A name with no address gets no row.',
])

# ------------------------------------------------------------------ 2
doc.add_heading('2. The kit (sniper)', level=1)
table([
    ['File', 'Role'],
    ['00_START_HERE.md', 'One page: what the package is, the six steps and how long each takes. The whole package is deleted at the end of the setup (Locked install).'],
    ['01_install\\', 'Prerequisites with tested versions, requirements.txt, package.json, install.ps1 (manual, schedules nothing; also copies /ask-me to the user\'s .claude\\commands).'],
    ['02_setup_prompt\\', 'PFE_CLAUDE_CODE_SETUP_PROMPT.md (section 4), answers_TEMPLATE.json, fill_placeholders.py.'],
    ['03_kit\\', 'campaign\\, interviews\\, my documents\\: the files the setup copies into ROOT (the same files as in the appendices), with {{PLACEHOLDERS}}.'],
    ['04_runbook_and_guides\\', 'This document, the Build Guide, Friendly Setup and Usage, the Claude Code Guide.'],
    ['05_build_sources\\', 'make_kit.py (regenerates 03_kit from a live campaign without /forever and /magic, writes MANIFEST.txt and runs the privacy scan), kit_blocks.json (with the LOCKED INSTALL blocks), make_runbook.py, one_time_prompts.py, the guide HTML sources.'],
    ['PERSONALISE.md, VERSION, CHANGELOG.md', 'Every placeholder explained; the rules version; one line per rule change.'],
], widths=[6.2, 11.2])
P('Not in the kit, because they are personal and cannot be generated: the source documents (CV, reports, '
  'letters, agreement templates, registers of past placements), and the campaign data (tracker and the rest '
  'of 02_tracker, 00_profile generated by S0, 04_outbound, 05_reports, interviews).', size=9.5)

# ------------------------------------------------------------------ 3
doc.add_heading('3. Part 1: you only, no Claude (about 45 minutes)', level=1)
for i, t in enumerate([
    'If ROOT is in OneDrive: OneDrive signed in and the folder synced (OneDrive can lock a file for a few seconds; the tools retry).',
    'Claude Code installed ({{USER_HOME}}\\.local\\bin\\claude.exe); `claude`, then /login with the claude.ai account that holds the connectors.',
    'Python 3.12 for the current user ({{USER_HOME}}\\AppData\\Local\\Programs\\Python\\Python312\\), then: python.exe -m pip install -r sniper\\01_install\\requirements.txt (full path). Node.js for the interview decks. 01_install\\install.ps1 does both.',
    'Microsoft Word installed and opened once (build.py makes PDFs through Word).',
    'Chrome: the {{SCHOOL}} profile with the Claude in Chrome extension (site access "On all sites", permission mode "Act without asking"), logged in to Gmail ({{SCHOOL}}), LinkedIn, Indeed, JobTeaser, WTTJ, Studyrama, StudentJob, EURAXESS and every portal where you have a candidate account.',
    'claude.ai → Settings → Connectors: Gmail, Google Drive, Google Calendar ({{SCHOOL}} account), Indeed. Gmail label {{GMAIL_LABEL}} exists.',
], 1):
    rich(f'**{i}.** {t}')

# ------------------------------------------------------------------ 3b
doc.add_heading('What no file can carry (check these on every new machine)', level=2)
table([
    ['Item', 'How to set it', 'How the system notices when it is wrong'],
    ['Claude Code login', 'claude, then /login (the claude.ai account with the connectors)', 'the first command fails to start'],
    ['Connectors: Gmail, Drive, Calendar, Indeed', 'claude.ai > Settings > Connectors, {{SCHOOL}} Google account', 'the run report names the failing connector; Indeed falls back to Chrome'],
    ['Chrome profile + Claude in Chrome', 'extension in the {{SCHOOL}} profile, "On all sites", "Act without asking"; /chrome > Enabled by default', 'preflight.py'],
    ['Gmail session in Chrome', 'sign in to Gmail in that profile when Google asks ("Confirmez qu il s agit bien de vous")', 'email rows BLOCKED "SESSION EXPIRED: GMAIL" in the Applier report'],
    ['Job-site and portal logins', 'sign in once in that profile, tick "stay signed in"', 'rows BLOCKED "SESSION EXPIRED" / "LOGIN_WALL"'],
    ['Python libraries, Word', 'Part 1 steps 3 and 4', 'preflight.py'],
    ['Gmail label {{GMAIL_LABEL}}', 'create it in Gmail', 'the Inbox report (list_labels)'],
], widths=[3.8, 7.0, 6.6])

# ------------------------------------------------------------------ 4
doc.add_heading('4. Part 2: the setup prompt (once per machine)', level=1)
P('cd into the folder that holds sniper, then claude --chrome, accept the folder, /chrome → Enabled '
  'by default. Paste the prompt below. It interviews you once (or reads 02_setup_prompt\\answers.json), then '
  'decides by itself between PATH A (restore: ROOT\\campaign has a tracker) and PATH B (new campaign: it creates '
  'the folders, fills every placeholder and runs the one-time prompts of section 5). It never resets campaign '
  'data. If Claude Code\'s safety check refuses to edit settings.json, or run a check, it hands you the exact '
  'command to type with "!" (forward slashes).')
if LOCKED:
    P('The setup prompt is not included in a locked install.', italic=True, size=9.5)
else:
  with open(SETUP, encoding='utf-8') as f:
    code_lines(f.read().rstrip('\n'), 'BEGIN PROMPT setup (also the file PFE_CLAUDE_CODE_SETUP_PROMPT.md)', 'END PROMPT')

# ------------------------------------------------------------------ 5
doc.add_heading('5. One-time campaign prompts (PATH B only)', level=1)
P('Run by the setup prompt for a brand-new campaign, in this order, each as its own job. Never run them on an '
  'existing campaign: they would rebuild the tracker from nothing.', bold=True)
for title, text in (('S0 PROFILE', otp.S0), ('CAMPAIGN INIT', otp.INIT), ('SEED IMPORT', otp.SEED)):
    doc.add_heading(title, level=2)
    code_lines(text, f'BEGIN PROMPT {title}', 'END PROMPT')

# ------------------------------------------------------------------ 6
doc.add_heading('6. Part 3: every week from then on', level=1)
table([
    ['When', 'You do', 'Time'],
    ['Every day', 'claude in the folder: /pfe-inbox, then /pfe-send-held, /pfe-checker, /pfe-applier as needed (answer the row question), /pfe-hunter when discovered rows run low.', 'as long as the runs take'],
    ['Report says "Decisions waiting"', 'claude in the folder, /pfe-send, answer e.g. "D: PFE-0042 option B"', '5 min'],
    ['Any time', 'Open 02_tracker\\tracker.xlsx: the dashboard sheet has four pie charts (all rows by status, and what was sent this week, last week and two weeks ago, with reply rates), refreshed after every run. The offers sheet lists every opportunity offered to me with its details, stage and next step', '2 min'],
    ['Once a week', '02_tracker\\blocked.csv: Easy Apply links, NEEDS_ANSWER questions, login walls. Apply by hand, then tell Claude "PFE-xxxx submitted".', '30 min'],
    ['Interview booked', '/pfe-interview-prep <their email>, then settle its CHECK BEFORE THE INTERVIEW list', '1 run'],
    ['Whenever', 'Write to the {{SCHOOL}} classmates from the registers who did their PFE at your target hosts. Still the highest-value move.', '-'],
], widths=[3.6, 11.6, 2.2])
P('Things you can say in a session: "PFE-0123 submitted" · "hold PFE-0500 until the LIST interview" · "release '
  'PFE-0393" · "PFE-0123 salary: say negotiable, submit it" · "add to FORM_ANSWERS: ..." · "mark Italy exhausted" '
  '· "put Portugal before Morocco" · "/pfe-hunter Portugal".', size=9.5)
doc.add_heading('Control commands (type in Claude Code, forward slashes)', level=2)
code_lines('\n'.join([
    '/pfe-checker ALL          /pfe-applier 15 email 10 portal          /pfe-hunter Portugal',
    '! "%LOCALAPPDATA%/Programs/Python/Python312/python.exe" scheduler/gate.py   (which commands have work)',
]), size=7.5)

# ------------------------------------------------------------------ 7
doc.add_heading('7. The prompts', level=1)
P('CLAUDE.md is loaded in every session. Each command file is the prompt of its run; you type the command '
  'to start it. Claude Code replaces $ARGUMENTS with whatever follows the command.')
embed('CLAUDE.md', 'Rules for every session. The setup personalises only the ACCOUNTS section.')
order = ['pfe-hunter', 'pfe-checker', 'pfe-applier', 'pfe-inbox', 'pfe-cleanup',
         'pfe-send-held', 'pfe-send', 'pfe-interview-prep', 'ask-me']
notes = {
    'pfe-hunter': 'Manual. Covers every available opportunity in the country, no row or search limit; each row saved as soon as it is ready. Every web search and page read runs in a subagent; the main session keeps the Indeed connector, Chrome boards, subagent launches and tracker writes (17 Oct 2026). Companies first (20 Oct 2026, rules 25): industrial companies, SMEs, scale-ups and startups (incubator and accelerator portfolios, deep-tech and cleantech lists, national startup registries, company careers pages) come before universities and public labs, which are still covered and never screened out for being academic; an unadvertised company contact (CTO, R&D lead, engineering manager, plant manager) counts when verified on a page that was opened; the report splits rows into company or startup and academic, and names the company sources tried when most rows are academic.',
    'pfe-checker': 'Manual. Asks how many rows (any number or ALL), no maximum; each row saved as soon as it is done. Among discovered rows of similar fit, company and startup rows come before academic rows (20 Oct 2026).',
    'pfe-applier': 'Manual. When the arguments leave the method or the number open, the questions are the very first action, before reading the tracker, counting rows or reading a PROGRESS file, and they are asked even when a PROGRESS file exists (it then only skips IDs that already have an outcome; 17 Oct 2026, v19). Asks which method (email, portal or both, multiSelect) and then how many applications of each (10, 25, 50, ALL or any number), showing the eligible rows per method and the cold emails left under today\'s cap; when Portal is ticked it stops, lists every portal (the site of application_url) with its eligible rows and asks which portal(s) to apply through (multiSelect, one, several or all; 17 Oct 2026, v18), and only rows on those portals are worked; the number counts only emails sent and portal forms submitted, so DRAFTED, BLOCKED and NO_CONTACT rows are replaced by the next eligible row of that method. Rows of a method not chosen are left alone. The tracker and the PROGRESS file (methods and numbers included) are updated after every row, so a run cut short resumes with the same choice. Email rows go in batches of up to 10: right after build.py one shell command copies the batch\'s PDFs into 02_tracker\\_upload\\<ID>\\ (deleted at the end or when the run stops); phase A composes each Gmail draft (one javascript_tool wait for the uploads, ATTACH_TIMEOUT after one reload and retry) and records it as queued, draft composed, COMPOSED in PROGRESS; phase B lists the drafts with one connector call, checks attachments on one read of the Drafts list and sends each draft that passes, updating the tracker after each send. No file listings between rows. BLOCKED and NO_CONTACT are the tool being honest, not failing. A BLOCKED row only a person can finish, and a draft held for a reason other than the cap, also gets a next_actions row. With the word draft in the arguments (draft mode, 28 Oct 2026) it makes the drafts and checks their attachments but never sends: each draft stays queued, DRAFTED, reason DRAFT_ONLY, the email number counts drafts made, and /pfe-send sends the ones approved.',
    'pfe-inbox': 'Manual, daily. Also sends due follow-ups (max 15) and expires dead rows, the two jobs of the retired /pfe-review. Updates the offers tab (offers.csv) every run: details, stage and next step of each offer. Adds and closes rows of the next_actions tab (Group 3 choices, interview prep, school convention, visa, missing documents). Keeps the waiting_list tab (waiting_list.csv) after the replies are processed and before the follow-ups: rows at applied with no response, status waiting, follow_up or followed_up, and the follow-ups are sent from its follow_up rows, oldest followup_due first. Portal rows with no address are never sent to: they get a note and one next_actions item. The one-line "Inbox choices: ..." answers are given in /pfe-send. A reply that names another person with an address adds a referral row (source referral: <referrer>, <original ID>), sent first by the Applier as a cold email and citing the referrer; auto-replies add the row but cite nobody; a redirect to a portal is not a referral (31 Oct 2026).',
    'pfe-cleanup': 'Manual, on the last day of the month. seen.csv is two columns wide and does one job: it stops Hunter from re-finding dead leads. Open next actions of archived rows are set dropped.',
    'pfe-send-held': 'Manual, first thing each day.',
    'pfe-send': 'Interactive only. Section H also lists the DRAFT_ONLY drafts of an Applier draft-mode run and sends only the ones named (send H 1-20, send H all), within the 50/day cap. After each send it closes the matching next action; a sent acceptance adds the school convention action.',
    'magic': 'Interactive only. Reviews one command task by task (keep, change, remove, explain more, stop; AskUserQuestion has 4 options, so stop is typed in Other), checks the changes against CLAUDE.md, then runs the /forever procedure with the approved ones. Writes nothing itself, no tracker data, no Excel export; RUN_STATS all zero (14 Oct 2026, v14).',
    'ask-me': 'Interactive, for a new user stuck on a step (18 Oct 2026, v20). Every step box of Friendly Setup and Usage ends with a line telling the user to copy the step, type /ask-me and paste it (steps 1 to 5, before Claude Code works: paste it at claude.ai; step 6, which installs /ask-me: paste it into Claude Code after "help me with this step:"). Finds the step in the guide sources, checks the machine read-only, does the step when only commands or files are needed, otherwise explains it again as tiny numbered steps in the user\'s language. install.ps1 copies it to %USERPROFILE%\\.claude\\commands so it works in any folder, including the setup session. No tracker data, no Excel export; RUN_STATS all zero when opened in the campaign.',
    'pfe-interview-prep': 'Interactive only, one session per interview. The NotebookLM prompt is always a plain-text note, NOTEBOOKLM_PROMPT.txt, with no Markdown syntax, never .md (17 Oct 2026, v17). The prep, the deck and the NotebookLM prompt never mention {{NEVER_MENTION}} and never use it as an argument (13 Oct 2026, v12). Section 6 is the one that matters most. Section 6A (7 Oct 2026) explains every technique from the CV and from the host, each with a labelled sketch of its typical graph; every answer is written in full, as in the {{PREP_MODEL_SHORT}} prep of 5 Oct 2026. Since 13 Oct 2026 every interview gets its own folder, {{ROOT}}\\interviews\\<YYYY-MM-DD>_<Organisation>_<Interviewer>\\ (interview date from interviews.csv; unknown: today and _date-TBC), with three files: the prep PDF (also kept in 05_reports), a short self-presentation deck <YYYY-MM-DD>_<Organisation>_presentation.pptx built by 00_profile\\interview_deck\\build_deck.js on the model of {{FIRST_NAME}}\'s edited {{DECK_MODEL_SHORT}} deck, and NOTEBOOKLM_PROMPT.txt, a NotebookLM coaching prompt in the interview language (key points, techniques, model answers, weak spots, questions to ask, mock interview one question at a time). Nothing loose in the root of the interviews folder. Since 17 Oct 2026 (v18) the deck follows {{FIRST_NAME}}\'s edited {{DECK_MODEL_SHORT}} deck ({{DECK_MODEL}}): its slide set only, with no "What I would change" lessons slide and no "Three things the numbers told me" slide, and speaker notes that first say what the slide shows in simple words, then the result, with any over-explanation between // and // (kept for questions, not said); the agenda slide has no notes.',
}
for name in order:
    embed(f'.claude/commands/{name}.md', notes[name])

# ------------------------------------------------------------------ 8
doc.add_heading('8. Rules that keep it honest', level=1)
bullets([
    'One run, one fresh session. The tracker is the memory and is updated after every row, so nothing is lost when a session ends.',
    'Never invent. No made-up contacts, emails, deadlines, results or techniques. No addresses built from a pattern. A verified email or none.',
    'My work versus the team\'s. Documents say what I did, not what a project or host group did. Every claim defensible under questioning.',
    'No GPA, marks or ranking anywhere. Selected coursework by module name only.',
    'Cold email is capped at 50 a day (raised from 25 on 28 Sep 2026); portals carry the volume. Deliverability collapses quietly, not loudly.',
    'Auto-sent email cannot be unsent. holds.csv is how to stop one company; not starting a command stops everything.',
    'Never apply to {{EXCLUDED_ORGS}}.',
    'Realistic funnel: 2500 discovered, 900 passing eligibility, 350 applications, 50 replies, 10 interviews, 2 offers.',
])

# ------------------------------------------------------------------ 9
doc.add_heading('9. When something goes wrong', level=1)
table([
    ['Symptom', 'Fix'],
    ['A run stopped part way', 'Run the command again. Rows are saved one by one; the Applier asks its questions again, then skips the IDs its PROGRESS file already marks done.'],
    ['Usage limit', 'Wait for the next plan window and run the command again: nothing done so far is lost.'],
    ['Many LOGIN_WALL / SESSION EXPIRED', 'Log in again in Chrome {{CHROME_PROFILE}}; /chrome → that browser; ask Claude to retry those rows.'],
    ['Drafts in the wrong Gmail account', 'Find which /mail/u/N/ is the {{SCHOOL}} account; tell Claude "Gmail compose is u/N".'],
    ['Permission denied in a log', 'Add the tool to "allow" in .claude\\settings.json (one allow block, commas).'],
    ['Wrong or duplicate email sent', 'Add a hold now; tell Claude, it drafts a short correction for /pfe-send.'],
    ['Tracker looks wrong', 'Every write left a copy in 02_tracker\\backups\\: "restore tracker from the backup before <time>".'],
    ['PermissionError on tracker.csv', 'Close Excel; read tracker.xlsx, never the CSV, during runs.'],
    ['! command "file does not exist"', 'Use forward slashes in ! commands.'],
], widths=[5.2, 12.2])
P('The full list with causes is in the Build Guide, section 9.', italic=True, size=9.5)

# ------------------------------------------------------------------ A
doc.add_heading('Appendix A. Scripts and configuration', level=1)
P('Copied into the workspace by the setup prompt (same relative path). holds.csv, country_priority.csv and '
  'FORM_ANSWERS.md are installed only when the workspace has none; holds.csv lists IDs of the 2026 campaign.')
done = {'CLAUDE.md'} | {f'.claude/commands/{n}.md' for n in order}
anote = {
    '.claude/settings.json': 'Permissions. If Claude Code refuses to write it, paste it with Notepad.',
    'scheduler/pfe-run.ps1': 'The daily chain and single jobs. -Job daily | inbox | hunt-check | check-apply | applier | send-held',
    'scheduler/install-tasks.ps1': 'Registers \\PFE2027\\Daily chain, daily 07:30.',
    'scheduler/uninstall-tasks.ps1': 'Kill switch.',
    'scheduler/snapshot.py': 'Mirrors the workspace to a folder you name, by hand only (no default destination since 18 Oct 2026). `snapshot.py test` runs its self-check.',
    'scheduler/test-budget.ps1': 'Budget self-check: runs the real Step function of pfe-run.ps1 against a fake claude that overspends every cap, and asserts the chain stays inside its budget. No Claude call, no writes.',
    'scheduler/preflight.py': 'Machine check, run by hand: Claude Code, Python libraries, Word, Chrome profile and extension.',
    'scheduler/gate.py': 'Read-only: which steps have work. `gate.py test` runs its self-check.',
    '02_tracker/tracker_tools.py': 'The only way to write the tracker. Backs up before every write; retries OneDrive locks. The interviews tab has an interview_language column between interviewer and interviewer_email. upsert_offer writes the offers tab (offers.csv), one row per opportunity offered to me. upsert_action writes the next_actions tab (next_actions.csv, first sheet of tracker.xlsx): one row per thing to do by hand, with type, due date, priority and status open, done or dropped. upsert_waiting and refresh_waiting write the waiting_list tab (waiting_list.csv): applied rows with no response, status waiting, follow_up or followed_up, in that file only. `tracker_tools.py test-waiting` is its self-check.',
    '02_tracker/unblock_tools.py': 'Manual queue: apply_row, block_row, note_block, workdays.',
    '02_tracker/holds.csv': 'State on 28 Sep 2026.',
    '01_sources/country_priority.csv': 'State on 28 Sep 2026; the Hunter updates status, runs, rows_added, last_run.',
    '00_profile/FORM_ANSWERS.md': 'Standing portal answers, decided by {{FIRST_NAME}} on 28 Sep 2026.',
    '04_outbound/_gen/run34/build.py': 'Document generator. Contract in Appendix B.',
    '04_outbound/_gen/run34/specs/EXAMPLE_PFE-0001.json': 'Spec format example. Never built as is (the setup smoke test builds a renamed copy in a temporary folder).',
    '00_profile/interview_deck/build_deck.js': 'Interview self-presentation deck (fade builds; speaker notes = script, // parts kept for questions), used by /pfe-interview-prep. node build_deck.js specs/<spec>.json <out.pptx>. Since 18 Oct 2026 the shared slides (title, about me, the project slides, instruments) come from profile_deck.json, so the code holds no personal fact; they carry only PROFILE.md / DEFENSIBLE_CLAIMS.md facts in English or French. The host slides come from the spec.',
    '00_profile/interview_deck/profile_deck.json': 'The shared slides of the deck: replace every EXAMPLE text with your facts (setup STEP 4).',
    '00_profile/interview_deck/package.json': 'Pins pptxgenjs 3.12.0. Run npm install in this folder once after installing the kit.',
    '00_profile/interview_deck/specs/EXAMPLE_2027-01-15_ExampleLab_Doe.json': 'Deck spec format example. Your specs live only in your workspace.',
}
for rel in KIT_FILES:
    if rel not in done:
        embed(rel, anote.get(rel))

# ------------------------------------------------------------------ B
doc.add_heading('Appendix B. Data formats and contracts', level=1)
doc.add_heading('Folder tree of the workspace', level=2)
code_lines('\n'.join([
    'ROOT\\                          {{ROOT}}',
    'campaign\\                      the workspace',
    '  CLAUDE.md AGENTS.md          rules (kit; AGENTS.md is the Codex copy)',
    '  .claude\\commands\\*.md        9 commands (kit)      .claude\\settings.json (kit)',
    '  00_profile\\                  PROFILE.md DEFENSIBLE_CLAIMS.md TRACKS.md KEYWORDS.md (S0), FORM_ANSWERS.md, personalisation_map.json (setup)',
    '  00_profile\\interview_deck\\   build_deck.js profile_deck.json package.json specs\\<date>_<Org>_<Name>.json (kit; npm install once)',
    '  01_sources\\                  source_registry.csv SOURCES.md insat_host_patterns.md insat_registers_seed\\ country_priority.csv',
    '  02_tracker\\                  tracker.csv responses.csv seen.csv blocked.csv screened_out.csv holds.csv interviews.csv offers.csv next_actions.csv waiting_list.csv id_counter.txt',
    '                               tracker.xlsx (view) tracker_tools.py unblock_tools.py backups\\',
    '  03_documents\\                CV_MASTER_V2.md CV_MASTER_V2.docx LETTER_MASTER.md',
    '  04_outbound\\<ID>\\            CV_{{FILE_STEM}}_<n>_v1.docx/.pdf Letter_{{FILE_STEM}}_<n>_v1.docx/.pdf email.md letter.txt notes.md sent_<date>.md',
    '  04_outbound\\_gen\\run34\\      build.py specs\\<ID>.json',
    '  05_reports\\                  <date>_runNN_<job>.md inbox_<date>.md interview_prep_*.md/.pdf logs\\',
    '  scheduler\\                   gate.py preflight.py snapshot.py (helpers, run by hand; nothing is scheduled)',
    'interviews\\<YYYY-MM-DD>_<Org>_<Name>\\   prep PDF, <date>_<Org>_presentation.pptx, NOTEBOOKLM_PROMPT.txt (one folder per interview)',
    'my documents\\                  cv\\ internship agreements\\ recommendations\\ reports and projects\\ (source documents)',
    'guides\\  sniper\\  archive\\   runbook and guides; this package; rule snapshots and parked files',
]))
doc.add_heading('CSV headers', level=2)
code_lines('\n'.join([
    'tracker.csv, blocked.csv, screened_out.csv (40 columns, one line):',
    'id,date_discovered,status,priority,match_score,selection_probability,country,city,company,company_domain,',
    'org_type,department,project_title,project_type,field,track,duration_weeks,start_date,deadline,stipend,',
    'visa_support,agreement_ok,supervisor,supervisor_email,hr_contact,hr_email,contact_confidence,best_method,',
    'application_url,source,date_applied,cv_version,letter_version,email_sent,date_response,response_type,',
    'interview_date,followup_due,outcome,notes',
    '',
    'responses.csv: date_received,opportunity_id,company,from_email,type,what_they_want,deadline_to_reply,handled',
    'seen.csv: company_domain,project_title',
    'holds.csv: id,company,reason,release_when,set_on',
    'country_priority.csv: rank,country,status,runs,rows_added,last_run,why   (status: pending | active | exhausted)',
    'source_registry.csv: source_name,url,country,type,needs_account,last_searched,rows_yielded,notes',
    'id_counter.txt: the highest number ever issued (IDs are PFE-0001, never reused)',
    'notes: one physical line, entries "YYYY-MM-DD text" joined by " | "',
]))
doc.add_heading('Spec format (04_outbound\\_gen\\run34\\specs\\<ID>.json)', level=2)
code_lines('\n'.join([
    '{ "source": "page read this run and date: the origin of the organisation-specific sentence",',
    '  "cv": { "summary": "...", "coursework": "comma-separated strings from COURSE_OK",',
    '          "instruments": [the 12 MASTER_INSTR in any order], "exp_order": [0,1,2], "proj_order": [0,1,2] },',
    '  "letter": { "to": ["line", ...], "subject": "...", "salutation": "...", "paras": ["...", ...],',
    '              "date": "28 September 2026 | 28 septembre 2026", "subject_label": "Subject: | Objet : ",',
    '              "close": "Kind regards, | Bien cordialement," },',
    '  "email": { "to": "address", "subject": "...", "body": "... Kind regards,\\n{{FULL_NAME}}\\n..." } }',
    'exp order: indexes of the three experiences of CV_MASTER_V2 in master order (0, 1, 2).',
    'proj order: indexes of the three projects of CV_MASTER_V2 in master order (0, 1, 2).',
    'COURSE_OK and MASTER_INSTR come from 00_profile\\personalisation_map.json (COURSES, INSTRUMENTS).',
    'Output: CV_{{FILE_STEM}}_<n>_v1, Letter_{{FILE_STEM}}_<n>_v1 (.docx + .pdf), email.md, letter.txt, notes.md.',
    'build.py prints: <ID> | CV pages=1 | Letter pages=1 | letter: <w>/400 words | email: <w>/180 words [BANNED ...] [OVER]',
]))
doc.add_heading('build.py contract: CV_MASTER_V2.docx paragraphs', level=2)
code_lines('\n'.join([
    ' 0 name                      1 contact line            2 PROFESSIONAL SUMMARY',
    ' 3 summary text (1 run: replaced by the spec summary; must start "Final-year")',
    ' 4 TECHNICAL SKILLS          5 "Instruments operated:" + run 2 = instrument list (reordered)',
    ' 6 Software  7 Methods  8 Quality frameworks',
    ' 9 PROFESSIONAL EXPERIENCE (anchor)',
    '10-13 experience 0 (org line, role, 2 bullets)   14-17 experience 1   18-20 experience 2 (1 bullet)',
    '21 ACADEMIC & RESEARCH PROJECTS (anchor)',
    '22-26 project 0   27-31 project 1   32-34 project 2',
    '35 EDUCATION  36 {{SCHOOL}} line  37 degree',
    '38 "Selected coursework:" + run 2 = coursework (from the spec, only COURSE_OK strings)',
    '39 LEADERSHIP & VOLUNTEERING  40-41 bullets',
    'A4, Calibri, one page. build.py asserts paragraphs 3, 5 and 38 before editing.',
]))

# ------------------------------------------------------------------ C
doc.add_heading('Appendix C. History', level=1)
table([
    ['Version', 'Date', 'What changed'],
    ['33 (rules 30)', '31 Oct 2026', 'Referral rule. A reply naming another person with an address makes /pfe-inbox add a new row (address from the email, source referral: <referrer>, <original ID>, status enriched, contact_confidence verified). The Applier ranks these rows first among email rows, whatever their score, as cold emails under every send check, and the letter and email cite the referrer unless they refused. An auto-reply naming a replacement contact adds the row with source referral, no citation. A redirect to a portal, a job board or a shared address is not a referral. A name with no address gets no row and one next_actions item. CLAUDE.md REFERRALS.'],
    ['32 (rules 29)', '31 Oct 2026', 'Waiting list tab (waiting_list.csv, tracker_tools.load_waiting / upsert_waiting / refresh_waiting): one row per tracker row at applied with no line in responses.csv, status waiting, follow_up or followed_up in that file only. /pfe-inbox refreshes it after the replies are processed and sends its follow-ups from the follow_up rows, oldest followup_due first, same 12 working days, cap 15 and checks. Portal rows with no address stay on the list, nothing is sent, with one next_actions item. Self-check: tracker_tools.py test-waiting.'],
    ['31 (rules 28)', '28 Oct 2026', 'Applier draft mode: the word draft in the arguments (/pfe-applier 20 email draft) builds the documents and Gmail drafts and checks the attachments on the Drafts list, but never calls send_message. Each draft stays queued, DRAFTED, reason DRAFT_ONLY; the email number counts drafts made and the 50/day cap does not limit it. /pfe-send lists them in section H and sends only the ones named (send H 1-20, send H all), after every send check, the cap included; /pfe-send-held never sends them. CLAUDE.md RUN SIZE and SENDING.'],
    ['30 (rules 27)', '22 Oct 2026', 'The transfer package is renamed sniper: the folder sniper\\, the archive sniper.zip with sniper/ inside, the download website (still the Worker zok-download). Setup prompt 28: STEP 6 LOCKDOWN matches exact names only (folder leaf sniper; zips ^(sniper( \\(n\\))?|zok ellougha( \\(n\\))?)\\.zip$; Recycle Bin entries named sniper, sniper.zip, sniper (n).zip or zok ellougha*), never a sniper* wildcard.'],
    ['29 (rules 27)', '22 Oct 2026', 'Next actions tab (next_actions.csv, the first sheet of tracker.xlsx, tracker_tools.upsert_action / load_actions): one row per thing to do by hand (choose or send an email, prepare a document, ask the school about the convention or a signature, prepare an interview, a visa step, apply by hand where a run was blocked), with ACT-NNNN id, type, due date, priority and status open, done or dropped. /pfe-inbox, /pfe-applier, /pfe-send and /pfe-cleanup add and close rows right after each row they work on; every report lists the actions added or closed. CLAUDE.md TOOLS AND PATHS and TRACKER AFTER EVERY ROW.'],
    ['28 (rules 26)', '22 Oct 2026', 'The author\'s own runbook in guides\\ is no longer rendered from this package: it is built from campaign\\_runbook\\make_runbook.py with the author\'s real values and mentions sniper in one section only. /forever rebuilds it there and never writes this runbook into guides\\. Nothing changes for a new user.'],
    ['27 (rules 25)', '20 Oct 2026', 'Companies first. SEARCH SCOPE: wherever a run decides where to look and in what order, industrial companies, SMEs, scale-ups and startups in the tracks come first (their R&D, production, quality and process teams), with startup sources in every country (incubator and accelerator portfolios, deep-tech and cleantech startup lists, national startup registries, company careers pages) and verified unadvertised company contacts (CTO, R&D lead, engineering manager, plant manager). Universities, public labs and institutes are still covered with the same rules, never screened out for being academic, no longer the default first stop. Startups pass every existing check and are scored honestly. Hunter report: company or startup rows vs academic rows, and the company sources tried when most rows are academic. Checker: company and startup rows before academic rows of similar fit.'],
    ['26 (rules 24)', '19 Oct 2026', 'The locked runbook of a user set up from sniper is a PDF: with RUNBOOK_LOCKED=1, make_runbook.py converts it through Word (docx2pdf, as build.py does for CVs), checks the PDF has pages and no BEGIN FILE or setup prompt, then deletes the .docx. Setup prompt 24 expects <CAMPAIGN_FILE_STEM>_Runbook_Claude_Code.pdf in guides\\; the kit CLAUDE.md points to that PDF. The shared runbook and the author\'s copy stay Word.'],
    ['25 (rules 23)', '19 Oct 2026', 'Rebuild gap closed for a locked install. The user\'s runbook in guides\\ is a locked copy (make_runbook.py RUNBOOK_LOCKED=1, setup prompt 23): no embedded file contents and no setup prompt; the author\'s copy stays full. The kit CLAUDE.md LOCKED INSTALL paragraph also forbids recreating, rebuilding or copying sniper or any part of it, extracting files or prompts from a runbook or guide, and creating new command, skill or rules files. The setup recreates a missing kit file only from the shared runbook in sniper and only before LOCKDOWN.'],
    ['24 (rules 22)', '18 Oct 2026', 'Locked install for a received package. The setup prompt (22) gains STEP 6 LOCKDOWN: the user\'s answers.json and any file of theirs in the package are kept, CLAUDE.md, the commands, settings.json and the guides are marked read-only, then sniper and its .zip are deleted for good (Recycle Bin entries of the package cleared too; skipped on the author\'s machine). /forever and /magic are author only: make_kit.py leaves them out of the kit (9 command files) and writes MANIFEST.txt; kit_blocks.json replaces their paragraphs in the kit CLAUDE.md with LOCKED INSTALL (Claude refuses any change to rules, commands, runbook or guides) and adds deny rules to the kit settings.json. The author\'s campaign is unchanged.'],
    ['23 (rules 21)', '18 Oct 2026', 'A new user\'s files and interview prep fit their own campaign and field. The runbook and Build Guide in guides\\ are named after CAMPAIGN_FILE_STEM (CAMPAIGN_NAME without spaces, derived by fill_placeholders.py): make_runbook.py takes RUNBOOK_OUT as a folder and render_guides.py names the Build Guide from the map; the shared copies stay PFE2027_*. The field-specific examples of /pfe-interview-prep (the "why this field" and "what if it fails" questions, the abbreviation example, the sketch shapes, axes, features and reading examples) are placeholders (FIELD_CHOICE_QUESTION, FAILURE_QUESTION, TECHNIQUE_ABBREV_EXAMPLE, SKETCH_SHAPES, SKETCH_AXES_EXAMPLE, SKETCH_FEATURES_EXAMPLE, READING_EXAMPLE) that the setup fills after S0 PROFILE from the new user\'s own techniques, with DECK_NOTE_EXAMPLE; before that second fill the setup copies the rule files from the kit again, so the neutral wording is really replaced. Setup prompt 21.'],
    ['22 (rules 20)', '18 Oct 2026', 'Guides without anyone\'s paths: the shared guides in sniper show example paths (C:\\Users\\<you>\\Desktop\\pfe workflow\\campaign, from render_guides.py without PFE_MAP). The setup no longer copies the shared PDFs into guides\\: at the end (STEP 3 on PATH A, STEP 4 on PATH B) it renders the user\'s own guides and runbook into ROOT\\guides with that machine\'s paths and values. Setup prompt 20.1. Friendly Setup and Usage gains a "Claude Code in simple words" section (PowerShell, cd, starting Claude, the main keys and commands).'],
    ['21 (rules 20)', '18 Oct 2026', '/ask-me added: a new user stuck on a step of the setup or a guide types /ask-me and pastes the step; Claude does it if it can or explains it again in simpler words. Every step of Friendly Setup and Usage ends with a "Stuck?" line saying how (steps 1 to 5: paste it at claude.ai). install.ps1 copies the command to the user\'s own .claude\\commands so it works in any folder. Listed in CLAUDE.md HOW THIS FOLDER WORKS, the command tables, the setup prompt and both guides; kit holds 11 command files.'],
    ['20 (rules 19)', '18 Oct 2026', 'One folder, pfe workflow: campaign\\ (the workspace, Claude Code opened there), interviews\\, my documents\\, guides\\, sniper\\ (the transfer package), archive\\ (rule snapshots, frozen data snapshot, parked junk). Every live path rewritten; /forever now updates the campaign and sniper (make_kit.py regenerates the kit templates from the live rules with personalisation_map.json and runs a privacy scan), snapshots go to archive\\rule snapshots. build.py, preflight.py and build_deck.js read personal facts from personalisation_map.json and profile_deck.json. Group 2 attachments from my documents are staged in 02_tracker\\_upload first. AGENTS.md regenerated from CLAUDE.md. The old data snapshot is frozen.'],
    ['19', '17 Oct 2026', 'Applier asks first: started without a method or number, its very first action is the method question (then portals, then numbers), before reading the tracker, counting rows or reading a PROGRESS file; asked even when a PROGRESS file exists, which then only skips IDs already done. Eligible counts are computed after the method answer, only to label the later questions.'],
    ['18', '17 Oct 2026', 'Applier: when Portal is chosen it stops, lists every portal (site of application_url) with its eligible rows and asks which portal(s) to apply through (multiSelect); only rows on those portals are worked; portal sites after the word portal answer in advance (CLAUDE.md RUN SIZE, /pfe-applier). Interview deck: the model is {{FIRST_NAME}}\'s edited {{DECK_MODEL_SHORT}} deck; build_deck.js drops the India slide "Three things the numbers told me" and the agenda notes, the PFA lessons slide is no longer used, and speaker notes say the slide simply, then the result, with over-explanation between // and // (CLAUDE.md, /pfe-interview-prep).'],
    ['17', '17 Oct 2026', 'Interview folder: the NotebookLM prompt is always a plain-text note, NOTEBOOKLM_PROMPT.txt (UTF-8, no Markdown syntax: headings as plain capital lines, the text to paste between COPY FROM HERE and COPY TO HERE lines), never .md (CLAUDE.md, /pfe-interview-prep). The existing prompts in the interviews folder were converted.'],
    ['16', '17 Oct 2026', 'Cost audit of the /pfe-* commands (05_reports\\2026-10-17_cost_audit.md). Hunter: the main session runs no WebSearch or WebFetch; every search and page read goes to a subagent (main-session searches ran at about 440k context, about seven times the cost of a subagent call). No other rule changed.'],
    ['15', '17 Oct 2026', 'Applier email route made cheaper without changing what it sends: PDFs copied once per batch into 02_tracker\\_upload\\<ID>\\ right after build.py (deleted at the end or when the run stops); one javascript_tool wait per draft for the uploads (30 s, one reload and retry, then DRAFTED ATTACH_TIMEOUT); batches of up to 10 email rows in two phases (A: compose, each draft recorded as queued, draft composed, COMPOSED in PROGRESS; B: one connector listing, one Drafts-list read, send checks, send, tracker after each send); no ls/cat/Get-ChildItem checks between rows. SENDING check 4 now reads the Gmail Drafts list in Chrome instead of get_draft, which returned empty autosaves in run65 (Applier and /pfe-send-held).'],
    ['14', '14 Oct 2026', '/magic added: guided review of one command at a time (task map with line numbers, keep / change / remove / explain more / stop for each task, conflict check against CLAUDE.md), approved changes applied through /forever. Listed in CLAUDE.md HOW THIS FOLDER WORKS, the command tables and both guides; kit and data now hold 10 command files.'],
    ['13', '14 Oct 2026', 'Applier asks the application method as well as the number: one AskUserQuestion (multiSelect Email / Portal, with eligible rows per method and cold emails left under today\'s cap), then how many applications of each (10, 25, 50, ALL or any number). Arguments such as 20 email, ALL portal, 15 email 10 portal answer in advance; a bare number still asks for the method. The number counts only emails sent and portal forms submitted; rows of a method not chosen get no documents and no status change; documents built only for selected rows, in small batches if needed; PROGRESS file records methods and numbers; report per method (requested, done, skipped, left). CLAUDE.md RUN SIZE, /pfe-applier.'],
    ['12', '13 Oct 2026', 'Interview prep, deck and NotebookLM prompt: never mention {{NEVER_MENTION}} or use it as an argument (CLAUDE.md, /pfe-interview-prep, DEFENSIBLE_CLAIMS #11). build_deck.js: the first card of "Three things the numbers told me" replaced by the R/G + chroma dual signal.'],
    ['11', '13 Oct 2026', '/pfe-interview-prep: one folder per interview, interviews\\<YYYY-MM-DD>_<Organisation>_<Interviewer>\\ (date from interviews.csv; unknown: today and _date-TBC), with the prep PDF, a short self-presentation deck (<date>_<Organisation>_presentation.pptx, built by the new kit file 00_profile\\interview_deck\\build_deck.js) and NOTEBOOKLM_PROMPT.md (a coaching prompt in the interview language, ending in a one-question-at-a-time mock interview). Nothing loose in the interviews root. Existing preps sorted into folders the same day. Setup: Node.js and npm install for the deck builder.'],
    ['10', '10 Oct 2026', '/pfe-interview-prep: every prep PDF is also kept, same file name, in the interviews folder on the Desktop instead of the Desktop itself, each time it is built or rebuilt. CLAUDE.md TOOLS AND PATHS carries the rule.'],
    ['9', '10 Oct 2026', 'Unpaid or low-paid offers: never declined, never answered with self-funding. Group 3 drafts negotiate a researched monthly figure tied to the visa proof of means or legal minimum, with alternatives (partial allowance, housing, grant, project contract). /pfe-inbox counts an unpaid offer as offer, not rejected. New CLAUDE.md section UNPAID OR LOW-PAID OFFERS.'],
    ['8', '8 Oct 2026', 'Offers tab (offers.csv, tracker.xlsx, tracker_tools.upsert_offer): one row per opportunity offered to me, with supervisor, project, country, dates, stipend, visa support, convention status, thread link, stage (offer_received to convention_signed, declined, withdrawn) and next step. /pfe-inbox updates it every run and lists it in its report; /pfe-send updates it after an offer reply.'],
    ['7', '7 Oct 2026', 'Interviews tab (interviews.csv, tracker.xlsx): new column interview_language between interviewer and interviewer_email, filled by /pfe-inbox from what the emails state. An older interviews.csv without it still loads and gains it on its next write.'],
    ['1 Cowork', '19-24 Sep 2026', 'tea.docx: Project + Cowork conversations, scheduled Inbox and Review in Cowork, {{FIRST_NAME}} sends every email.'],
    ['2 Claude Code', '27 Sep 2026', 'Slash commands = tea.docx prompts word for word + adaptation blocks; Task Scheduler; four tasks; sending only in /pfe-send.'],
    ['2.1', '28 Sep 2026 (night)', 'One daily chain + gate.py; automatic sending with five checks and the 25/day cap; holds.csv; FORM_ANSWERS.md; /pfe-send-held; plugins trimmed.'],
    ['3.1', '28 Sep 2026', 'data\\ snapshot refreshed daily (snapshot.py); preflight.py machine check in the popup; Gmail u/0 verified; setup prompt: PATH A FROM SNAPSHOT and AUTOMATED MODE; one-time task installed v3 after the 28 Sep chain.'],
    ['3.2', '28 Sep 2026', 'Budget: the Hunter burst ($11 in 6 min) hit the plan limit twice and saved nothing. Every step now has a hard --max-budget-usd cap inside an 11.5 chain budget (window about 13), Hunter last, batches Checker 15 / Applier 8 / Hunter 25 rows and 40 searches, at most 2 subagents at a time, rows saved as each subagent returns, COST line per step, test-budget.ps1.'],
    ['3.3', '28 Sep 2026', 'Cold-email cap raised from 25 to 50 a day ({{FIRST_NAME}}). The Applier budget is unchanged, so the budget, not the cap, still limits emails per day.'],
    ['4', '4 Oct 2026', 'Daily chain and Task Scheduler removed: every command is started by hand. Applier row count asked at the start.'],
    ['5.1', '7 Oct 2026', '/forever added: the one command that changes a rule everywhere (workspace, kit, data, setup prompt, runbooks, guides, memory) and verifies nothing old is left.'],
    ['6', '7 Oct 2026', '/pfe-interview-prep: new section 6A TECHNIQUES (every technique on the CV and used by the host: definition, problem it targets, what it measures, inline SVG sketch of the typical graph with labelled axes, a full spoken answer); full answers modelled on the {{PREP_MODEL_SHORT}} prep (5 Oct 2026). Interview prep PDF built from HTML so the sketches show.'],
    ['5', '6 Oct 2026', 'No hard limits: Checker and Applier ask how many rows (any number or ALL), Hunter covers every available opportunity in the country, no search, subagent or spending caps; BUDGET section removed from CLAUDE.md. Email caps kept (50 a day, 15 follow-ups, 10 Group 2 replies). Every command updates the tracker after every row and every action (TRACKER AFTER EVERY ROW). /pfe-send-held and /pfe-send aligned to the 50/day cap.'],
    ['3', '28 Sep 2026', 'Commands rewritten as Claude Code-native prompts; CLAUDE.md merged into one rule set; country_priority.csv (15 countries, one until exhausted, track ALL); Chrome profile opened by the chain; self-closing popup; block_row(); OneDrive retry in tracker_tools; kit + runbook + guide + setup prompt v3.'],
], widths=[2.4, 3.2, 11.8])

if FILL:   # personal copy: every run that still holds a placeholder gets its value
    for par in doc.paragraphs + [p for t in doc.tables for r in t.rows for c in r.cells for p in c.paragraphs]:
        for run in par.runs:
            if '{{' in run.text:
                run.text = fill(run.text)
doc.save(OUT)

# ------------------------------------------------------------------ self-check: re-extract every file
d = Document(OUT)
paras = [p.text for p in d.paragraphs]
found, i = {}, 0
while i < len(paras):
    if paras[i].startswith('BEGIN FILE '):
        rel = paras[i][len('BEGIN FILE '):]
        j = paras.index('END FILE', i)
        found[rel] = '\n'.join(paras[i + 1:j]); i = j
    i += 1
if LOCKED:   # a locked copy must hold no file and no setup prompt
    text = '\n'.join(paras + [c.text for t in d.tables for r in t.rows for c in r.cells])
    assert not found and 'BEGIN PROMPT setup' not in text, 'locked copy still holds files or the setup prompt'
    print('locked copy: no embedded files, no setup prompt')
    bad, missing = [], []
else:
    bad = [rel for rel in KIT_FILES if found.get(rel) != fill(read(rel))]
    missing = [rel for rel in KIT_FILES if rel not in found]
print(f'{OUT}\n{len(found)} files embedded, {len(KIT_FILES)} in kit; missing {missing}; mismatched {bad}')
assert not bad and not missing
if LOCKED:   # deliver the locked copy as PDF only
    import pypdf
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '03_kit', 'campaign', 'scheduler'))
    import platform_env
    pdf = platform_env.docx_to_pdf(OUT, os.path.splitext(OUT)[0] + '.pdf')
    ptext = '\n'.join((pg.extract_text() or '') for pg in pypdf.PdfReader(pdf).pages)
    # prose may name the markers; an embedded file is a line that starts with one
    assert len(pypdf.PdfReader(pdf).pages) > 0 and not re.search(r'(?m)^\s*BEGIN (FILE \S|PROMPT setup)', ptext), 'locked PDF check failed'
    os.remove(OUT)
    print(f'locked PDF: {pdf} ({len(pypdf.PdfReader(pdf).pages)} pages); .docx deleted')
