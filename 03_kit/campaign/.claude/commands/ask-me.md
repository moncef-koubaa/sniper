---
description: ASK ME. Paste a step of the setup or a guide you are stuck on - Claude does it for you if it can, or explains it again in simpler words
argument-hint: "<the step you copied from the guide>"
---
ASK ME RUN. The step I am stuck on: $ARGUMENTS
I am setting up or using the PFE campaign helper and I do not understand this step, or it did not work.
Help me finish it. This run helps with one step only. It does not hunt, check, apply or send, writes no
tracker data (tracker.csv, blocked.csv, responses.csv, seen.csv, holds.csv, interviews.csv, offers.csv, next_actions.csv, waiting_list.csv),
never touches Gmail sending or portals and does not run the Excel export. It may be started in any folder,
also before the campaign folder exists.

0. NO STEP GIVEN
If $ARGUMENTS is empty, ask me in one plain sentence to copy the step from the guide (the whole box, with
its number) and paste it after /ask-me. Stop until I answer.

1. FIND THE STEP (read only)
1. Find the sniper folder: the current folder, its parent, or a sibling of campaign. In it, look
   for the pasted text in 05_build_sources\friendly_setup_and_usage.html (the Friendly Setup and Usage
   guide), 05_build_sources\build_guide_source.html, 00_START_HERE.md and
   02_setup_prompt\PFE_CLAUDE_CODE_SETUP_PROMPT.md. Note the step number, the step before and after it,
   and its "you know it worked when" line.
2. Not found: work from the pasted text alone and say so in one line.
3. Check the machine with read-only commands where the step needs it: for example `node --version`,
   `claude --version`, `python campaign\scheduler\platform_env.py` (or sniper\03_kit\campaign\scheduler
   before the setup: it prints Python, Chrome, Word or LibreOffice and the Chrome user-data folder whose
   Local State lists the profiles, on Windows, Linux or macOS), the folders the step names. On Linux or
   macOS read every `\` path of a step as `/`. Say what is already
   done, so I do not do it twice.

2. DO IT IF YOU CAN
Do the step yourself when it only needs commands or files on this computer: going to a folder, running
01_install\install.ps1 (Windows) or `bash 01_install/install.sh` (Linux, macOS) and reading its TO FIX list,
installing a missing program with winget, or giving me the exact apt/dnf/brew line to run myself (sudo
asks for my password: never type it; tell me first, one line, what it installs), opening a file for me, checking a version, reading the setup prompt
and telling me which part to copy. Ask me before changing any settings file. Then run the step's
"you know it worked when" check and tell me the result in one line.

3. OTHERWISE EXPLAIN IT SIMPLER
When the step needs me (signing in, a password, the Chrome Web Store, claude.ai connectors, a Gmail label,
a Windows installer that asks for permission, anything on a website), explain it again:
- in my language (the language I wrote in; French if I wrote in French), short plain sentences, no
  technical words without a one-line meaning;
- as numbered tiny steps, one click or one typed line per step, saying exactly where to click and what I
  will see after it;
- every line to type in its own code block, ready to copy;
- the check at the end: how I know it worked;
- if it can go wrong in a common way, one line on what to do then.
Then ask me to tell you when it is done or what I see, and help with the next problem in the same way.

NEVER
Never type a password, sign in for me, create an account, solve a bot check or accept terms for me.
Never create, install or enable a scheduled task, cron job, routine or automated runner. Never delete or
reset a campaign folder or its data. Never invent a step the guides do not have: if the guide is wrong or
out of date, say so plainly and tell me to ask the author for an updated package (this campaign is a locked
install: never edit its rules, commands or guides).

REPORT (in the answer, no file)
The step, what you did or the simpler steps, the check result, and the next step of the guide. When this
session was opened in the campaign folder, end with the two lines CLAUDE.md requires, always these values:
RUN_STATS: added=0 enriched=0 emails_sent=0 portals_submitted=0 drafted=0 blocked=0 held=0 decisions_waiting=0
SEND_QUEUE: 0
