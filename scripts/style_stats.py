#!/usr/bin/env python3
"""Quantitative style stats for writing samples (used by /learn-style and the analysis notes).
Usage: python3 scripts/style_stats.py <pdf|txt> ...  -> JSON per document."""
import json, re, subprocess, sys
from pathlib import Path

HEAD = re.compile(r"^(FORMATION|EDUCATION|EXP[ÉE]RIENCE.*|PROFESSIONAL EXPERIENCE|ADDITIONAL EXPERIENCE|PROJETS ACAD[ÉE]MIQUES|ACADEMIC PROJECTS|COMP[ÉE]TENCES TECHNIQUES|TECHNICAL SKILLS|ACTIVIT[ÉE]S EXTRASCOLAIRES|EXTRACURRICULAR ACTIVITIES|LANGUES.*|LANGUAGES.*|CERTIFICATES)\s*$")

def text_of(p):
    p = Path(p)
    if p.suffix.lower() == ".pdf":
        return subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
    return p.read_text(errors="replace")

def cv_stats(t):
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    sections = [l for l in lines if HEAD.match(l)]
    bullets, cur = [], None
    for l in lines:
        if l.startswith(("•", "∙")):
            if cur: bullets.append(cur)
            cur = l.lstrip("•∙ ").strip()
        elif cur is not None and not HEAD.match(l) and not re.search(r"\d{2}/\d{4}|20\d\d–", l) and l[:1].islower():
            cur += " " + l
        else:
            if cur: bullets.append(cur); cur = None
    if cur: bullets.append(cur)
    words = [len(b.split()) for b in bullets]
    first = [b.split()[0].strip(":") for b in bullets if b.split()]
    return {"sections": sections, "n_bullets": len(bullets),
            "avg_bullet_words": round(sum(words)/len(words), 1) if words else 0,
            "max_bullet_words": max(words) if words else 0,
            "bullets_with_number": sum(bool(re.search(r"\d", b)) for b in bullets),
            "first_words": first}

def letter_stats(t):
    paras = [p.strip().replace("\n", " ") for p in re.split(r"\n\s*\n|(?<=[.,:])\n(?=[A-ZÀ-Ý])", t) if p.strip()]
    body = " ".join(paras)
    return {"words": len(body.split()), "n_blocks": len(paras),
            "salutation": next((p for p in paras if re.match(r"(Madame|Monsieur|Dear)", p)), None),
            "closing": paras[-2:] if len(paras) > 1 else paras}

if __name__ == "__main__":
    out = {}
    for a in sys.argv[1:]:
        t = text_of(a)
        out[Path(a).name] = cv_stats(t) if ("/cvs/" in a or "cv" in Path(a).name.lower() and "letter" not in a.lower()) and "Lettre" not in a else letter_stats(t)
    print(json.dumps(out, indent=1, ensure_ascii=False))
