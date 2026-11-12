---
description: Interactive only. Group 3 decisions and anything held back by the checks. Sends only what {{FIRST_NAME}} approves.
---
SEND RUN. Follow CLAUDE.md. Interactive only. Applications, follow-ups and Inbox
Group 2 replies are sent automatically by their own commands; this run covers only what those runs left
for me.

1. BUILD THE QUEUE
list_drafts (all pages), match each draft to a tracker or blocked row by recipient, domain and thread.
Keep only:
   D. DECISIONS: Group 3 A/B/C drafts from the latest inbox reports (interview, offer, salary, contract,
      visa or legal replies, questions about my experience).
   H. HELD BACK: application or follow-up drafts a run left DRAFTED because a check failed (hold,
      address already emailed, attachments missing, swap test), with the reason from its report,
      and the DRAFT_ONLY drafts of an Applier run in draft mode (notes "held: DRAFT_ONLY"; added 28 Oct
      2026), oldest first. A DRAFT_ONLY draft is sent only when I name it, after every SENDING check.
Report without touching them: drafts that match nothing, duplicates with no attachments. Never touch
emails in Gmail's Scheduled folder.
2. Count cold emails today (tracker rows with date_applied = today and email_sent set). Section H
   applications respect the 50/day cap; D does not count.
3. Show one table per section: #, ID, company, to, subject, opening sentence, attachments, and for H the
   reason it was held. For D, each option in one line.
4. STOP AND WAIT. I answer "D: PFE-0042 option B", "send H 2", "send H 1-20", "send H all", "release PFE-0393",
   "rewrite 5: ..." or "skip". Silence, a question or anything ambiguous is not approval.
5. Send exactly what I approved with send_message(draftId). For D, send the chosen option and delete the
   unused option drafts (delete_draft). If I asked for an edit: update_draft, show the new version, wait
   again. If I release a hold, remove that line from holds.csv. A rewrite about pay follows CLAUDE.md
   UNPAID OR LOW-PAID OFFERS (look up the figures first, never offer to fund myself, never decline).
6. After every send, at once: application → status applied, date_applied today, email_sent, followup_due
   12 working days out, note "sent <date>"; follow-up → note "followup sent <date>" and
   tracker_tools.upsert_waiting(id, status="followed_up", followup_sent_on=<date>); decision →
   responses.csv handled=yes and the row note (interview accepted: interview_date if fixed); a reply
   about an offer also updates offers.csv (tracker_tools.upsert_offer: stage, my_last_action,
   my_last_action_date, next_step); the row's open next action (tracker_tools.load_actions) is set done
   with tracker_tools.upsert_action(action_id, status="done", note=...), and a sent acceptance adds a
   type university action "ask {{SCHOOL}} for the convention de stage", priority high. Save each
   sent body as 04_outbound\<ID>\sent_<date>.md.
7. Report: sent per section, left as drafts, cap used today.

Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: <drafts still waiting for me>`.
