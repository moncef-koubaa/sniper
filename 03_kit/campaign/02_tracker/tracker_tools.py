"""
tracker_tools.py - the only way to write the PFE 2027 tracker.

tracker.csv is the only source of truth for opportunities.
responses.csv is the only source of truth for replies.
Every write copies the current file into backups/ first (timestamped), then
replaces the file atomically.

Use from Python with this folder as the working directory or on sys.path:

    import tracker_tools as tt
    rows = tt.load()
    added, skipped = tt.add_rows([{"company": ..., "company_domain": ...,
                                   "project_title": ..., "source": ...}])
    tt.update_status("PFE-0007", "applied", "sent via portal",
                     cv_version="CV_PFE-0007_v1")
    tt.archive_rows()
    tt.export_xlsx()

Dead leads leave tracker.csv. archive_rows() deletes them from it and records
their dedup key (company_domain, project_title) in seen.csv, so a lead screened
out once is never rediscovered and re-screened. add_rows() checks tracker.csv
and seen.csv before adding anything. The full rows are also kept in
screened_out.csv, which nothing reads: it is a recovery copy, not the index.

next_actions.csv (the "next_actions" tab, first in tracker.xlsx) lists what I
must do myself; upsert_action() creates, updates and closes its rows.

waiting_list.csv (the "waiting_list" tab) lists applied rows with no reply yet;
refresh_waiting() keeps it in step and drives the /pfe-inbox follow-ups.

Command line:
    python tracker_tools.py summary
    python tracker_tools.py archive
    python tracker_tools.py export
"""
from __future__ import annotations

import csv
import datetime as _dt
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACKER = HERE / "tracker.csv"
RESPONSES = HERE / "responses.csv"
BACKUP_DIR = HERE / "backups"
ID_COUNTER = HERE / "id_counter.txt"   # highest ID ever issued, so IDs are never reused
XLSX = HERE / "tracker.xlsx"
SEEN = HERE / "seen.csv"              # dedup index of dead leads: two columns, read by add_rows()
ARCHIVE = HERE / "screened_out.csv"   # full rows of the same leads, recovery copy, read by nothing

HEADER = [
    "id", "date_discovered", "status", "priority", "match_score",
    "selection_probability", "country", "city", "company", "company_domain",
    "org_type", "department", "project_title", "project_type", "field", "track",
    "duration_weeks", "start_date", "deadline", "stipend", "visa_support",
    "agreement_ok", "supervisor", "supervisor_email", "hr_contact", "hr_email",
    "contact_confidence", "best_method", "application_url", "source",
    "date_applied", "cv_version", "letter_version", "email_sent",
    "date_response", "response_type", "interview_date", "followup_due",
    "outcome", "notes",
]

SEEN_HEADER = ["company_domain", "project_title"]

RESPONSES_HEADER = [
    "date_received", "opportunity_id", "company", "from_email", "type",
    "what_they_want", "deadline_to_reply", "handled",
]

# One row per opportunity that asked for or agreed to an interview.
INTERVIEWS = HERE / "interviews.csv"
INTERVIEWS_HEADER = [
    "opportunity_id", "company", "stage", "interview_date", "interview_time",
    "interviewer", "interview_language", "interviewer_email", "others_attending", "date_offered",
    "time_zone", "format", "meeting_link", "topic", "prep_file",
    "post_interview_response", "post_response_date", "outcome", "next_step", "notes",
]
# Columns added after files existed: an older file without them still loads
# (empty values) and gets them on its next write.
ADDED_COLUMNS = {"interview_language"}  # added 7 Oct 2026
INTERVIEW_STAGES = ("offered", "scheduled", "held", "closed")
# offered = they asked/agreed, no time yet; scheduled = time fixed; held = done,
# waiting for their answer; closed = outcome known (outcome column says which).

# One row per opportunity offered to me (tracker status offer, or a host that
# agreed to take me). Added 8 Oct 2026.
OFFERS = HERE / "offers.csv"
OFFERS_HEADER = [
    "opportunity_id", "company", "stage", "country", "city", "supervisor", "supervisor_email",
    "others_cc", "project", "dates_offered", "duration_weeks", "date_offered", "stipend",
    "visa_support", "convention_status", "thread_subject", "thread_link", "my_last_action",
    "my_last_action_date", "next_step", "deadline_to_reply", "notes",
]
OFFER_STAGES = ("offer_received", "reply_drafted", "questions_asked", "accepted",
                "convention_in_progress", "convention_signed", "declined", "withdrawn")
# offer_received = nothing answered yet; reply_drafted = drafts waiting for me;
# questions_asked = I asked (visa, stipend, dates...) and wait for them;
# accepted = I accepted in writing; convention_* = the school's agreement after
# acceptance; declined = I said no; withdrawn = they took the offer back.

# One row per thing I must do myself: send or choose an email, prepare a
# document, ask the school, prepare an interview, a visa step. Added 22 Oct 2026.
ACTIONS = HERE / "next_actions.csv"
ACTIONS_HEADER = [
    "action_id", "opportunity_id", "company", "action", "type", "due_date", "priority",
    "status", "source_command", "created_on", "done_on", "notes",
]
ACTION_TYPES = ("email", "document", "university", "interview", "visa", "application", "other")
ACTION_STATUSES = ("open", "done", "dropped")
ACTION_PRIORITIES = ("high", "normal", "low")

# One row per tracker row at applied with no line in responses.csv. Added 31 Oct 2026.
WAITING = HERE / "waiting_list.csv"
WAITING_HEADER = [
    "opportunity_id", "company", "contact_email", "method", "date_applied", "followup_due",
    "days_waiting", "status", "followup_sent_on", "last_checked", "notes",
]
WAITING_STATUSES = ("waiting", "follow_up", "followed_up")   # never in tracker.csv: it stays applied
# waiting = followup_due not passed; follow_up = due, not sent yet; followed_up = sent, stays until
# they reply or the tracker status changes.
NO_ADDRESS_ACTION = "follow up by hand, no email address:"

STATUSES = (
    "discovered", "screened_out", "enriched", "queued", "applied",
    "acknowledged", "interview", "offer", "rejected", "expired", "no_response", "blocked",
)

# Date column stamped with today's date when a row enters a status.
# The header has no column of its own for screened_out, enriched, queued,
# expired or no_response: for those the dated line in notes is the record.
# date_response holds the date of the most recent reply; earlier replies stay
# in notes. interview_date is the scheduled interview, set explicitly.
STATUS_DATE_COLUMN = {
    "discovered": "date_discovered",
    "applied": "date_applied",
    "acknowledged": "date_response",
    "interview": "date_response",
    "offer": "date_response",
    "rejected": "date_response",
}

# archive_rows() policy
ARCHIVE_STATUSES = ("screened_out", "expired", "blocked")        # moved whatever their age
AGE_ARCHIVE_STATUSES = ("rejected", "no_response")    # moved once cold
KEEP_STATUSES = ("acknowledged", "interview", "offer")  # never moved, whatever their age
ARCHIVE_AGE_DAYS = 90
DATE_COLUMNS = ("date_discovered", "date_applied", "date_response",
                "interview_date", "followup_due")     # email_sent holds an address, not a date

