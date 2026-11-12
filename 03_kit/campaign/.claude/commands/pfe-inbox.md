---
description: INBOX run, daily. Files PFE mail, sends Group 2 replies, drafts Group 3 options, sends due follow-ups, expires rows, updates the tracker
argument-hint: "[FULL SWEEP]"
---
INBOX RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md. This run reads my PFE mail, labels it, replies only where the rules below allow,
drafts options where they do not, sends due follow-ups, expires dead rows and records everything. It does
not hunt or apply.

SCOPE: mail from the last 36 hours (queries use newer_than:2d). If the arguments say FULL SWEEP: all mail
since {{CAMPAIGN_START}} and every PFE thread not yet labelled (queries use after:{{CAMPAIGN_START}}).

1. MATCH LIST
Load tracker.csv and blocked.csv. Collect every company_domain, supervisor_email and hr_email (split on
";") and every company name.

2. FIND THE THREADS (Gmail connector, follow pageToken to the last page)
  a. label:{{GMAIL_LABEL_ID}} newer_than:2d
  b. in:sent newer_than:2d
  c. from:(tracker domains, about 15 per query joined with OR) newer_than:2d
  d. subject:(PFE OR stage OR internship OR thesis OR "Masterarbeit" OR "projet de fin" OR candidature OR
     application OR Bewerbung) newer_than:2d
  e. from:(skeeled.com OR jobteaser OR welcometothejungle OR mitacs OR iaeste OR euraxess OR indeed OR
     linkedin) newer_than:2d
Search results show only part of a thread: call get_thread (PLAIN_TEXT) on every candidate and read it in
full. Skip anything not about my PFE applications: {{SCHOOL}} circulars, class lists, GitHub, OpenAI,
newsletters naming no specific offer.

3. LABEL
Confirm the id with list_labels, then label_thread "{{GMAIL_LABEL}}" ({{GMAIL_LABEL_ID}}) on every PFE
thread, including threads I only sent to, auto-replies and bounces. A labelled thread with new messages
gets labelled again. Leave your other labels ({{GMAIL_LABEL_TO_LEAVE}}) alone; create no labels.

4. MATCH EACH THREAD
In order: exact supervisor_email or hr_email, then domain, then company name, then project title or
reference number. If two rows share a domain, match on recipient and subject, never guess. No match but a
real PFE exchange with a named organisation: tracker_tools.add_rows with only what the emails show,
everything else UNVERIFIED, note "added from mailbox sweep". Anything still ambiguous (for example an
automatic receipt that fits two rows): UNMATCHED, report it, do not ask me about it and do not count it as
a decision.

5. GROUP EVERY MATCHED INBOUND MESSAGE (one group each)
GROUP 1, NO REPLY: automatic receipts, newsletters, no-reply senders, out-of-office, bounces. Record only
(an auto-reply naming a replacement contact also goes through Referrals in step 6).
GROUP 2, SEND AUTOMATICALLY, only these three and only when unambiguous:
- they ask for a document I have in 03_documents or ..\my documents\ (CV, recommendation
  letter, convention de stage template; changed 18 Oct 2026): reply with it attached. A file from
  ..\my documents\ is outside the session folder, so copy it first into 02_tracker\_upload\<ID>\
  (Chrome file_upload only accepts files under the session folder) and delete 02_tracker\_upload\
  in one command at the end of the run. The connector cannot attach local
  files: build the reply draft in Chrome (open the thread, Reply, file_upload, wait for "Saved"), then
  send_message(draftId);
- they ask me to confirm dates, duration, or that {{SCHOOL}} signs a convention de stage: {{PFE_WINDOW}}, 26 weeks, {{SCHOOL}} signs the convention, I handle the visa with their supporting letter;
- a rejection: two short polite sentences, thanks and a request to be considered for future openings.
Their language, under 100 words, plain sentences, no em dashes, signed {{FULL_NAME}}, in the same
thread (create_draft with replyToMessageId, then send_message). Max 10 per run. Before sending, check the
thread has no reply from me after their message (never send twice) and the row is not held. Save each
sent reply as 04_outbound\<ID>\sent_<date>.md.
GROUP 3, I DECIDE, drafts only: everything else, and anything mixing Group 2 with something else. Always
Group 3: interview invitations or scheduling; offers, acceptances, declines; salary, stipend, contracts;
visa, immigration or legal questions; questions about my experience, results or technical skills;
anything you are unsure how to group. Write 2 or 3 complete replies (same rules as Group 2), save each as a
draft in the thread (create_draft with replyToMessageId). Label them A, B, C only in the report. Send none.
An offer or reply that says the stay is unpaid, or offers a very low allowance (changed 10 Oct 2026):
follow CLAUDE.md UNPAID OR LOW-PAID OFFERS. Look up the pay for that position in that country (or
Europe) and the visa and legal-minimum anchors first; every option negotiates a concrete monthly figure
tied to an external requirement, with alternatives (partial allowance, housing, a grant, a project
contract). No option says I fund myself or declines. List the figures and their sources in the report.
For an interview with a stated date and time, create a Google Calendar event "PFE interview: <company>"
with the link in the description. Never guess a time; an ambiguous time zone means no event, flag it.
When a Group 3 thread opens or a row moves to interview or offer, every other row with that
company_domain is held automatically: list them.

