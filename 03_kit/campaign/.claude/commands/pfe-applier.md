---
description: APPLIER run, by the method(s) and number of applications {{FIRST_NAME}} chooses (email, portal or both, no limit) - documents built, portals submitted, emails sent within the checks and the 50/day cap, or only drafted with the word draft
argument-hint: "[<n or ALL> email] [<n or ALL> portal [<site> ...]] [draft]"
---
APPLIER RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md (SENDING, FORMS, HOLDS, BROWSER SPEED, WRITING). After the method, portal and number questions
below, never wait for a reply from me. It does not hunt.

ASK FIRST (added 17 Oct 2026)
If the arguments do not give the method, or do not give a number for each method given, the very first
action of the run is the questions in METHOD, PORTALS AND NUMBER below, before reading the tracker,
counting rows, reading a PROGRESS file or doing anything else. Nothing else starts until every missing
answer is given. This holds when a PROGRESS file exists too.

RESUME (changed 17 Oct 2026)
If 05_reports\*_applier_PROGRESS.md exists, this is a continuation, but the questions are still asked
when the arguments leave anything open (ASK FIRST). The answers given now set the methods, portals and
numbers; the PROGRESS file is used only to skip every ID already marked with an outcome. A row marked
COMPOSED reuses its Gmail draft and goes straight to STEP 3 phase B.

NO VERIFICATION LISTINGS (added 17 Oct 2026)
Do not run ls, cat, dir, Get-ChildItem or Get-Content to check files between rows. Trust the output of
build.py (page counts, refusals), tracker_tools and unblock_tools. Read a file only when a tool reported
an error, or when the run needs its content (spec, email.md, notes).

METHOD, PORTALS AND NUMBER (CLAUDE.md RUN SIZE, no hard limit; changed 17 Oct 2026)
1. Method first. If the arguments give no method, ask step 3 now, as the first action of the run, with
   plain options "Email" and "Portal" (no counts yet). Only after the method is known, count the eligible
   rows for each chosen method, only to label the portal and number questions, skipping held rows
   (holds.csv and the automatic holds):
   - EMAIL: rows with best_method email (send route through Gmail): referral rows (source starting with
     "referral") at any priority or score, queued rows with no Gmail draft yet, enriched rows priority A
     and B, then C with match_score 50 or more.
   - PORTAL: rows with best_method web form (same statuses), plus blocked.csv rows whose only blocker was
     "no browser" or a portal route not yet tried.
   Also count the cold emails still allowed today: 50 minus tracker rows with date_applied today and
   email_sent set (CLAUDE.md SENDING 5).
2. Arguments answer the questions in advance: `20 email`, `ALL portal`, `15 email 10 portal` (a number or
   ALL followed by a method), and portal sites after the word portal (`10 portal jobs.veolia.com
   admissions.kaust.edu.sa`). A bare number with no method (`30`) still asks for the method; portal with
   no site still asks for the portals. The word draft anywhere in the arguments turns on DRAFT MODE
   below (`20 email draft`); it changes nothing for portal rows.
3. Otherwise ask {{FIRST_NAME}} with ONE AskUserQuestion call, before anything else: "Which application method(s)
   should this run use?" (multiSelect: true), options "Email" and "Portal".
4. PORTALS (added 17 Oct 2026). When Portal is chosen and no site was given, stop before any portal work.
   Group the eligible PORTAL rows by portal: the host of application_url without "www." (rows with no
   application_url: "(no URL)"). Show {{FIRST_NAME}} the full list in the answer, one line per portal, largest
   first: portal, number of eligible rows, the companies. Then ONE AskUserQuestion (multiSelect: true):
   "Which portal(s) should this run apply through?", options the three largest portals as "<portal> (<n>
   eligible)" and "All portals (<n> eligible)"; he can type any other portal names. Do not proceed until
   answered. Only rows on the chosen portals are PORTAL candidates; rows on other portals are left alone.