ID_PREFIX = "PFE-"
NOTE_SEP = " | "          # notes stay on one physical line: "date text | date text"
UNVERIFIED = "UNVERIFIED"
PROTECTED = {"id", "status", "notes"}   # changed only through the functions below


# ----------------------------------------------------------------- helpers

def today() -> str:
    return _dt.date.today().isoformat()


def _clean(value) -> str:
    if value is None:
        return ""
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def _read(path: Path, header: list) -> list:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        got = reader.fieldnames or []
        if got != header and got != [h for h in header if h not in ADDED_COLUMNS]:
            raise ValueError(
                f"{path.name} header does not match the contract.\n"
                f"  missing: {[c for c in header if c not in got]}\n"
                f"  unexpected: {[c for c in got if c not in header]}"
            )
        return [{h: (row.get(h) or "") for h in header} for row in reader]


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    dest = BACKUP_DIR / f"{path.stem}_{stamp}{path.suffix}"
    shutil.copy2(path, dest)
    return dest


def _write(path: Path, header: list, rows: list) -> Path | None:
    """Back up, then write to a temp file in the same folder and swap it in."""
    backup = _backup(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.stem}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=header, lineterminator="\n",
                                    extrasaction="raise")
            writer.writeheader()
            writer.writerows(rows)
        for attempt in range(20):          # OneDrive can hold a lock for a few seconds
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if attempt == 19:
                    raise
                import time; time.sleep(1.5)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    return backup


def _check_fields(fields: dict, header: list, protected=()) -> None:
    unknown = [k for k in fields if k not in header]
    if unknown:
        raise ValueError(f"unknown column(s): {unknown}")
    blocked = [k for k in fields if k in protected]
    if blocked:
        raise ValueError(f"column(s) {blocked} cannot be set here")


def _check_status(status: str) -> None:
    if status not in STATUSES:
        raise ValueError(f"status '{status}' not in vocabulary {STATUSES}")


def _append_note(existing: str, text: str, date: str) -> str:
    entry = f"{date} {_clean(text)}"
    return f"{existing}{NOTE_SEP}{entry}" if existing else entry


def norm_domain(value: str) -> str:
    """'https://www.Arkema.com/fr/' -> 'arkema.com'. Empty or UNVERIFIED -> ''."""
    v = _clean(value).lower()
    if not v or v == UNVERIFIED.lower():
        return ""
    v = re.sub(r"^[a-z]+://", "", v)
    v = v.split("/")[0].split("?")[0].split("#")[0].split(":")[0]
    v = v.removeprefix("www.").rstrip(".")
    return v


def norm_text(value: str) -> str:
    v = unicodedata.normalize("NFKC", _clean(value)).casefold()
    v = re.sub(r"[^\w]+", " ", v)
    return " ".join(v.split())


def dedup_key(row: dict) -> tuple:
    """(company_domain, project_title), both normalised.

    If company_domain is empty or UNVERIFIED the company name stands in for it,
    so two unrelated organisations without a domain do not collide on a
    generic title.
    """
    title = norm_text(row.get("project_title", ""))
    if not title:
        raise ValueError("project_title is required for deduplication")
    org = norm_domain(row.get("company_domain", ""))
    if not org:
        name = norm_text(row.get("company", ""))
        if not name:
            raise ValueError("company_domain or company is required for deduplication")
        org = "name:" + name
    return (org, title)


def _id_number(opp_id: str) -> int | None:
    m = re.fullmatch(rf"{re.escape(ID_PREFIX)}(\d+)", opp_id or "")
    return int(m.group(1)) if m else None


def _read_counter() -> int:
    try:
        return int(ID_COUNTER.read_text(encoding="utf-8").strip() or 0)
    except FileNotFoundError:
        return 0


def _write_counter(value: int) -> None:
    ID_COUNTER.write_text(f"{value}\n", encoding="utf-8")


def _find(rows: list, opp_id: str) -> dict:
    for row in rows:
        if row["id"] == opp_id:
            return row
    if any(r["id"] == opp_id for r in load_archive()):
        raise KeyError(f"{opp_id} was archived to {ARCHIVE.name}; it is not in tracker.csv")
    raise KeyError(f"{opp_id} not in tracker")


def _store_domain(row: dict) -> None:
    """Keep company_domain as a bare domain; UNVERIFIED stays literal."""
    v = row.get("company_domain", "")
    if v and v.upper() != UNVERIFIED:
        row["company_domain"] = norm_domain(v)


def _check_no_collision(rows: list, row: dict) -> None:
    key = dedup_key(row)
    for other in rows:
        if other is not row and dedup_key(other) == key:
            raise ValueError(f"{row['id']} would duplicate {other['id']} on {key}")
    for other in load_seen():
        if seen_key(other) == key:
            raise ValueError(f"{row['id']} would duplicate a lead already in {SEEN.name} on {key}")


# ----------------------------------------------------------------- public API

def load() -> list:
    """All tracker rows as a list of dicts (every value a string)."""
    return _read(TRACKER, HEADER)


def load_responses() -> list:
    return _read(RESPONSES, RESPONSES_HEADER)


def load_archive() -> list:
    """Rows moved out of tracker.csv by archive_rows(). [] if the file is absent."""
    if not ARCHIVE.exists():
        return []
    return _read(ARCHIVE, HEADER)


def load_seen() -> list:
    """Dead-lead dedup keys. [] if seen.csv does not exist yet."""
    if not SEEN.exists():
        return []
    return _read(SEEN, SEEN_HEADER)


def seen_key(row: dict) -> tuple:
    """Key of one seen.csv row, in the same shape as dedup_key()."""
    org = _clean(row.get("company_domain", ""))
    title = norm_text(row.get("project_title", ""))
    if not org or not title:
        raise ValueError(f"seen.csv row is missing a value: {row}")
    return (org, title)


def _seen_entry(row: dict) -> dict:
    """Tracker row -> seen.csv row. company_domain holds the org half of
    dedup_key(): the bare domain, or 'name:<company>' when the row has no
    usable domain, so the key matches exactly either way."""
    org, _ = dedup_key(row)
    return {"company_domain": org, "project_title": _clean(row.get("project_title", ""))}


def add_seen(rows: list) -> int:
    """Append dedup keys to seen.csv, skipping keys already there. Backed up first."""
    current = load_seen()
    have = {seen_key(r) for r in current}
    fresh = []
    for row in rows:
        entry = _seen_entry(row)
        key = seen_key(entry)
        if key in have:
            continue
        have.add(key)
        fresh.append(entry)
    if fresh:
        _write(SEEN, SEEN_HEADER, current + fresh)
    return len(fresh)


def parse_date(value) -> _dt.date | None:
    """'2026-09-20' or '20/09/2026' -> date. Anything unparseable -> None."""
    v = _clean(value)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return _dt.datetime.strptime(v, fmt).date()
        except ValueError:
            continue
    return None


