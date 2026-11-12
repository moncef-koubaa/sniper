#!/usr/bin/env python3
"""Compile a LaTeX CV and verify it.

Usage: python3 scripts/build_cv.py <folder-or-source.tex> [--out NAME.pdf] [--pages N] [--png]

- Compiles <folder>/source.tex with pdflatex (twice), TEXINPUTS pointing at resumes/library/_template/.
- Checks: page count == expected (default 1), no "Overfull \\hbox" wider than 2pt, no missing characters,
  the text layer is extractable. Exit code 0 only if every check passes.
- --out copies the PDF to that name in the same folder (e.g. Moumen_Nermine_CV_Air-Liquide.pdf).
- --png renders page 1 to preview.png (open it with the Read tool to eyeball overflow).
Prints a JSON report.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "resumes" / "library" / "_template"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    target = Path(argv[0]).resolve()
    src = target if target.suffix == ".tex" else target / "source.tex"
    folder = src.parent
    expected = int(argv[argv.index("--pages") + 1]) if "--pages" in argv else 1
    env = dict(os.environ, TEXINPUTS=f"{TEMPLATE}//:")
    log = ""
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", src.name],
                           cwd=folder, env=env, capture_output=True, text=True)
        log = (folder / (src.stem + ".log")).read_text(errors="replace") if (folder / (src.stem + ".log")).exists() else r.stdout
        if r.returncode != 0:
            break
    pdf = folder / (src.stem + ".pdf")
    report = {"source": str(src.relative_to(ROOT)), "compiled": r.returncode == 0 and pdf.exists()}
    if report["compiled"]:
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        report["pages"] = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        overfull = [float(x) for x in re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide", log)]
        report["overfull_boxes_pt"] = [o for o in overfull if o > 2.0]
        report["missing_chars"] = len(re.findall(r"Missing character", log))
        text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        report["words"] = len(text.split())
        report["ok"] = (report["pages"] == expected and not report["overfull_boxes_pt"]
                        and report["missing_chars"] == 0 and report["words"] > 100)
        if "--out" in argv:
            out = folder / argv[argv.index("--out") + 1]
            shutil.copy2(pdf, out)
            report["pdf"] = str(out.relative_to(ROOT))
        else:
            report["pdf"] = str(pdf.relative_to(ROOT))
        if "--png" in argv:
            subprocess.run(["pdftoppm", "-r", "80", "-png", "-singlefile", str(pdf), str(folder / "preview")])
            report["preview"] = str((folder / "preview.png").relative_to(ROOT))
    else:
        report["ok"] = False
        report["error"] = "\n".join(l for l in log.splitlines() if l.startswith("!"))[:800]
    for ext in (".aux", ".out", ".log"):
        (folder / (src.stem + ext)).unlink(missing_ok=True)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