5. Then, for each method ticked and not yet given a number, one AskUserQuestion: "How many <method>
   applications?" (for Portal, the eligible count on the chosen portals) with choices 10, 25, 50 and
   ALL; he can type any number. If the email number chosen or offered is above what is left under
   today's cap, the question says so (drafts over the cap wait for /pfe-send-held and do not count as
   sent); in DRAFT MODE the email question is "How many email drafts?" and says nothing about the cap.
   Do not proceed until answered.
6. The number is the number of applications completed by that method: emails sent, or portal forms
   submitted (APPLIED). Rows that end DRAFTED, BLOCKED, NO_CONTACT or EXPIRED do not count toward it: move
   to the next eligible row of that method until the number is reached or the method runs out of rows. ALL
   means every eligible row of that method (for Portal, on the chosen portals). Portals never count
   toward the email cap. In DRAFT MODE the email number counts drafts made (DRAFT_ONLY) instead.
7. Rows of a method not chosen, and portal rows on portals not chosen, are left alone: no spec, no
   documents, no status change. They stay eligible for the next run.

DRAFT MODE (added 28 Oct 2026; CLAUDE.md RUN SIZE and SENDING)
Turned on by the word draft in the arguments. The email route runs STEP 1 and STEP 3 phase A as usual,
and phase B up to and including the checks, but never calls send_message. A draft that passes every
check except the 50/day cap ends DRAFTED, reason DRAFT_ONLY, and counts toward the email number. A draft
that fails another check ends DRAFTED with that reason and does not count. The 50/day cap neither stops
nor limits the run. The PROGRESS file records "draft mode". /pfe-send-held never sends DRAFT_ONLY
drafts; only /pfe-send sends them, the ones {{FIRST_NAME}} approves.

TARGET LIST, per chosen method, in this order (the tracker and the PROGRESS file are saved after every
row), skipping held rows:
- PORTAL (only rows on the chosen portals)
  1. blocked.csv rows whose only blocker was "no browser" or a portal route not yet attempted, documents
     already in 04_outbound\<ID>. Check the posting is still open, then apply. New documents only if the
     old ones name a wrong date.
  2. queued and enriched web form rows: priority A and B, then C with match_score 50 or more.
- EMAIL
  1. referral rows (added 31 Oct 2026; CLAUDE.md REFERRALS): source starting with "referral", enriched or
     queued with no Gmail draft yet, at any priority or score. They rank above every other email row.
  2. queued rows with no Gmail draft yet (build documents first if missing).
  3. enriched rows priority A and B, then C with match_score 50 or more.
Within each group: nearest deadline first, then highest match_score. "Profile is weak" is not a reason
to skip: apply to B and C rows the same way as A rows. Do not re-rank on your own judgement.
Before the first action write 05_reports\<YYYY-MM-DD>_runNN_applier_PROGRESS.md with the methods chosen,
the portals chosen, the number requested per method (or ALL), the done count per method (0) and the ordered candidate ID list
per method. The numbers are the job. Every ID worked ends with exactly one outcome:
  APPLIED     portal form submitted, or email sent
  DRAFTED     Gmail draft ready but a send check failed (cap reached, held, address already emailed,
              ATTACH_TIMEOUT), or DRAFT_ONLY in DRAFT MODE
  BLOCKED     CAPTCHA, login wall, account creation, Easy Apply / Indeed Apply, or NEEDS_ANSWER
  NO_CONTACT  email route but no verified address
  EXPIRED     posting gone when opened
Update the PROGRESS file after every row (outcome, done count per method and last completed ID). An email
row whose draft is composed is marked COMPOSED until STEP 3 phase B gives it its outcome. IDs on
the candidate list never reached keep no outcome and are left alone.

STEP 1, DOCUMENTS (selected rows without documents)
Build documents only for rows the run has selected from its candidate lists. For each row write
04_outbound\_gen\run34\specs\<ID>.json (format: runbook appendix "spec format"; subagents draft them, 2 or
3 rows each, each reading the row, its notes and the host page), then run ONE build.py call per batch:
  build.py <ID> <ID> ...
