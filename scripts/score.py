#!/usr/bin/env python3
"""Deterministic scoring for /find-contacts and /find-offers.

Claude judges only the qualitative sub-scores (0.0-1.0 per criterion, each with a short note); this script
does all the arithmetic, the CV decision (threshold + per-run cap), the colour band and the ranking.

Usage:
  python3 scripts/score.py rows.json [-o scored.json]
rows.json = list of objects, each with at least:
  {"key": "<company or offer id>", "subscores": {"domain_fit": 0.8, ...}, "notes": {"domain_fit": "...", ...}}
Other fields are passed through untouched. Output (stdout or -o): the same rows sorted by score desc, with
  score, points{criterion: pts}, breakdown "Domain 24/30 · Skills 14/20 · …", band (green/amber/grey),
  cv_decision ("Custom" | "Custom (pending)" | "Library"), letter_due (bool, offers), rank.
Self-test: python3 scripts/score.py --selftest
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scoring.yaml"
LABELS = {"domain_fit": "Domain", "skills_match": "Skills", "feasibility": "Feasibility",
          "hiring_signal": "Hiring", "contact_quality": "Contact", "strategic_value": "Strategic"}


def load_config() -> dict:
    cfg = yaml.safe_load(CONFIG.read_text())
    total = sum(cfg["weights"].values())
    if total != 100:
        raise SystemExit(f"config/scoring.yaml: weights sum to {total}, must be 100")
    return cfg


def score_rows(rows: list[dict], cfg: dict) -> list[dict]:
    w = cfg["weights"]
    thr = cfg["custom_cv_threshold"]
    amber = cfg.get("bands", {}).get("amber_min", 60)
    for r in rows:
        subs = r.get("subscores", {})
        missing = [k for k in w if k not in subs]
        if missing:
            raise SystemExit(f"row {r.get('key')}: missing sub-scores {missing}")
        pts = {}
        for k, weight in w.items():
            s = float(subs[k])
            if not 0.0 <= s <= 1.0:
                raise SystemExit(f"row {r.get('key')}: sub-score {k}={s} outside 0-1")
            pts[k] = round(weight * s, 1)
        r["points"] = pts
        r["score"] = round(sum(pts.values()), 1)
        r["breakdown"] = " · ".join(f"{LABELS.get(k, k)} {pts[k]:g}/{w[k]}" for k in w)
        r["band"] = "green" if r["score"] >= thr else ("amber" if r["score"] >= amber else "grey")
        r["letter_due"] = r["score"] >= cfg.get("cover_letter_threshold", 60)
    rows.sort(key=lambda r: (-r["score"], str(r.get("key", ""))))
    built = 0
    for i, r in enumerate(rows, 1):
        r["rank"] = i
        if r["score"] >= thr:
            if built < cfg["max_custom_cvs_per_run"]:
                r["cv_decision"] = "Custom"
                built += 1
            else:
                r["cv_decision"] = "Custom (pending)"
        else:
            r["cv_decision"] = "Library"
    return rows


def selftest() -> None:
    cfg = load_config()
    one = {k: 1.0 for k in cfg["weights"]}
    rows = [{"key": "a", "subscores": one}, {"key": "b", "subscores": {k: 0.5 for k in one}}]
    rows += [{"key": f"c{i}", "subscores": {k: 0.8 for k in one}} for i in range(6)]
    out = score_rows(rows, cfg)
    assert out[0]["key"] == "a" and out[0]["score"] == 100.0 and out[0]["rank"] == 1
    assert all(abs(sum(r["points"].values()) - r["score"]) < 0.05 for r in out)
    assert [r["cv_decision"] for r in out].count("Custom") == cfg["max_custom_cvs_per_run"]
    assert out[-1]["score"] == 50.0 and out[-1]["band"] == "grey" and out[-1]["cv_decision"] == "Library"
    assert [r["score"] for r in out] == sorted((r["score"] for r in out), reverse=True)
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        selftest()
        sys.exit(0)
    data = json.loads(Path(a[0]).read_text())
    res = score_rows(data, load_config())
    text = json.dumps(res, indent=1, ensure_ascii=False)
    if "-o" in a:
        Path(a[a.index("-o") + 1]).write_text(text + "\n")
    else:
        print(text)
