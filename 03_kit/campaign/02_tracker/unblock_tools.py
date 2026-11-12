"""Move one row from blocked.csv back into tracker.csv and mark it applied.
Uses tracker_tools write/backup helpers. One row per call."""
import csv, datetime as dt, sys
import tracker_tools as tt
BLOCKED = tt.HERE / "blocked.csv"

def workdays(start, n):
    d = start
    while n:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d.isoformat()

def load_blocked():
    return tt._read(BLOCKED, tt.HEADER)

def apply_row(opp_id, note, **fields):
    blocked = load_blocked()
    row = next(r for r in blocked if r["id"] == opp_id)
    rows = tt.load()
    if any(r["id"] == opp_id for r in rows):
        raise ValueError(f"{opp_id} already in tracker")
    tt._write(tt.TRACKER, tt.HEADER, rows + [row])           # back into tracker (status still blocked)
    today = dt.date.today()
    out = tt.update_status(opp_id, "applied", note,
                           followup_due=workdays(today, 12), **fields)
    tt._write(BLOCKED, tt.HEADER, [r for r in blocked if r["id"] != opp_id])
    return out

def block_row(opp_id, reason):
    """Move one tracker row to blocked.csv (manual queue): every column kept, status blocked,
    reason as a dated note. Documents in 04_outbound/<ID> stay where they are."""
    rows = tt.load()
    row = next(r for r in rows if r["id"] == opp_id)
    blocked = load_blocked()
    if any(r["id"] == opp_id for r in blocked):
        raise ValueError(f"{opp_id} already in blocked.csv")
    row["notes"] = tt._append_note(row["notes"], f"{row['status']} -> blocked: {reason}", tt.today())
    row["status"] = "blocked"
    tt._write(BLOCKED, tt.HEADER, blocked + [row])           # blocked.csv first: never lose the row
    tt._write(tt.TRACKER, tt.HEADER, [r for r in rows if r["id"] != opp_id])
    tt.remove_waiting(opp_id)
    return row

def note_block(opp_id, text):
    blocked = load_blocked()
    for r in blocked:
        if r["id"] == opp_id:
            r["notes"] = tt._append_note(r["notes"], text, tt.today())
    tt._write(BLOCKED, tt.HEADER, blocked)

if __name__ == "__main__":
    print(workdays(dt.date.today(), 12))
