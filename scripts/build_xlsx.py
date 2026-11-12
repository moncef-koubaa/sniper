#!/usr/bin/env python3
"""Shared openpyxl writer for /find-contacts and /find-offers.

Usage: python3 scripts/build_xlsx.py <run.json> <out.xlsx>
run.json:
  {"kind": "contacts", "run_date": "YYYY-MM-DD", "companies": [ {<Companies columns>} ], "contacts": [ {...} ]}
  {"kind": "offers",   "run_date": "YYYY-MM-DD", "offers":    [ {<Offers columns>} ] }
Keys are the column names below (missing keys -> empty cell). Rows are re-sorted by Score (desc) and Rank is
rewritten 1..n, so row 2 is always the top priority. The script never overwrites: if <out.xlsx> exists it writes
<out>_2.xlsx, _3 ... and prints the path used.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import yaml
from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent

COMPANY_COLS = [
    "Rank", "Score", "Score breakdown", "Company", "Country/City", "Sector", "Website", "Why it fits",
    "Careers email", "HR name", "HR role", "HR email", "CEO/Director name", "CEO email",
    "Chem/Process engineer 1 name", "Chem/Process engineer 1 role", "Chem/Process engineer 1 email",
    "Chem/Process engineer 1 LinkedIn URL", "Chem/Process engineer 2 name", "Chem/Process engineer 2 role",
    "Chem/Process engineer 2 email", "Chem/Process engineer 2 LinkedIn URL", "Other contact name",
    "Other contact role", "Other contact email", "Primary contact", "Email confidence", "Language",
    "Email subject", "Email body draft", "CV decision", "CV file", "Sources", "Status", "Date sent",
    "Follow-up date", "Response", "Notes"]
CONTACT_COLS = ["Company", "Name", "Role", "Category", "Email", "Confidence", "Source URL", "LinkedIn URL"]
OFFER_COLS = [
    "Rank", "Score", "Score breakdown", "Title", "Company", "Team/Lab", "Location", "Start", "Duration", "Pay",
    "Language", "Deadline", "Key requirements", "My matching evidence", "Gaps (honest)", "CV decision", "CV file",
    "Cover letter file", "Contact on offer", "Application method", "Link to post", "Date found", "Status",
    "Date applied", "Notes"]
STATUSES = ["To send", "Sent", "Followed up", "Replied", "Rejected", "Interview"]
WIDE = {"Score breakdown": 48, "Why it fits": 40, "Email body draft": 80, "Sources": 50, "Notes": 40,
        "Key requirements": 50, "My matching evidence": 50, "Gaps (honest)": 40, "Email subject": 45,
        "Link to post": 45, "Title": 40, "Website": 30, "CV file": 45, "Cover letter file": 40}

HEAD_FILL = PatternFill("solid", fgColor="1F3864")
GREEN = PatternFill("solid", fgColor="C6EFCE")
AMBER = PatternFill("solid", fgColor="FFEB9C")
GREY = PatternFill("solid", fgColor="D9D9D9")
RED = PatternFill("solid", fgColor="FFC7CE")


def sheet(wb, title, cols, rows, score_cfg=None, deadline=False, status=True):
    ws = wb.create_sheet(title)
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = HEAD_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append([r.get(c, "") if not isinstance(r.get(c), (list, dict)) else json.dumps(r.get(c), ensure_ascii=False)
                   for c in cols])
    n = ws.max_row
    for i, c in enumerate(cols, 1):
        letter = get_column_letter(i)
        ws.column_dimensions[letter].width = WIDE.get(c, 18 if len(c) < 18 else len(c) + 2)
        for cell in ws[letter][1:]:
            cell.alignment = Alignment(wrap_text=c in WIDE or c in ("Email body draft",), vertical="top")
            if isinstance(cell.value, str) and cell.value.startswith("http") and len(cell.value) < 250:
                cell.hyperlink = cell.value
                cell.font = Font(color="0563C1", underline="single")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{max(n, 2)}"
    if score_cfg and "Score" in cols and n > 1:
        col = get_column_letter(cols.index("Score") + 1)
        rng = f"{col}2:{col}{n}"
        thr, amber = score_cfg["custom_cv_threshold"], score_cfg.get("bands", {}).get("amber_min", 60)
        ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThanOrEqual", formula=[str(thr)], fill=GREEN))
        ws.conditional_formatting.add(rng, CellIsRule(operator="between", formula=[str(amber), str(thr - 0.01)], fill=AMBER))
        ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=[str(amber)], fill=GREY))
    if status and "Status" in cols and n > 1:
        col = get_column_letter(cols.index("Status") + 1)
        dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}{max(n, 200)}")
    if deadline and "Deadline" in cols and n > 1:
        col = get_column_letter(cols.index("Deadline") + 1)
        for cell in ws[col][1:]:
            v = cell.value
            if isinstance(v, str):
                try:
                    cell.value = dt.date.fromisoformat(v[:10])
                    cell.number_format = "yyyy-mm-dd"
                except ValueError:
                    pass
        ws.conditional_formatting.add(
            f"A2:{get_column_letter(len(cols))}{n}",
            FormulaRule(formula=[f'AND(ISNUMBER(${col}2),${col}2-TODAY()<=7,${col}2>=TODAY())'], fill=RED))
    return ws


def readme(wb, cfg, kind, run_date, counts):
    ws = wb.create_sheet("README")
    lines = [
        [f"PFE 2027 — {kind} sheet — run {run_date}"], [],
        ["Scoring (config/scoring.yaml)", "weight"],
        *[[k, v] for k, v in cfg["weights"].items()],
        ["custom_cv_threshold", cfg["custom_cv_threshold"]],
        ["max_custom_cvs_per_run", cfg["max_custom_cvs_per_run"]],
        ["cover_letter_threshold", cfg.get("cover_letter_threshold", 60)], [],
        ["How to read"],
        ["Rank / Score", "Rows sorted by Score, highest first. Score = sum of the six criteria (0-100)."],
        ["Score breakdown", "Points per criterion / weight, then the note justifying each sub-score."],
        ["Colours", f"green >= {cfg['custom_cv_threshold']} (custom CV) · amber 60-{cfg['custom_cv_threshold'] - 1} · grey < 60"
                    + (" · red row = deadline within 7 days" if kind == "offers" else "")],
        ["Email confidence", "verified = address appears verbatim on the source URL · inferred = built from a "
                             "confirmed company pattern, NOT verified · none = no address"],
        ["CV decision", "Custom = built by /tailor-cv · Custom (pending) = over the per-run cap, library CV meanwhile "
                        "· Library = best library CV (reason in Notes / CV file)"],
        ["Status", "Dropdown: " + " / ".join(STATUSES) + ". Nothing has been sent: every email is a draft."],
        ["GENERIC SALUTATION", "In Notes when no named recipient could be found."], [],
        ["Counts", json.dumps(counts, ensure_ascii=False)],
    ]
    for line in lines:
        ws.append(line)
    ws["A1"].font = Font(bold=True, size=13)
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 110


def main(src: str, out: str) -> str:
    data = json.loads(Path(src).read_text())
    cfg = yaml.safe_load((ROOT / "config" / "scoring.yaml").read_text())
    kind, run_date = data["kind"], data.get("run_date", dt.date.today().isoformat())
    wb = Workbook()
    wb.remove(wb.active)
    key = "companies" if kind == "contacts" else "offers"
    rows = sorted(data[key], key=lambda r: -float(r.get("Score") or 0))
    for i, r in enumerate(rows, 1):
        r["Rank"] = i
        r.setdefault("Status", "To send")
    if kind == "contacts":
        sheet(wb, "Companies", COMPANY_COLS, rows, cfg)
        sheet(wb, "Contacts", CONTACT_COLS, data.get("contacts", []), status=False)
        counts = {"companies": len(rows), "contacts": len(data.get("contacts", []))}
    else:
        sheet(wb, "Offers", OFFER_COLS, rows, cfg, deadline=True)
        counts = {"offers": len(rows)}
    readme(wb, cfg, kind, run_date, counts)
    p = Path(out)
    k = 2
    while p.exists():
        p = Path(out).with_name(f"{Path(out).stem}_{k}{Path(out).suffix}")
        k += 1
    p.parent.mkdir(parents=True, exist_ok=True)
    wb.save(p)
    load_workbook(p)  # proves the file opens
    return str(p)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    print(main(sys.argv[1], sys.argv[2]))
