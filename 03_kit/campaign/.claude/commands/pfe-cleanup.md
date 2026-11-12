---
description: CLEANUP run, monthly (last day of the month, after the Applier)
---
CLEANUP RUN. Follow CLAUDE.md. Every write goes through tracker_tools (it backs up first).

1. tracker_tools.archive_rows(ids=[id]), one row at a time (CLAUDE.md TRACKER AFTER EVERY ROW): every row at screened_out or expired, and every rejected or no_response
   row whose latest date is over 90 days old, gets its (company_domain, project_title) key in
   02_tracker\seen.csv, its full row in screened_out.csv, and leaves tracker.csv. Rows at acknowledged,
   interview or offer are never moved. Right after each row moves, its open next actions
   (tracker_tools.load_actions) are set dropped: upsert_action(action_id, status="dropped",
   note="row archived").
2. Confirm add_rows() still checks seen.csv as well as tracker.csv: add one dummy row whose key is in
   seen.csv and check it is skipped (nothing is written when it is skipped).
3. Delete leftover 02_tracker\.tracker_*.tmp, .seen_*.tmp and LibreOffice lu*.tmp files older than a day
   (list them if deletion is refused).
4. 02_tracker\backups\ keeps every tracker backup. If it holds more than 3000 files, zip everything older
   than 30 days into backups\archive_<YYYY-MM>.zip and delete the zipped files.
5. List anything in ..\archive\junk\ (parked leftovers, changed 18 Oct 2026) older than 30 days; delete
   nothing there unless I said so.

Write 05_reports\<YYYY-MM-DD>_runNN_cleanup.md: rows moved by status, rows remaining, seen.csv size, the
dedup check result, files deleted.
Last two lines: RUN_STATS (CLAUDE.md) and `SEND_QUEUE: 0`.