def last_date(row: dict) -> _dt.date | None:
    """Most recent parseable date across DATE_COLUMNS, or None if the row has none."""
    found = [d for d in (parse_date(row.get(c, "")) for c in DATE_COLUMNS) if d]
    return max(found) if found else None


def next_id(rows: list | None = None) -> str:
    """Next sequential ID. Never reuses an ID, including archived and removed ones."""
    rows = (load() + load_archive()) if rows is None else rows
    highest = max((n for n in (_id_number(r["id"]) for r in rows) if n is not None),
                  default=0)
    return f"{ID_PREFIX}{max(highest, _read_counter()) + 1:04d}"


def add_rows(new_rows: list, date: str | None = None) -> tuple:
    """Add opportunities. Returns (added_ids, skipped).

    - IDs, date_discovered and the first notes line are filled here.
    - status defaults to 'discovered'; a row can be added directly as
      'screened_out', with the reason in its notes.
    - A row whose (company_domain, project_title) matches a row in tracker.csv,
      a key in seen.csv, or an earlier row in the same batch, is skipped, not
      added. Both files are checked so that a lead screened out once is never
      rediscovered and re-screened. skipped is a list of (company,
      project_title, reason), the reason naming which file matched.
    - The whole batch is validated before anything is written.
    """
    date = date or today()
    rows = load()
    seen = {seen_key(r): ("a lead already screened out", SEEN.name) for r in load_seen()}
    seen.update({dedup_key(r): (r["id"], TRACKER.name) for r in rows})
    counter = max(_read_counter(),
                  max((n for n in (_id_number(r["id"]) for r in rows + load_archive())
                       if n), default=0))
    added, skipped, staged = [], [], []

    for new in new_rows:
        _check_fields(new, HEADER)
        if _clean(new.get("id")):
            raise ValueError("do not pass 'id'; add_rows assigns it")
        status = _clean(new.get("status")) or "discovered"
        _check_status(status)
        key = dedup_key(new)
        if key in seen:
            dup_id, where = seen[key]
            skipped.append((_clean(new.get("company")), _clean(new.get("project_title")),
                            f"duplicate of {dup_id} in {where}"))
            continue
        row = {h: "" for h in HEADER}
        row.update({k: _clean(v) for k, v in new.items()})
        _store_domain(row)
        counter += 1
        row["id"] = f"{ID_PREFIX}{counter:04d}"
        row["status"] = status
        row["date_discovered"] = row["date_discovered"] or date
        col = STATUS_DATE_COLUMN.get(status)
        if col and not row[col]:
            row[col] = date
        caller_note = row["notes"]
        row["notes"] = _append_note("", f"added as {status}"
                                    + (f": {caller_note}" if caller_note else ""), date)
        seen[key] = (row["id"], TRACKER.name)
        staged.append(row)
        added.append(row["id"])

    if staged:
        _write(TRACKER, HEADER, rows + staged)
        _write_counter(counter)
    return added, skipped


def archive_rows(ids: list | None = None, age_days: int = ARCHIVE_AGE_DAYS,
                 date: str | None = None) -> dict:
    """Delete dead rows from tracker.csv, keeping their dedup key in seen.csv.

    Each moved row's (company_domain, project_title) goes to seen.csv, its full
    row to screened_out.csv as a recovery copy, and the row leaves tracker.csv.
    Moved by default:
      - every row at screened_out or expired, whatever its age;
      - every row at rejected or no_response whose most recent date column is
        more than `age_days` days old.
    Rows at acknowledged, interview or offer are never moved, whatever their
    age. Pass `ids` to move exactly those rows instead of applying the policy.

    Each moved row gets one dated line in notes. seen.csv and screened_out.csv
    are written before tracker.csv, so an interrupted run leaves a duplicated
    key rather than a lost lead, and re-running skips what is already recorded.
    Every file is backed up first. Returns a summary dict.
    """
    date = date or today()
    cutoff = (parse_date(date) or _dt.date.today()) - _dt.timedelta(days=age_days)
    rows = load()
    archive = load_archive()
    move, reasons = [], {}

    if ids is not None:
        wanted = set(ids)
        move = [r for r in rows if r["id"] in wanted]
        missing = wanted - {r["id"] for r in move}
        if missing:
            raise KeyError(f"not in tracker: {sorted(missing)}")
        live = [r["id"] for r in move if r["status"] in KEEP_STATUSES]
        if live:
            raise ValueError(f"live rows cannot be archived: {live}")
        reasons = {r["id"]: f"archived to {ARCHIVE.name}: status {r['status']}"
                   for r in move}
    else:
        for row in rows:
            status = row["status"]
            if status in KEEP_STATUSES:
                continue
            if status in ARCHIVE_STATUSES:
                move.append(row)
                reasons[row["id"]] = f"archived to {ARCHIVE.name}: status {status}"
            elif status in AGE_ARCHIVE_STATUSES:
                seen = last_date(row)
                if seen and seen < cutoff:
                    move.append(row)
                    reasons[row["id"]] = (
                        f"archived to {ARCHIVE.name}: status {status}, last date "
                        f"{seen.isoformat()}, over {age_days} days old")

    by_status = {}
    for row in move:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
    result = {"moved": sorted(r["id"] for r in move), "by_status": by_status,
              "remaining": len(rows) - len(move), "seen_added": 0,
              "seen_total": len(load_seen()), "archive_total": len(archive)}
    if not move:
        return result

    already = {r["id"] for r in archive}
    for row in move:
        row["notes"] = _append_note(row["notes"], reasons[row["id"]], date)
    result["seen_added"] = add_seen(move)         # dedup key first: never lose the memory
    new_archive = archive + [r for r in move if r["id"] not in already]
    _write(ARCHIVE, HEADER, new_archive)          # then the recovery copy
    moved_ids = {r["id"] for r in move}
    _write(TRACKER, HEADER, [r for r in rows if r["id"] not in moved_ids])
    result["seen_total"] = len(load_seen())
    result["archive_total"] = len(new_archive)
    return result


def update_status(opp_id: str, new_status: str, note: str,
                  date: str | None = None, **fields) -> dict:
    """Move one row to a new status.

    Stamps today's date into the matching date column (STATUS_DATE_COLUMN),
    appends one dated line to notes, and optionally sets other columns in the
    same write, e.g. update_status(id, "interview", "invited by email",
    interview_date="2027-01-12", response_type="interview").
    """
    _check_status(new_status)
    if not _clean(note):
        raise ValueError("a note is required for every status change")
    _check_fields(fields, HEADER, PROTECTED)
    date = date or today()
    rows = load()
    row = _find(rows, opp_id)
    old = row["status"]
    if old == new_status:
        raise ValueError(f"{opp_id} is already '{old}'; use update_fields() for other edits")
    row["status"] = new_status
    col = STATUS_DATE_COLUMN.get(new_status)
    if col:
        row[col] = date
    row.update({k: _clean(v) for k, v in fields.items()})
    _store_domain(row)
    row["notes"] = _append_note(row["notes"], f"{old} -> {new_status}: {note}", date)
    _check_no_collision(rows, row)
    _write(TRACKER, HEADER, rows)
    if new_status != "applied":
        remove_waiting(opp_id, date)
    return dict(row)


