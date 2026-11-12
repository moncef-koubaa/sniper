# sniper: start here

This folder is a complete PFE (final-year internship) campaign system run by Claude Code:
it finds internships country by country, checks contacts, writes a tailored one-page CV and letter for each,
submits portal forms, sends application emails within strict checks, reads your mailbox and prepares your
interviews. It runs on Windows, Linux or macOS. You start every job yourself with a slash command; nothing runs on a schedule.
It holds none of its author's personal data: every personal detail is a `{{PLACEHOLDER}}` that the setup fills
with yours (PERSONALISE.md lists them). Rules version: see VERSION. What changed: CHANGELOG.md.
**This package stays.** The setup builds your campaign next to it and locks nothing: `sniper` remains the
reference copy (setup prompt, kit, build sources), and you can change the rules and commands of your campaign
by asking Claude (CLAUDE.md, OPEN INSTALL).

## The 6 steps

| # | Step | Time |
|---|---|---|
| 1 | Copy this whole folder into an empty folder of its own, for example `Desktop\pfe workflow\sniper` (Linux: `~/pfe-workflow/sniper`). The setup builds your campaign next to it. | 5 min |
| 2 | Install the tools: read `01_install\README.md`, then in `01_install` run `powershell -ExecutionPolicy Bypass -File .\install.ps1` (Windows) or `bash install.sh` (Linux, macOS). It must end with "all checks passed". Also install what its TO FIX list names (Claude Code, Node.js, Word or LibreOffice, Chrome). It writes the machine settings to `.env` next to `sniper` (see `01_install\.env.example`). | 30 to 45 min |
| 3 | Chrome and connectors: in your campaign Chrome profile add the **Claude in Chrome** extension (site access "On all sites", "Act without asking") and log in to Gmail, LinkedIn, Indeed and your job sites. On claude.ai, Settings, Connectors: connect Gmail, Google Drive, Google Calendar and Indeed. In Gmail, create the label you want campaign mail filed under. | 15 min |
| 4 | Open PowerShell (Linux, macOS: a terminal) in the folder that holds `sniper`, type `claude --chrome`, accept the folder, type `/chrome` and choose "Enabled by default". Paste everything below the line of `02_setup_prompt\PFE_CLAUDE_CODE_SETUP_PROMPT.md`. Answer its questions in one reply (or fill `02_setup_prompt\answers.json` from `answers_TEMPLATE.json` first). | 10 min |
| 5 | Let it work: it creates `campaign\`, `interviews\`, `my documents\` and `guides\`, fills every placeholder ("placeholders left: 0"), asks you once for your CV, reports and letters, builds your profile, runs a smoke test, and finishes without locking or deleting anything. | about 1 hour |
| 6 | Open a new Claude Code session in `campaign\` and type the first command it names (`/pfe-hunter` on a new campaign). From then on: your own `guides\Friendly Setup and Usage.pdf`, section "every day". | 2 min |

Stuck on a step? Once install.ps1 has run (step 2; it installs `/ask-me`), open Claude Code, type `/ask-me`, a
space, and paste the step: Claude does it for you if it can, or explains it again in simpler words. Before
that, paste the step at claude.ai.

## What is in here

- `01_install\` tools, tested versions, requirements.txt, package.json, install.ps1 (Windows), install.sh (Linux, macOS), .env.example
- `02_setup_prompt\` the setup prompt, answers_TEMPLATE.json, fill_placeholders.py
- `03_kit\` the workspace template (campaign, interviews, my documents)
- `04_runbook_and_guides\` runbook (every prompt and file), Build Guide, Friendly Setup and Usage
- `05_build_sources\` what rebuilds the kit and the docs (used by the author's /forever)

## Rules you will meet

Nothing is ever scheduled. Never more than 50 cold emails a day. Nothing is invented: unknown contacts stay
UNVERIFIED. Interviews, offers, money and visa replies are never sent automatically. Your campaign is an open
install: rules and commands change only when you ask Claude for the change, and Claude Code asks before each edit.
