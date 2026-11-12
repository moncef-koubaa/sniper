#!/usr/bin/env python3
"""Pick the best library CV for a target by keyword overlap with resumes/library/index.yaml.

Usage: python3 scripts/pick_cv.py --lang fr|en "text of the offer or company description / keywords"
Prints JSON: ranked candidates (id, score, matched keywords) and a one-line reason for the winner.
Language is a hard filter (falls back to the other language only if none exists).
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "resumes" / "library" / "index.yaml"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def pick(text: str, lang: str) -> dict:
    cvs = yaml.safe_load(INDEX.read_text())["cvs"]
    t = " " + re.sub(r"[^a-z0-9+\-/ ]", " ", norm(text)) + " "
    ranked = []
    for cv in cvs:
        hits = [k for k in cv["keywords"] if f" {norm(k)} " in t or (len(k) > 5 and norm(k) in t)]
        focus_hits = [w for w in re.split(r"[ ,&/]+", norm(cv["focus"])) if len(w) > 5 and w in t]
        score = len(set(hits)) + 0.25 * len(set(focus_hits))
        ranked.append({"id": cv["id"], "language": cv["language"], "score": round(score, 2),
                       "matched": sorted(set(hits)), "best_for": cv["best_for"]})
    same = [r for r in ranked if r["language"] == lang] or ranked
    same.sort(key=lambda r: (-r["score"], r["id"]))
    win = same[0]
    reason = (f"{win['id']}: best {lang.upper()} keyword overlap ({len(win['matched'])} terms: "
              f"{', '.join(win['matched'][:5]) or 'none — default CV'})")
    if win["score"] == 0:
        win = next(r for r in same if r["id"] in ("process_fr", "process_en") and r["language"] == lang)
        reason = f"{win['id']}: no keyword overlap, default {lang.upper()} CV"
    return {"choice": win["id"], "reason": reason, "ranked": same[:4]}


if __name__ == "__main__":
    args = sys.argv[1:]
    lang = args[args.index("--lang") + 1] if "--lang" in args else "fr"
    text = " ".join(a for i, a in enumerate(args) if a != "--lang" and (i == 0 or args[i - 1] != "--lang"))
    print(json.dumps(pick(text, lang), indent=1, ensure_ascii=False))