def update_fields(opp_id: str, note: str | None = None,
                  date: str | None = None, **fields) -> dict:
    """Set columns on one row without changing its status (e.g. enrichment)."""
    _check_fields(fields, HEADER, PROTECTED)
    if not fields and not note:
        raise ValueError("nothing to update")
    date = date or today()
    rows = load()
    row = _find(rows, opp_id)
    row.update({k: _clean(v) for k, v in fields.items()})
    _store_domain(row)
    if note:
        row["notes"] = _append_note(row["notes"], note, date)
    _check_no_collision(rows, row)
    _write(TRACKER, HEADER, rows)
    return dict(row)


def add_response(**fields) -> dict:
    """Append one reply to responses.csv (backed up first)."""
    _check_fields(fields, RESPONSES_HEADER)
    rows = load_responses()
    row = {h: "" for h in RESPONSES_HEADER}
    row.update({k: _clean(v) for k, v in fields.items()})
    row["date_received"] = row["date_received"] or today()
    row["handled"] = row["handled"] or "no"
    if row["opportunity_id"]:
        _find(load(), row["opportunity_id"])
    _write(RESPONSES, RESPONSES_HEADER, rows + [row])
    if row["opportunity_id"]:
        remove_waiting(row["opportunity_id"])
    return row


def load_interviews() -> list:
    if not INTERVIEWS.exists():
        return []
    return _read(INTERVIEWS, INTERVIEWS_HEADER)


def upsert_interview(opp_id: str, note: str | None = None,
                     date: str | None = None, **fields) -> dict:
    """Create or update the interviews.csv row for one opportunity.

    Call it when someone asks for or agrees to an interview (stage "offered"),
    when a time is fixed ("scheduled"), after it happens ("held"), and when
    they answer afterwards (post_interview_response, post_response_date,
    outcome, stage "closed"). Notes are appended, never overwritten.
    """
    return _upsert(INTERVIEWS, INTERVIEWS_HEADER, INTERVIEW_STAGES, "offered",
                   opp_id, note, date, fields)


def load_offers() -> list:
    if not OFFERS.exists():
        return []
    return _read(OFFERS, OFFERS_HEADER)


def upsert_offer(opp_id: str, note: str | None = None,
                 date: str | None = None, **fields) -> dict:
    """Create or update the offers.csv row for one opportunity.

    Call it when a host offers or agrees to take me (stage "offer_received"),
    and at every later step: drafts written, questions asked, acceptance,
    convention, decline. A new row copies country, city, supervisor,
    supervisor_email and project from the tracker; fields given override.
    Notes are appended, never overwritten.
    """
    opp = _find(load(), opp_id)
    if not any(r["opportunity_id"] == opp_id for r in load_offers()):
        seed = {"country": opp["country"], "city": opp["city"], "supervisor": opp["supervisor"],
                "supervisor_email": opp["supervisor_email"], "project": opp["project_title"]}
        fields = {**seed, **fields}
    return _upsert(OFFERS, OFFERS_HEADER, OFFER_STAGES, "offer_received",
                   opp_id, note, date, fields)


def _upsert(path, header, stages, first_stage, opp_id, note, date, fields) -> dict:
    _check_fields(fields, header, {"opportunity_id", "notes"})
    if "stage" in fields and fields["stage"] not in stages:
        raise ValueError(f"stage must be one of {stages}")
    opp = _find(load(), opp_id)
    rows = _read(path, header) if path.exists() else []
    row = next((r for r in rows if r["opportunity_id"] == opp_id), None)
    if row is None:
        row = {h: "" for h in header}
        row.update(opportunity_id=opp_id, company=opp["company"], stage=first_stage)
        rows.append(row)
    row.update({k: _clean(v) for k, v in fields.items()})
    if note:
        row["notes"] = _append_note(row["notes"], note, date or today())
    _write(path, header, rows)
    return dict(row)


def load_actions() -> list:
    if not ACTIONS.exists():
        return []
    return _read(ACTIONS, ACTIONS_HEADER)


def upsert_action(action_id: str | None = None, note: str | None = None,
                  date: str | None = None, **fields) -> dict:
    """Create or update one next_actions.csv row (something I must do myself).

    With action_id, that row is updated. Without it, an open row with the same
    opportunity_id and type (or, with no opportunity_id, the same action text)
    is updated; otherwise a new row is made (action and type required, status
    open, priority normal, company copied from tracker.csv or blocked.csv).
    Status done or dropped stamps done_on. Notes are appended, never overwritten.
    """
    _check_fields(fields, ACTIONS_HEADER, {"action_id", "notes", "created_on"})
    for col, allowed in (("type", ACTION_TYPES), ("status", ACTION_STATUSES),
                         ("priority", ACTION_PRIORITIES)):
        if col in fields and fields[col] not in allowed:
            raise ValueError(f"{col} must be one of {allowed}")
    date = date or today()
    rows = load_actions()
    if action_id:
        row = next((r for r in rows if r["action_id"] == action_id), None)
        if row is None:
            raise KeyError(f"{action_id} not in {ACTIONS.name}")
    else:
        opp = _clean(fields.get("opportunity_id"))
        row = next((r for r in rows if r["status"] == "open" and (
            (opp and r["opportunity_id"] == opp and r["type"] == fields.get("type"))
            or (not opp and not r["opportunity_id"]
                and r["action"] == _clean(fields.get("action"))))), None)
    if row is None:
        if not fields.get("action") or not fields.get("type"):
            raise ValueError("a new action needs action and type")
        nums = [int(r["action_id"][4:]) for r in rows if r["action_id"][4:].isdigit()]
        row = {h: "" for h in ACTIONS_HEADER}
        row.update(action_id=f"ACT-{max(nums, default=0) + 1:04d}", status="open",
                   priority="normal", created_on=date)
        opp = _clean(fields.get("opportunity_id"))
        if opp and not fields.get("company"):
            blocked_csv = HERE / "blocked.csv"
            pool = load() + (_read(blocked_csv, HEADER) if blocked_csv.exists() else [])
            row["company"] = next((r["company"] for r in pool if r["id"] == opp), "")
        rows.append(row)
    row.update({k: _clean(v) for k, v in fields.items()})
    if fields.get("status") in ("done", "dropped") and not fields.get("done_on"):
        row["done_on"] = date
    if note:
        row["notes"] = _append_note(row["notes"], note, date)
    _write(ACTIONS, ACTIONS_HEADER, rows)
    return dict(row)


def load_waiting() -> list:
    if not WAITING.exists():
        return []
    return _read(WAITING, WAITING_HEADER)


