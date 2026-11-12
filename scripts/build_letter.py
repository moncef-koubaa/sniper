#!/usr/bin/env python3
"""Turn a cover-letter Markdown file into .docx (+ .pdf) with Nermine's letter layout, and check it.

Usage: python3 scripts/build_letter.py outputs/letters/<Company>_<lang>.md [--no-pdf]
Markdown convention (what /find-offers writes):
  line 1  **Moumen Nermine**
  line 2  nermine.moumen@insat.ucar.tn | +216 27 040 414
  blank
  **Objet : …**  /  **Subject: …**
  blank, then one paragraph per block (salutation, ¶1…¶4, closing lines, signature).
Layout: A4, Times New Roman 12 pt, justified body, 2.5 cm margins (matches the Google Docs exports).
Checks: body word count 250-390 (CL-01), PDF exactly 1 page. Prints JSON; exit 1 if a check fails.
Never overwrites: existing .docx/.pdf are archived to _archive/<date>/ first.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def md_to_html(md: str) -> str:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", md.strip()) if b.strip()]
    out = []
    for i, b in enumerate(blocks):
        lines = [html.escape(l) for l in b.splitlines()]
        lines = [re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", l) for l in lines]
        align = "left" if i < 2 or len(b) < 90 else "justify"
        out.append(f'<p style="text-align:{align};margin:0 0 10pt 0">' + "<br/>".join(lines) + "</p>")
    return ('<html><head><meta charset="utf-8"><style>@page{size:21cm 29.7cm;margin:2.5cm}'
            'body{font-family:"Times New Roman",Liberation Serif,serif;font-size:12pt}</style></head><body>'
            + "".join(out) + "</body></html>")


def body_words(md: str) -> int:
    blocks = [b for b in re.split(r"\n\s*\n", md.strip()) if b.strip()]
    return len(" ".join(blocks[2:]).replace("**", "").split())  # skip header + subject


def main(argv: list[str]) -> int:
    src = Path(argv[0]).resolve()
    md = src.read_text()
    rep = {"letter": str(src.relative_to(ROOT)), "body_words": body_words(md)}
    today = dt.date.today().isoformat()
    for ext in (".docx", ".pdf"):
        old = src.with_suffix(ext)
        if old.exists():
            dest = ROOT / "_archive" / today / old.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old, dest)
    with tempfile.TemporaryDirectory() as td:
        h = Path(td) / (src.stem + ".html")
        h.write_text(md_to_html(md))
        subprocess.run(["soffice", "--headless", "--convert-to", "docx:MS Word 2007 XML", "--outdir", td, str(h)],
                       capture_output=True, timeout=180)
        docx = Path(td) / (src.stem + ".docx")
        if docx.exists():
            shutil.copy2(docx, src.with_suffix(".docx"))
            rep["docx"] = str(src.with_suffix(".docx").relative_to(ROOT))
            if "--no-pdf" not in argv:
                subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", td, str(docx)],
                               capture_output=True, timeout=180)
                pdf = Path(td) / (src.stem + ".pdf")
                if pdf.exists():
                    shutil.copy2(pdf, src.with_suffix(".pdf"))
                    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
                    rep["pdf"] = str(src.with_suffix(".pdf").relative_to(ROOT))
                    rep["pages"] = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    rep["ok"] = 250 <= rep["body_words"] <= 390 and "docx" in rep and rep.get("pages", 1) == 1
    print(json.dumps(rep, ensure_ascii=False))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
