---
description: CHECKER run, as many rows as {{FIRST_NAME}} chooses (no limit) - bounced addresses, probable contacts, then discovered rows
argument-hint: "[number of rows or ALL]"
---
CHECKER RUN. Arguments: $ARGUMENTS
Follow CLAUDE.md. This run verifies and scores. It does not hunt, apply, or touch Gmail.

HOW MANY ROWS (CLAUDE.md RUN SIZE, no hard limit)
If the arguments hold a number or ALL, use it. Otherwise, before selecting any target rows, count the
eligible rows and ask {{FIRST_NAME}} via AskUserQuestion: "How many rows should this Checker run cover?
(<n> eligible)" with choices 10, 25, 50 and ALL; he can type any number. Do not proceed until answered.

TARGET, the number of rows chosen (ALL = every eligible row), in this order:
1. Rows whose email bounced (responses.csv type bounce, or "bounce" in notes with no newer verified
   address): they need a new verified address.
2. Enriched rows with contact_confidence probable or UNVERIFIED.
3. Discovered rows with the highest apparent fit to 00_profile\TRACKS.md, company and startup rows
   before academic rows of similar fit (CLAUDE.md SEARCH SCOPE, changed 20 Oct 2026); academic rows are
   still checked, never skipped.
Skip held rows and {{EXCLUDED_ORGS}}. Research with subagents, 5 rows each. Only the main session writes
the tracker, and it saves each row as soon as its subagent returns (a run cut short keeps everything saved).

FOR EACH ROW
1. Open the organisation's own site. Confirm the opportunity still exists and the deadline is real. Gone
   or deadline passed: update_status(id, "expired", ...) and move on.
2. Find the right human, in this order: named internship coordinator, named team or department lead,
   named supervisor for the project, HR recruitment address, general careers address.
   contact_confidence = verified (address seen on their own site or an official directory page),
   probable (person listed, address not: record the name, email UNVERIFIED), or generic. Never
   construct an address from a naming pattern.
3. Viability: will they take a non-EU student needing a visa, and will they sign a third-party
   internship agreement? Site silent: UNKNOWN, never assume. A "no" to either: screened_out with the
   reason. {{SCHOOL}} register hosts: agreement_ok = YES.
4. Score out of 100 (CLAUDE.md SCORING), selection_probability as a plain honest percentage, priority
   A/B/C (CLAUDE.md).
5. One line in notes: the single strongest argument for why they should take me, referencing something
   specific about them.
6. best_method (web form or email) and application_url; status enriched (update_status) or, for rows
   already enriched, update_fields with a note.
Save each row through tracker_tools as soon as it is done (CLAUDE.md TRACKER AFTER EVERY ROW).

REPORT 05_reports\<YYYY-MM-DD>_runNN_checker.md: rows covered out of the number chosen, eligible rows
still remaining; the A list with one line each; every row where the fit
is strong but something non-technical blocks it; bounced rows fixed or still without an address.

Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: 0`.