def _waiting_contact(r: dict) -> tuple:
    """(method, address) from what was really sent. email_sent holds an address, YES, NO or
    nothing. A portal row with only a generic hr_email has no thread to reply in, so no address."""
    find = lambda v: "; ".join(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", v))
    sent = r["email_sent"].strip().upper()
    if "@" in sent:
        return "email", find(r["email_sent"])
    if sent == "NO" or (sent != "YES" and _apply_via(r) != "email"):
        return "portal", ""
    address = find(r["supervisor_email"] + "; " + r["hr_email"])
    return ("email", address) if address else ("portal", "")


def _waiting_fields(r: dict, date: str) -> dict:
    """waiting_list columns read from one tracker row. The timer is the tracker's followup_due;
    a row left without one (a mailbox-found application) gets the same workdays(date_applied, 12)."""
    from unblock_tools import workdays
    applied = parse_date(r["date_applied"])
    method, address = _waiting_contact(r)
    return {"company": r["company"], "contact_email": address, "method": method,
            "date_applied": r["date_applied"],
            "followup_due": r["followup_due"] or (workdays(applied, 12) if applied else ""),
            "days_waiting": (parse_date(date) - applied).days if applied else "",
            "last_checked": date}


def _waiting_status(old: str, due: str, date: str, sent: bool) -> str:
    """Next status of one row. followed_up never goes back; due must have passed, not just arrived."""
    if sent or old == "followed_up":
        return "followed_up"
    d = parse_date(due)
    return "follow_up" if old == "follow_up" or (d and d < parse_date(date)) else "waiting"


def upsert_waiting(opp_id: str, note: str | None = None, date: str | None = None,
                   **fields) -> dict:
    """Create or update one waiting_list.csv row, one write per row.

    A new row must be an applied tracker row; it is filled from tracker.csv at status waiting.
    Status followed_up stamps followup_sent_on. Notes are appended, never overwritten.
    Nothing is written when nothing changes, so a second run on the same day adds no backups.
    """
    _check_fields(fields, WAITING_HEADER, {"opportunity_id", "notes"})
    if "status" in fields and fields["status"] not in WAITING_STATUSES:
        raise ValueError(f"status must be one of {WAITING_STATUSES}")
    date = date or today()
    rows = load_waiting()
    row = next((r for r in rows if r["opportunity_id"] == opp_id), None)
    fresh = row is None
    if fresh:
        opp = _find(load(), opp_id)
        if opp["status"] != "applied":
            raise ValueError(f"{opp_id} is '{opp['status']}', only applied rows wait")
        row = {h: "" for h in WAITING_HEADER}
        row.update(opportunity_id=opp_id, status="waiting")
        row.update({k: _clean(v) for k, v in _waiting_fields(opp, date).items()})
        rows.append(row)
    before = dict(row)
    row.update({k: _clean(v) for k, v in fields.items()})
    if row["status"] == "followed_up" and not row["followup_sent_on"]:
        row["followup_sent_on"] = date
    if note:
        row["notes"] = _append_note(row["notes"], note, date)
    if fresh or row != before:
        _write(WAITING, WAITING_HEADER, rows)
    return dict(row)


def remove_waiting(opp_id: str, date: str | None = None) -> bool:
    """Take one row off the list (a reply came, or it left applied) and drop its hand follow-up."""
    rows = load_waiting()
    if not any(r["opportunity_id"] == opp_id for r in rows):
        return False
    _write(WAITING, WAITING_HEADER, [r for r in rows if r["opportunity_id"] != opp_id])
    for a in load_actions():
        if a["opportunity_id"] == opp_id and a["status"] == "open" \
                and a["action"].startswith(NO_ADDRESS_ACTION):
            upsert_action(a["action_id"], status="dropped", date=date,
                          note="left the waiting list")
    return True


def refresh_waiting(date: str | None = None, actions: bool = True) -> dict:
    """Bring waiting_list.csv in step with tracker.csv and responses.csv, saving after every row.

    Removes rows that got a reply or left applied, adds new ones, refreshes days_waiting and
    last_checked, and moves due rows on. A tracker note "followup sent <date>" means followed_up,
    so a follow-up sent by /pfe-send or before this list existed is never sent twice.
    A follow_up row with no address gets the note "no address" and one next_actions item, once;
    actions=False leaves both for the next run (the one-time backfill).
    Returns the status counts and the ids added, removed, moved and with no address.
    """
    date = date or today()
    replied = {r["opportunity_id"] for r in load_responses()}
    eligible = {r["id"]: r for r in load() if r["status"] == "applied" and r["id"] not in replied}
    out = {"added": [], "removed": [], "moved": [], "no_address": []}
    current = load_waiting()
    for row in current:
        if row["opportunity_id"] not in eligible and remove_waiting(row["opportunity_id"], date):
            out["removed"].append(row["opportunity_id"])
    have = {r["opportunity_id"]: r for r in current}
    for opp_id, r in eligible.items():
        old = have.get(opp_id)
        fields = _waiting_fields(r, date)
        sent = re.search(r"followup sent\s*(\S*)", r["notes"], re.I)
        previous = old["status"] if old else "waiting"
        fields["status"] = _waiting_status(previous, fields["followup_due"], date, bool(sent))
        if sent and not (old and old["followup_sent_on"]):
            on = parse_date(sent.group(1))
            fields["followup_sent_on"] = on.isoformat() if on else date
        if fields["status"] == "follow_up" and previous == "waiting":
            out["moved"].append(opp_id)
        note = None
        if fields["status"] == "follow_up" and not fields["contact_email"]:
            out["no_address"].append(opp_id)
            if actions and "no address" not in (old["notes"] if old else ""):
                note = "no address"
                upsert_action(opportunity_id=opp_id, type="application",
                              action=f"{NO_ADDRESS_ACTION} {r['company']} (applied by portal)",
                              due_date=fields["followup_due"], source_command="pfe-inbox", date=date)
        if not old:
            out["added"].append(opp_id)
        upsert_waiting(opp_id, note, date, **fields)
    for s in WAITING_STATUSES:
        out[s] = sum(r["status"] == s for r in load_waiting())
    return out


def _apply_via(r: dict) -> str:
    """email or platform, read from best_method (free text), then from the contact fields."""
    m = r["best_method"].strip().lower()
    if m.startswith("email"):
        return "email"
    if any(k in m for k in ("portal", "form", "apply", "listing")):
        return "platform"
    if r["application_url"].strip():
        return "platform"
    if "@" in r["supervisor_email"] + r["hr_email"]:
        return "email"
    return ""


def _method(r: dict) -> str:
    """Finer route for the totals sheet: email, web form, portal (account), domestic fallback or (none)."""
    m = r["best_method"].strip().lower()
    if "domestic" in m:
        return "domestic fallback"
    if "account" in m:
        return "portal (account)"
    via = _apply_via(r)
    if via == "platform":
        return "web form"
    return via or "(none)"


def export_xlsx(path: Path | str | None = None) -> Path:
    """Write tracker.csv and responses.csv to one workbook for reading in Excel.

    The workbook is a view, regenerated on every call. Never edit it and
    expect the change to reach the CSV.
    """
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    path = Path(path) if path else XLSX
    numeric = {"match_score", "selection_probability", "duration_weeks", "priority", "days_waiting"}
    wb = Workbook()
    k = HEADER.index("country") + 1
    view_header = HEADER[:k] + ["apply_via"] + HEADER[k:]
    view_rows = [{**r, "apply_via": _apply_via(r)} for r in load()]
    actions = sorted(load_actions(), key=lambda r: (
        r["status"] != "open", r["due_date"] or "9999", ACTION_PRIORITIES.index(r["priority"])
        if r["priority"] in ACTION_PRIORITIES else 9))
    for i, (name, header, rows) in enumerate(
            [("tracker", view_header, view_rows), ("next_actions", ACTIONS_HEADER, actions),
             ("waiting_list", WAITING_HEADER, sorted(load_waiting(), key=lambda r: r["followup_due"])),
             ("offers", OFFERS_HEADER, load_offers()),
             ("interviews", INTERVIEWS_HEADER, load_interviews()),
             ("responses", RESPONSES_HEADER, load_responses())]):
        ws = wb.active if i == 0 else wb.create_sheet()
        ws.title = name
        ws.append(header)
        for r in rows:
            out = []
            for h in header:
                v = r[h]
                if h in numeric and re.fullmatch(r"-?\d+(\.\d+)?", v or ""):
                    v = float(v) if "." in v else int(v)
                out.append(v)
            ws.append(out)
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F4E78")
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = ws.dimensions
        for j, h in enumerate(header, start=1):
            longest = max([len(h)] + [len(str(r[h])) for r in rows])
            ws.column_dimensions[get_column_letter(j)].width = min(max(10, longest + 2),
                                                                   80 if h == "notes" else 45)
            if h == "notes":
                for cell in ws[get_column_letter(j)][1:]:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws = wb.create_sheet("totals", 0)
    rows = load()
    blocked_csv = HERE / "blocked.csv"
    blocked = _read(blocked_csv, HEADER) if blocked_csv.exists() else []
    ws.append(["status", "rows"])
    for s, n in summary(rows).items():
        ws.append([s, n])
    ws.append(["blocked (blocked.csv)", len(blocked)])
    ws.append(["TOTAL", len(rows) + len(blocked)])
    ws.append([])
    ws.append(["priority", "rows"])
    for p in sorted({r["priority"] for r in rows}):
        ws.append([p or "(none)", sum(r["priority"] == p for r in rows)])
    ws.append([])
    ws.append(["method (enriched)", "rows", "verified or generic contact"])
    by_method = {}
    for r in rows:
        if r["status"] == "enriched":
            c = by_method.setdefault(_method(r), [0, 0])
            c[0] += 1
            c[1] += r["contact_confidence"].strip().lower() in ("verified", "generic")
    for name, c in sorted(by_method.items(), key=lambda kv: -kv[1][0]):
        ws.append([name, *c])
    ws.append([])
    ws.append(["country", "total", "applied or later", "interview/offer", "blocked"])
    later = {"applied", "acknowledged", "interview", "offer", "rejected", "no_response"}
    by = {}
    for r in rows + blocked:
        c = by.setdefault(r["country"].strip() or "(none)", [0, 0, 0, 0])
        c[0] += 1
        c[1] += r["status"] in later
        c[2] += r["status"] in {"interview", "offer"}
        c[3] += r in blocked
    for name, c in sorted(by.items(), key=lambda kv: -kv[1][0]):
        ws.append([name, *c])
    ws.column_dimensions["A"].width = 24
    for row in ws.iter_rows():
        if row[0].value in ("status", "priority", "method (enriched)", "country"):
            for cell in row:
                cell.font = Font(bold=True)
    _dashboard(wb.create_sheet("dashboard", 0), rows, blocked)
    _daily(wb.create_sheet("daily", 1), rows, blocked)
    wb.move_sheet("next_actions", -wb.sheetnames.index("next_actions"))  # first tab, opens on it
    wb.active = 0
    try:
        wb.save(path)
    except PermissionError as exc:
        raise PermissionError(f"{path} is open in another program; close it and retry") from exc
    return path


def _dashboard(ws, rows: list, blocked: list, today: _dt.date | None = None) -> list:
    """Four pie charts: every row by status, then applications sent in each of the
    last three Monday-to-Sunday weeks by their status now. Returns the blocks drawn."""
    from openpyxl.chart import PieChart, Reference
    from openpyxl.chart.label import DataLabelList
    from openpyxl.styles import Font

    today = today or _dt.date.today()
    monday = today - _dt.timedelta(days=today.weekday())
    replied = {"acknowledged", "interview", "offer", "rejected"}
    everything = rows + blocked
    blocks = [("All rows by status", everything)]
    for k, name in enumerate(("This week", "Last week", "Two weeks ago")):
        start = monday - _dt.timedelta(weeks=k)
        end = start + _dt.timedelta(days=6)
        sent = [r for r in everything
                if (d := parse_date(r["date_applied"])) and start <= d <= end]
        blocks.append((f"{name}: sent {start:%d %b} to {end:%d %b}", sent))
    ws.column_dimensions["A"].width = ws.column_dimensions["L"].width = 16
    drawn = []
    for i, (title, subset) in enumerate(blocks):
        col, top = 1 + (i % 2) * 11, 1 + (i // 2) * 24
        counts = {}
        for r in subset:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        counts = dict(sorted(counts.items(), key=lambda kv: -kv[1]))
        ws.cell(top, col, title).font = Font(bold=True, size=12)
        ws.cell(top + 1, col, "status").font = Font(bold=True)
        ws.cell(top + 1, col + 1, "rows").font = Font(bold=True)
        for j, (s, n) in enumerate(counts.items()):
            ws.cell(top + 2 + j, col, s)
            ws.cell(top + 2 + j, col + 1, n)
        after = top + 2 + len(counts)
        ws.cell(after, col, "total").font = Font(bold=True)
        ws.cell(after, col + 1, len(subset)).font = Font(bold=True)
        if i:
            answered = sum(r["status"] in replied for r in subset)
            ws.cell(after + 1, col, "replied")
            ws.cell(after + 1, col + 1, f"{answered} ({answered * 100 // len(subset)}%)"
                    if subset else "0")
        drawn.append((title, counts))
        if not counts:
            ws.cell(top + 2, col, "nothing sent")
            continue
        pie = PieChart()
        pie.title = title
        pie.add_data(Reference(ws, min_col=col + 1, min_row=top + 1, max_row=top + 1 + len(counts)),
                     titles_from_data=True)
        pie.set_categories(Reference(ws, min_col=col, min_row=top + 2, max_row=top + 1 + len(counts)))
        pie.dataLabels = DataLabelList(showVal=True, showPercent=True, showCatName=False,
                                       showSerName=False, showLegendKey=False)
        pie.legend.position = "r"
        pie.height, pie.width = 10, 13
        ws.add_chart(pie, ws.cell(top, col + 3).coordinate)
    return drawn


def _pie(ws, title, cats, vals, anchor):
    from openpyxl.chart import PieChart
    from openpyxl.chart.label import DataLabelList
    pie = PieChart()
    pie.title = title
    pie.add_data(vals, titles_from_data=False)
    pie.set_categories(cats)
    pie.dataLabels = DataLabelList(showVal=True, showPercent=True, showCatName=False,
                                   showSerName=False, showLegendKey=False)
    pie.legend.position = "r"
    pie.height, pie.width = 9, 13
    ws.add_chart(pie, anchor)


def _daily(ws, rows: list, blocked: list, today: _dt.date | None = None, days: int = 14) -> dict:
    """Daily progress tab: status totals, what each of the last `days` days did (found,
    applied, replies, blocked), and opportunities per country, each with a pie chart.
    Returns the three tables for the self-check."""
    from openpyxl.chart import Reference
    from openpyxl.styles import Font

    today = today or _dt.date.today()
    everything = rows + blocked
    bold = Font(bold=True)
    later = {"applied", "acknowledged", "interview", "offer", "rejected", "no_response"}
    replied = {"acknowledged", "interview", "offer", "rejected"}

    def header(r, c, cells):
        for j, v in enumerate(cells):
            ws.cell(r, c + j, v).font = bold

    # 1. status totals
    status = {}
    for r in everything:
        status[r["status"]] = status.get(r["status"], 0) + 1
    status = dict(sorted(status.items(), key=lambda kv: -kv[1]))
    ws.cell(1, 1, "All opportunities by status").font = Font(bold=True, size=12)
    header(2, 1, ["status", "rows"])
    for j, (s, n) in enumerate(status.items()):
        ws.cell(3 + j, 1, s); ws.cell(3 + j, 2, n)
    end = 3 + len(status)
    header(end, 1, ["TOTAL", len(everything)])
    if status:
        _pie(ws, "All opportunities by status",
             Reference(ws, min_col=1, min_row=3, max_row=end - 1),
             Reference(ws, min_col=2, min_row=3, max_row=end - 1), "D1")

    # 2. day by day; blocked has no date column, so its date is read from the dated "-> blocked" note
    blocked_on = lambda r: [_dt.date.fromisoformat(d) for d in
                            re.findall(r"(\d{4}-\d{2}-\d{2}) [^|]*?-> blocked", r["notes"])]
    top = max(end + 3, 21)
    ws.cell(top, 1, f"Day by day, last {days} days").font = Font(bold=True, size=12)
    header(top + 1, 1, ["date", "found", "applied", "replies", "blocked"])
    per_day = []
    for k in range(days):
        d = today - _dt.timedelta(days=k)
        per_day.append([d.isoformat(),
                        sum(parse_date(r["date_discovered"]) == d for r in everything),
                        sum(parse_date(r["date_applied"]) == d for r in everything),
                        sum(parse_date(r["date_response"]) == d for r in everything),
                        sum(d in blocked_on(r) for r in blocked)])
    for j, line in enumerate(per_day):
        for c, v in enumerate(line):
            ws.cell(top + 2 + j, 1 + c, v)
    tot = top + 2 + days
    header(tot, 1, [f"TOTAL {days} days"] + [sum(line[c] for line in per_day) for c in range(1, 5)])
    # enriched has no date column either: rows whose dated note says "-> enriched" or "added as enriched" today
    enriched = sum(bool(re.search(rf"{today.isoformat()} (?:[^|]*?-> |added as )enriched", r["notes"]))
                   for r in everything)
    today_line = list(zip(["found", "enriched", "applied", "replies", "blocked"],
                          [per_day[0][1], enriched] + per_day[0][2:]))
    ws.cell(top, 8, "Today").font = Font(bold=True, size=12)
    for j, (name, v) in enumerate(today_line):
        ws.cell(top + 1 + j, 8, name); ws.cell(top + 1 + j, 9, v)
    if sum(v for _, v in today_line):
        _pie(ws, f"Today ({today:%d %b})", Reference(ws, min_col=8, min_row=top + 1, max_row=top + 5),
             Reference(ws, min_col=9, min_row=top + 1, max_row=top + 5), ws.cell(top, 11).coordinate)
    else:
        ws.cell(top + 6, 8, "nothing yet today")

    # 3. per country
    by = {}
    for r in everything:
        c = by.setdefault(r["country"].strip() or "(none)", [0, 0, 0, 0, 0])
        c[0] += 1
        c[1] += r["status"] in later
        c[2] += r["status"] in replied
        c[3] += r["status"] in {"interview", "offer"}
        c[4] += r["status"] == "blocked"
    countries = sorted(by.items(), key=lambda kv: -kv[1][0])
    top = tot + 3
    ws.cell(top, 1, "Opportunities by country").font = Font(bold=True, size=12)
    header(top + 1, 1, ["country", "found", "applied", "replies", "interview/offer", "blocked"])
    for j, (name, c) in enumerate(countries):
        ws.cell(top + 2 + j, 1, name)
        for k, v in enumerate(c):
            ws.cell(top + 2 + j, 2 + k, v)
    last = top + 2 + len(countries)
    header(last, 1, ["TOTAL"] + [sum(c[k] for _, c in countries) for k in range(5)])
    if countries:
        n = min(8, len(countries))
        _pie(ws, "Found per country (top 8)", Reference(ws, min_col=1, min_row=top + 2, max_row=top + 1 + n),
             Reference(ws, min_col=2, min_row=top + 2, max_row=top + 1 + n), ws.cell(top, 8).coordinate)
    ws.column_dimensions["A"].width = 22
    for col in "BCDEF":
        ws.column_dimensions[col].width = 12
    ws.column_dimensions["H"].width = 10
    return {"status": status, "days": per_day, "today": dict(today_line), "countries": dict(countries)}


def summary(rows: list | None = None) -> dict:
    counts = {s: 0 for s in STATUSES}
    for r in (load() if rows is None else rows):
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return counts


# ------------------------------------------------ setup-test cleanup only

def _remove_rows(ids: list, reset_counter_to: int | None = None) -> None:
    """Not for campaign use: dead rows are moved with archive_rows(), never deleted.
    Exists so the workspace setup test can remove its dummy rows."""
    rows = load()
    keep = [r for r in rows if r["id"] not in set(ids)]
    if len(keep) != len(rows) - len(set(ids)):
        raise KeyError("some ids not found")
    _write(TRACKER, HEADER, keep)
    if reset_counter_to is not None:
        _write_counter(reset_counter_to)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    if cmd == "summary":
        counts = summary()
        print(f"{sum(counts.values())} rows in {TRACKER.name}")
        for s, n in counts.items():
            print(f"  {s:13s} {n}")
        print(f"{len(load_seen())} dead-lead keys in {SEEN.name} (checked by add_rows)")
        archived = load_archive()
        print(f"{len(archived)} full rows kept in {ARCHIVE.name} (recovery copy)")
        print(f"next id: {next_id()}")
    elif cmd == "archive":
        out = archive_rows()
        print(f"deleted {len(out['moved'])} rows from {TRACKER.name}: {out['by_status']}")
        print(f"{out['remaining']} left, {out['seen_total']} keys in {SEEN.name} "
              f"(+{out['seen_added']}), {out['archive_total']} rows in {ARCHIVE.name}")
    elif cmd == "export":
        print(export_xlsx())
    elif cmd == "test-dashboard":
        from openpyxl import Workbook
        row = lambda s, d: {"status": s, "date_applied": d}
        got = _dashboard(Workbook().active,
                         [row("applied", "2026-09-28"), row("rejected", "2026-09-22"),
                          row("discovered", ""), row("applied", "2026-09-10")],
                         [row("blocked", "2026-09-30")], today=_dt.date(2026, 9, 30))
        assert got[0][1] == {"applied": 2, "rejected": 1, "discovered": 1, "blocked": 1}, got[0]
        assert got[1][1] == {"applied": 1, "blocked": 1}, got[1]
        assert got[2][1] == {"rejected": 1} and got[3][1] == {}, got
        full = lambda s, found, applied, resp, country, notes="": {
            "status": s, "date_discovered": found, "date_applied": applied,
            "date_response": resp, "country": country, "notes": notes}
        day = _daily(Workbook().active,
                     [full("applied", "2026-09-29", "2026-09-30", "", "Italy"),
                      full("rejected", "2026-09-20", "2026-09-21", "2026-09-30", "France"),
                      full("enriched", "2026-09-29", "", "", "Spain", "2026-09-30 discovered -> enriched: x")],
                     [full("blocked", "2026-09-30", "", "", "Italy", "2026-09-30 enriched -> blocked: login")],
                     today=_dt.date(2026, 9, 30), days=3)
        assert day["status"] == {"applied": 1, "rejected": 1, "enriched": 1, "blocked": 1}, day
        assert day["days"][0] == ["2026-09-30", 1, 1, 1, 1], day["days"]
        assert day["days"][1] == ["2026-09-29", 2, 0, 0, 0], day["days"]
        assert day["today"] == {"found": 1, "enriched": 1, "applied": 1, "replies": 1, "blocked": 1}, day
        assert day["countries"]["Italy"] == [2, 1, 0, 0, 1], day["countries"]
        print("dashboard self-check ok")
    elif cmd == "test-actions":
        tmp_dir = Path(tempfile.mkdtemp())
        ACTIONS, BACKUP_DIR = tmp_dir / "next_actions.csv", tmp_dir / "backups"
        a = upsert_action(action="ask the school for the convention", type="university", company="X")
        assert a["action_id"] == "ACT-0001" and a["status"] == "open", a
        b = upsert_action(action="ask the school for the convention", type="university", note="asked")
        assert b["action_id"] == "ACT-0001" and b["notes"].endswith("asked"), b
        c = upsert_action(action="reply to Y", type="email", company="Y", due_date="2026-11-01")
        assert c["action_id"] == "ACT-0002", c
        d = upsert_action("ACT-0001", status="done")
        assert d["done_on"] == today() and len(load_actions()) == 2, d
        try:
            upsert_action(action="z", type="phone")
            raise AssertionError("bad type accepted")
        except ValueError:
            pass
        shutil.rmtree(tmp_dir)
        print("actions self-check ok")
    elif cmd == "test-waiting":
        step = _waiting_status
        assert step("waiting", "2026-10-30", "2026-10-30", False) == "waiting"     # due today: not passed
        assert step("waiting", "2026-10-29", "2026-10-30", False) == "follow_up"
        assert step("waiting", "", "2026-10-30", False) == "waiting"
        assert step("follow_up", "2026-11-30", "2026-10-30", False) == "follow_up"
        assert step("follow_up", "2026-10-29", "2026-10-30", True) == "followed_up"
        assert step("followed_up", "2026-10-29", "2026-10-30", False) == "followed_up"
        tmp_dir = Path(tempfile.mkdtemp())
        TRACKER, RESPONSES, WAITING = tmp_dir / "t.csv", tmp_dir / "r.csv", tmp_dir / "w.csv"
        ACTIONS, BACKUP_DIR = tmp_dir / "a.csv", tmp_dir / "backups"
        ARCHIVE, SEEN = tmp_dir / "x.csv", tmp_dir / "s.csv"
        row = lambda i, **f: {**{h: "" for h in HEADER}, "id": i, "status": "applied",
                              "company": i, "company_domain": i + ".org", "project_title": i,
                              "date_applied": "2026-10-01", "followup_due": "2026-10-19", **f}
        _write(TRACKER, HEADER, [
            row("PFE-0001", email_sent="a@x.org", followup_due="2026-11-30"),   # not due
            row("PFE-0002", email_sent="b@x.org"),                              # due
            row("PFE-0003", email_sent="NO", hr_email="jobs@x.org"),            # portal, due
            row("PFE-0004", email_sent="YES", supervisor_email="d@x.org (lab)",
                notes="2026-10-20 followup sent 2026-10-20 in thread"),         # already sent
            row("PFE-0005", email_sent="e@x.org"),                              # has a reply
            row("PFE-0006", email_sent="f@x.org", status="rejected")])
        _write(RESPONSES, RESPONSES_HEADER, [{**{h: "" for h in RESPONSES_HEADER},
                                              "opportunity_id": "PFE-0005"}])
        got = refresh_waiting("2026-10-30")
        assert (got["waiting"], got["follow_up"], got["followed_up"]) == (1, 2, 1), got
        assert got["moved"] == ["PFE-0002", "PFE-0003"] and got["no_address"] == ["PFE-0003"], got
        w = {r["opportunity_id"]: r for r in load_waiting()}
        assert len(w) == 4 and w["PFE-0001"]["days_waiting"] == "29", w
        assert w["PFE-0004"]["followup_sent_on"] == "2026-10-20", w["PFE-0004"]
        assert w["PFE-0004"]["contact_email"] == "d@x.org", w["PFE-0004"]
        assert w["PFE-0003"]["method"] == "portal" and not w["PFE-0003"]["contact_email"]
        assert w["PFE-0003"]["notes"].endswith("no address"), w["PFE-0003"]
        assert len(load_actions()) == 1 and load_actions()[0]["status"] == "open"
        count = len(list(BACKUP_DIR.iterdir()))
        again = refresh_waiting("2026-10-30")
        assert not again["moved"] and not again["added"] and len(load_actions()) == 1, again
        assert len(list(BACKUP_DIR.iterdir())) == count, "same-day refresh wrote backups"
        sent = upsert_waiting("PFE-0002", status="followed_up", date="2026-10-30")
        assert sent["followup_sent_on"] == "2026-10-30", sent
        add_response(opportunity_id="PFE-0003", from_email="z@x.org")
        assert not any(r["opportunity_id"] == "PFE-0003" for r in load_waiting())
        assert load_actions()[0]["status"] == "dropped", load_actions()
        update_status("PFE-0001", "rejected", "no capacity")
        assert not any(r["opportunity_id"] == "PFE-0001" for r in load_waiting())
        try:
            upsert_waiting("PFE-0006")
            raise AssertionError("rejected row accepted")
        except ValueError:
            pass
        last = refresh_waiting("2026-10-31")
        assert last["followed_up"] == 2 and last["waiting"] == last["follow_up"] == 0, last
        shutil.rmtree(tmp_dir)
        print("waiting self-check ok")
    else:
        print(__doc__)
