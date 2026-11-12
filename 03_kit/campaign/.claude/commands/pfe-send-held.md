---
description: Sends the application drafts held back by yesterday's 50/day cap, oldest first, within today's cap and every send check.
---
SEND-HELD RUN. Follow CLAUDE.md (SENDING, HOLDS). Never wait for a reply.

1. Candidates: tracker rows at status queued whose notes say the draft was left DRAFTED because of the
   daily cap ("over the 50/day cap", "over the 25/day cap" or "cap reached"), oldest note date first.
   Never a DRAFT_ONLY draft (Applier draft mode): those wait for /pfe-send (added 28 Oct 2026).
2. Count cold emails today (tracker rows with date_applied = today and email_sent set; emails scheduled
   for today count). Stop when the count reaches 50 (CLAUDE.md SENDING).
3. Send a candidate only if every check passes, else skip it with the reason:
   - not held (holds.csv and the automatic holds);
   - address verified and never emailed (Gmail in:sent OR in:scheduled to:<address>, tracker email_sent);
   - the draft exists (list_drafts query to:<address>) and shows the CV and letter PDFs on ONE
     full-reload read of the Gmail Drafts list in Chrome before the first send (javascript_tool: every
     draft's recipient and attachment names; one working tab), not get_draft (CLAUDE.md SENDING 4).
   Then send_message(draftId). Never create a draft here, never click Send in Chrome.
4. After every send, before the next one (CLAUDE.md TRACKER AFTER EVERY ROW): tracker_tools.update_status(id, "applied", "sent <date> by /pfe-send-held",
   email_sent=<address>, followup_due=unblock_tools.workdays(today, 12)); body saved as
   04_outbound\<ID>\sent_<date>.md.
5. Report 05_reports\<YYYY-MM-DD>_send_held.md: sent, skipped with reason, HELD, cap used today.

Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: <cap-held drafts still waiting>`.