Small batches as the run goes are allowed (for example the next few candidates of each method), so that
rows that fail can be replaced by the next eligible row of the same method.
- PDF staging (changed 17 Oct 2026): right after each build.py call, copy in ONE shell command the CV PDF
  and letter PDF of every email row in that batch into 02_tracker\_upload\<ID>\ (Chrome file_upload only
  accepts files under the session folder). Gmail uploads use those paths. Never copy per row.
- CV: from CV_MASTER_V2. Change the summary, the order of experiences and projects, the coursework shown
  (only the approved course strings build.py accepts), the instrument order. Never change a fact, date,
  number, title or result. Never add a skill.
- Letter (under 400 words) and email (under 180 words): CLAUDE.md WRITING. One sentence only this
  organisation could get, from something read on their site this run (record the page and date in the
  spec "source"). The dates / 26 weeks / convention de stage / visa paragraph near the end. Letter in the
  language of the posting (French letters: French date, "Objet : ", "Bien cordialement,").
- Referral rows (added 31 Oct 2026; CLAUDE.md REFERRALS): source "referral: <name>, ...": the first
  lines of the letter and of the email say <name> suggested I contact them, and nothing else about
  <name>. Source "referral, no citation: ...": nobody is cited, the row is written like any other.
- Every new spec sets "date" to today in the letter's language.
- Quality gate: swap test on every pair of openings in the batch; rewrite both of any swappable pair.
  build.py refuses banned words and em dashes: fix and rebuild, never bypass. Both documents one page.
- Paste the first three letters of the run into the report (instead of stopping to show me).

STEP 2, PORTAL ROWS (best_method web form)
1. Open the application page in the working tab. Know the ATS from the URL (BROWSER SPEED 8).
2. Fill standard fields from 00_profile\FORM_ANSWERS.md (email always {{GMAIL_ACCOUNT}}).
   Upload the tailored CV and letter PDFs from 04_outbound\<ID>\.
3. Free-text questions: answer with the letter rules, submit, copy each answer into notes.md.
4. A required question with no truthful answer in FORM_ANSWERS.md (passport or ID number or upload, a /20
   average or exact rank, numeric salary, postal code, legal visa declaration, a filtering question whose right answer is not
   obvious from my profile): do not submit; BLOCKED, reason NEEDS_ANSWER, with the exact question.
5. Submit. Save the confirmation text into notes.md. Portals do not count toward the email cap: when the
   cap is reached and Portal was chosen, keep going with portal rows.
6. CAPTCHA, a login I am not signed into, account creation, LinkedIn Easy Apply, Indeed Apply: BLOCKED,
   never attempted.