6. RECORD, ONE THREAD AT A TIME
Set the row's status from what actually happened (update_status dated by the email that caused it, not
today):
- I sent an application or request: applied, date_applied = my first sent message.
- Automatic receipt, or a human reply that is not a decision yet (asks for documents, points to another
  position or a portal, says to apply through Mitacs): acknowledged.
- Interview invitation or scheduling: interview, with interview_date if given.
- Offer or acceptance: offer, also when they say the stay is unpaid or low-paid but they would host me.
  Refusal, position filled, no capacity, or no funding that means they cannot host me at all: rejected.
- Bounce: keep the status, note the dead address. Out of office: keep the status, note the return date.
Set date_response, response_type, one plain note line. If the status is already right, update_fields.
Interviews tab: whenever someone asks for or agrees to an interview, fixes or changes a time, or replies
after an interview, call tracker_tools.upsert_interview(id, note, **fields) with what the emails state:
stage (offered = no time yet, scheduled = time fixed, held = took place, closed = outcome known),
interviewer, interview_language (the language the interview is held in, e.g. French or English, only
if the email states or clearly shows it, else UNVERIFIED), interviewer_email, others_attending,
date_offered, interview_date, interview_time (both time zones), time_zone, format, meeting_link, topic, post_interview_response, post_response_date,
outcome (pending, next_round, offer, rejected), next_step. A scheduled interview whose date has passed
with no news: stage held only if I confirmed it, otherwise note it and list it under DECIDE.
Offers tab (changed 8 Oct 2026): every row at status offer, and every host that agreed to take me, has
one offers.csv row. Each run, for each such row with a thread in scope, and for any offer row with no
offers.csv line yet (read its thread with get_thread), call tracker_tools.upsert_offer(id, note,
**fields) with what the emails state: stage (offer_received = nothing answered yet, reply_drafted =
drafts waiting for me, questions_asked = I asked something and wait for them, accepted = I accepted
in writing, convention_in_progress, convention_signed, declined = I said no, withdrawn = they took it
back), others_cc, dates_offered, duration_weeks, date_offered, stipend, visa_support,
convention_status, thread_subject, thread_link (https://mail.google.com/mail/u/0/#all/<threadId>),
my_last_action, my_last_action_date, next_step (one plain line: what happens next and who acts),
deadline_to_reply only if stated. A new row copies country, city, supervisor, supervisor_email and
project from the tracker. Not stated in the emails: UNVERIFIED. My own replies in the thread move the
stage too (a sent question: questions_asked; a sent acceptance: accepted).
Next actions tab (added 22 Oct 2026): right after each thread is recorded, call
tracker_tools.upsert_action(opportunity_id=id, action=..., type=..., due_date=..., priority=...,
source_command="pfe-inbox", note=...) for what it leaves me to do, one plain line each:
- a Group 3 thread: type email, "choose option A/B/C in /pfe-send" with what they asked, due_date =
  deadline_to_reply if stated, priority high for interviews and offers;
- an interview offered or scheduled: type interview, "prepare: run /pfe-interview-prep", due_date =
  interview_date, priority high;
- an offer accepted, or a host asking for the convention de stage: type university, "ask {{SCHOOL}} for the
  convention de stage" (or the signature or paper asked), priority high;
- a visa, residence or proof-of-means question: type visa;
- a document they ask for that I do not have in 03_documents or ..\my documents\: type document;
- Gmail SESSION EXPIRED: type other, "sign in to Gmail in Chrome", no opportunity_id.
When a thread shows an action resolved (my reply sent, interview held, convention signed, offer
declined or withdrawn, row rejected), call upsert_action(action_id, status="done" or "dropped", note=...)
on its open action (tracker_tools.load_actions()).
Referrals (added 31 Oct 2026; CLAUDE.md REFERRALS): right after the thread is recorded, for each person
the message names to contact, with the name and the address stated in it (one row per person):
- Look the address up in tracker.csv and blocked.csv (supervisor_email, hr_email) and in Gmail (in:sent OR
  in:scheduled to:<address>). Already there: no row, one note line on the original row, listed in the report.
- Otherwise tracker_tools.add_rows with status enriched, best_method email, supervisor = the name,
  supervisor_email = the address, contact_confidence verified, project_title "Referral: <name>",
  company_domain from the address, and country, city, company, org_type, field, track and agreement_ok
  copied from the original row when it is the same organisation, else only what the email states and
  UNVERIFIED for the rest. source = "referral: <referrer name>, <original ID>" when a human wrote the
  message and did not refuse to be cited; "referral, no citation: <referrer name>, <original ID>" when
  that person refused; "referral, no citation: auto-reply of <sender>, <original ID>" for an auto-reply
  naming a replacement contact. One note line on the original row with the new ID.
- A redirect to a portal, a job board or a shared address is not a referral: no row, the row stays as
  recorded above.
- A name with no address: no row and no built address. One note line on the original row and
  upsert_action(type="other", action="find the address of <name>, referred by <referrer>").
The message itself is still handled by its group in step 5. The new row follows the HOLDS: while a Group 3
thread or an interview or offer holds its company_domain, the Applier skips it.
One responses.csv line per inbound human or system message (tracker_tools.add_response: date_received,
opportunity_id, company, from_email, type, what_they_want, deadline_to_reply only if stated, handled yes if
a reply was sent in the thread, else NO). Skip it if the same from_email + date_received + opportunity_id
exists. A row in blocked.csv cannot take a responses line: add the fact with unblock_tools.note_block and
report it. Only facts the email states; contradictions with the tracker go in notes and the report, never
overwrite silently. Save after each thread and after each action on a row (CLAUDE.md TRACKER AFTER
EVERY ROW), never at the end.

7. WAITING LIST (added 31 Oct 2026)
After every thread is recorded and before any follow-up, call tracker_tools.refresh_waiting() once and
keep what it returns for the report. It works on 02_tracker\waiting_list.csv, one save per row:
- removes every row with a line in responses.csv or a tracker status other than applied (add_response,
  update_status and block_row already do this at once);
- adds every tracker row at status applied with no line in responses.csv;
- refreshes last_checked and days_waiting (calendar days since date_applied) on every row;
- moves a row from waiting to follow_up when followup_due has passed. The period is the tracker's
  followup_due (12 working days, workdays(date_applied, 12)), no second timer;
- a tracker note "followup sent <date>" makes the row followed_up. It stays on the list until they reply
  or its tracker status changes.
A follow_up row with no contact_email (a portal application, so no thread to reply in) stays on the list
and nothing is sent: the first time, the function adds the note "no address" and one next_actions item.
waiting, follow_up and followed_up exist only in waiting_list.csv: the tracker status stays applied.

8. FOLLOW-UPS, SENT AUTOMATICALLY (cap 15 a run, oldest followup_due first)
Work from tracker_tools.load_waiting(), not tracker.csv: rows with status follow_up and a contact_email,
oldest followup_due first. For each: find the original sent thread (search_threads in:sent
to:<contact_email>), write one short paragraph that references the original application date and adds one
new piece of information rather than just asking again, create_draft with replyToMessageId, then
send_message after these checks: the row is not held (CLAUDE.md HOLDS), no banned word or em dash
(CLAUDE.md WRITING), no reply of mine in the thread since the application (never follow up twice), not
already noted "followup sent".
Note "followup sent <date>" on the row (update_fields), save the body as
04_outbound\<ID>\followup_<date>.md, then at once tracker_tools.upsert_waiting(id, status="followed_up",
followup_sent_on=<date>). A row that fails a check is not sent, stays follow_up and is listed in the report.
Over the cap: the rest stay follow_up for the next run.

9. EXPIRE
update_status(id, "expired", ...) for every row whose deadline has passed and that was never applied to.

10. REPORT 05_reports\inbox_<YYYY-MM-DD>.md
Top, under 20 lines: threads found / labelled / matched / new rows / unmatched; SENT (ID, company, what
they asked, what was sent); DECIDE (ID, company, what they asked, deadline, options A/B/C one line each
with draft ids); WAITING LIST (counts of waiting, follow_up and followed_up after step 8, of which no
address; rows that moved to follow_up: ID, company, method; follow-ups sent: ID, company, date); EXPIRED (ID, company); status changes (ID,
company, old -> new, date); WAITING ON ME (responses.csv handled = NO); REFERRALS (new rows: ID, person, address,
referrer, cited or not, held or not; names with no address; addresses already emailed); UNMATCHED; HELD (new automatic
holds); OFFERS (ID, company, stage, next step, one line each for every offers.csv row not declined or
withdrawn); NEXT ACTIONS (every open next_actions.csv row by due date: ACT id, ID, company, action,
due date; then the ones this run closed); contradictions. Below: a table of every row touched (ID, company, contact, date applied, last
inbound date, status, response_type). If nothing arrived, say so in one line.

Last two lines: RUN_STATS (CLAUDE.md; emails_sent counts Group 2 replies and follow-ups; decisions_waiting
= Group 3 threads waiting) and `SEND_QUEUE: <Group 3 threads now waiting for me>`.
