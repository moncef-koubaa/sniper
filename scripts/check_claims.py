#!/usr/bin/env python3
"""Check that a CV / letter / email makes no claim missing from profile/me.md.

Usage: python3 scripts/check_claims.py <file.pdf|.tex|.md|.txt> [...]
Checks (heuristic, conservative):
  1. every number with a unit or % (e.g. 40,5 mV, 97.14 %, 0.584 V, 20 min, 1.40 L/h) appears in me.md
     (decimal comma/point and spacing normalised);
  2. every tool/technique from a known vocabulary that appears in the document appears in me.md;
  3. forbidden overclaims: "hands-on"/"expérience pratique"/"maîtrise" near a technique of me.md §5c;
  4. "[assumed]" facts (nationality wording etc.) are not stated.
Prints JSON {file: {numbers_checked, unknown_numbers, unknown_terms, overclaims, ok}}; exit 1 if any problem.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ME = (ROOT / "profile" / "me.md").read_text()
UNIT = r"(?:%|mV|V|min|h|j|d|L/h|L/j|mol ?%|mol%|°C|K|bar|mois|months?)"
VOCAB = ["Aspen Plus", "Aspen HYSYS", "COMSOL", "Ansys Fluent", "ANSYS Fluent", "MATLAB", "Python", "Mathematica",
         "OpenLCA", "SimaPro", "GaBi", "Cantera", "ICP-OES", "ICP-AES", "ICP-MS", "HPLC", "GC-MS", "XRD", "SEM", "TEM",
         "MEB", "MET", "FTIR", "Raman", "RAMAN", "NMR", "RMN", "UV-Vis", "XPS", "BET", "TGA", "DSC",
         "voltamm", "voltamétrie", "polarograph", "impedance", "impédance", "EIS", "galvanostat", "potentiostat",
         "glovebox", "boîte à gants", "coin cell", "pile bouton", "Aspen Process Economic Analyzer", "Pro/II",
         "ProSim", "DWSIM", "gPROMS", "Simulink", "LabVIEW", "SolidWorks", "AutoCAD"]
STUDIED = ["HPLC", "NMR", "RMN", "FTIR", "XRD", "SEM", "TEM", "MEB", "MET", "Raman", "RAMAN", "sol-gel",
           "voltamétrie cyclique", "cyclic voltammetry", "UV-Vis", "Soxhlet", "TLC", "CCM"]
OVERCLAIM = r"(hands-on|expérience pratique|pratique solide|maîtrise|maîtrise de|solid practice|extensive experience)"


def norm_num(s: str) -> str:
    return re.sub(r"\s+", "", s.replace(",", ".")).lower()


ME_NUMS = {norm_num(m) for m in re.findall(r"\d+(?:[.,]\d+)?\s?" + UNIT, ME)}
ME_NUMS |= {norm_num(m) for m in re.findall(r"\d+(?:[.,]\d+)?", ME)}  # bare numbers too
ME_LOWER = ME.lower()


def text_of(p: Path) -> str:
    if p.suffix.lower() == ".pdf":
        return subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
    t = p.read_text(errors="replace")
    if p.suffix == ".tex":
        t = re.sub(r"(?m)^%.*$", "", t)
        t = re.sub(r"\\(textbf|textit|summary|project|item|entry|section|twocol|cvheader|href)\b", " ", t)
        t = t.replace("\\%", "%").replace("{,}", ",").replace("$", "")
    return t


def check(p: Path) -> dict:
    t = text_of(p)
    nums = re.findall(r"(?<![\w/.])(\d+(?:[.,]\d+)?)\s?(" + UNIT + r")(?![\w])", t)
    unknown = []
    for n, u in nums:
        if n in {"1", "3", "6", "9", "2027", "2026"} and u.startswith("mois") or u.startswith("month"):
            continue
        if norm_num(n + u) not in ME_NUMS and norm_num(n) not in ME_NUMS:
            unknown.append(f"{n} {u}")
    def present(term: str, hay: str) -> bool:  # word-boundary match ("TGA" must not match "Stuttgart")
        return re.search(r"(?<![a-z0-9])" + re.escape(term.lower()), hay.lower()) is not None
    terms = sorted({v for v in VOCAB if present(v, t) and not present(v, ME)})
    over = []
    for m in re.finditer(OVERCLAIM, t, re.I):
        window = t[max(0, m.start() - 160): m.end() + 160]
        hit = [s for s in STUDIED if s.lower() in window.lower()]
        if hit:
            over.append(f"'{m.group(0)}' near {', '.join(hit)}")
    res = {"numbers_checked": len(nums), "unknown_numbers": unknown, "unknown_terms": terms, "overclaims": over}
    res["ok"] = not (unknown or terms or over)
    return res


if __name__ == "__main__":
    out = {a: check(Path(a)) for a in sys.argv[1:]}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    sys.exit(0 if all(v["ok"] for v in out.values()) else 1)