STEP 3, EMAIL ROWS (best_method email; two phases per batch of up to 10 rows, changed 17 Oct 2026)
- Address UNVERIFIED: NO_CONTACT.
- Phase A, compose, one row at a time: build the Gmail draft in Chrome with GMAIL COMPOSE (BROWSER SPEED
  10): to the verified address only, subject naming the project title or the department and field (never
  "Internship application" alone), body from email.md, CV PDF and letter PDF from 02_tracker\_upload\<ID>\
  attached, ONE javascript_tool wait call for the uploads (timeout: one reload and one retry, then
  DRAFTED, reason ATTACH_TIMEOUT). Reuse an existing draft for the row; never make a second one. Never
  leave a "Leave site?" dialog. After each draft: update_status(id, "queued", "<date> draft composed,
  subject: ...") and mark the row COMPOSED in the PROGRESS file.
- Phase B, check and send, once the batch is composed: ONE connector call lists the batch's drafts
  (list_drafts or search_threads in:drafts) for the draft ids. Then ONE full-reload read of the Gmail
  Drafts list in Chrome (javascript_tool: every draft's recipient and attachment names) confirms both
  PDFs on each draft (CLAUDE.md SENDING 4). Run the other SENDING checks per draft (swap test and banned
  words, address never emailed, holds, 50/day cap), then send_message(draftId) for each draft that
  passes. Right after each send, before the next one: tracker updated (STEP 4 APPLIED), sent_<date>.md
  saved, PROGRESS updated.
- A draft that fails a check: DRAFTED, update_status(id, "queued", "draft ready <date>, subject: ...,
  held: <reason>") and list it. Drafts over the cap are sent first tomorrow by /pfe-send-held (note
  "over the 50/day cap").
- DRAFT MODE: no send_message. Each draft that passes every check except the cap: DRAFTED,
  update_status(id, "queued", "draft ready <date>, subject: ..., held: DRAFT_ONLY, waiting for
  /pfe-send"), PROGRESS updated.

STEP 4, TRACKER AFTER EVERY ROW, WHATEVER THE OUTCOME (CLAUDE.md TRACKER AFTER EVERY ROW)
Immediately when a row gets its outcome, before the next row:
- Documents built: update_fields(id, cv_version=..., letter_version=...) with a note line, right after
  build.py, row by row.
- APPLIED: status applied, date_applied today, cv_version, letter_version, email_sent (email rows),
  followup_due = unblock_tools.workdays(today, 12), one note line. Blocked rows come back with
  unblock_tools.apply_row(id, note, cv_version=..., letter_version=...). Sent email bodies saved as
  04_outbound\<ID>\sent_<date>.md.
- DRAFTED: update_status(id, "queued", ...) as in STEP 3.
- EXPIRED: update_status(id, "expired", "<date> posting gone when opened").
- NO_CONTACT: tracker_tools.archive_rows(ids=[id]) (dedup key to seen.csv, row out of tracker.csv).
- BLOCKED: unblock_tools.block_row(id, "<RUNNN> BLOCKED: <reason>; documents in 04_outbound/<ID>") moves
  the whole row to blocked.csv; 04_outbound\<ID>\ stays in place.
- Next actions (added 22 Oct 2026), right after the row's own write: a BLOCKED row only I can finish
  (NEEDS_ANSWER, EASY_APPLY, CAPTCHA, login wall, account creation, SESSION EXPIRED) gets
  tracker_tools.upsert_action(opportunity_id=id, type="application" ("other" for SESSION EXPIRED),
  action="<what to do by hand: the exact question, or apply at the URL>", due_date=<deadline if
  stated>, source_command="pfe-applier"); a DRAFTED row held for a reason other than the daily cap
  gets type "email", action "decide on the held draft in /pfe-send: <reason>" (DRAFT_ONLY included). A row later sent or
  submitted closes its open action (status done).
The run is not complete until every row with an outcome is updated in the tracker.

IF THE CONTEXT RUNS LOW, OR THE RUN HITS THE PLAN USAGE LIMIT
Stop cleanly after the current row: tracker saved, PROGRESS file up to date (COMPOSED rows included),
02_tracker\_upload\ deleted in one command. The next /pfe-applier resumes from it.

END OF RUN
Delete 02_tracker\_upload\ in one command. Rename the PROGRESS file to <YYYY-MM-DD>_runNN_applier.md (only when each chosen method has reached its
number or run out of eligible rows) and write in it: a table of every ID worked with its method and
outcome, the first three letters, the DRAFTED list with reasons, HELD, then the numbered BLOCKED list: ID,
company, what blocked it (the exact question for NEEDS_ANSWER), direct URL.

STEP 5, FINAL COUNT (rows were already moved in STEP 4; rows never reached are left alone)
For each method chosen: the number requested, the number done (APPLIED; DRAFT_ONLY in DRAFT MODE), the rows skipped and why
(DRAFTED, BLOCKED, NO_CONTACT, EXPIRED, HELD) and the eligible rows still left for that method. For each
method not chosen: the eligible rows left for it. Then rows moved to seen.csv, rows moved to blocked.csv,
rows remaining in tracker.csv, and the manual queue as a numbered table: ID, company, blocker, URL,
documents folder.

Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: <application drafts still waiting>`.