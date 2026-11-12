#!/usr/bin/env python3
"""Incremental document ingestion for /get-to-know-me.

Hashes every file in profile/inbox/ and writing-samples/ (plus extra paths given on the command line),
skips files whose SHA-256 is already in profile/processed/manifest.json (unless --full), extracts text
to profile/processed/text/<sha12>__<name>.txt, guesses a document class, and prints a JSON report of what
is new so Claude can read the extracted text and update profile/me.md.

Usage:
  python3 scripts/ingest.py [--full] [--dry-run] [extra paths ...]
  python3 scripts/ingest.py --mark <sha256> [<sha256> ...]   # record files as ingested into me.md

A file is only recorded in the manifest with status "ingested" once Claude has merged its facts
(--mark); extraction alone records status "extracted". Re-runs therefore re-offer extracted-but-unmerged files.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "profile" / "processed" / "manifest.json"
TEXT_DIR = ROOT / "profile" / "processed" / "text"
SCAN_DIRS = [ROOT / "profile" / "inbox", ROOT / "writing-samples" / "cvs",
             ROOT / "writing-samples" / "cover-letters", ROOT / "writing-samples" / "emails"]
SKIP_NAMES = {".gitkeep", ".DS_Store", "README.md"}
TEXT_EXT = {".txt", ".md", ".tex", ".csv", ".json", ".yaml", ".yml", ".eml"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".heic"}

CLASS_RULES = [  # (class, regex on lowercase filename + first 1500 chars of text)
    ("transcript", r"relev[ée] de notes|transcript|moyenne g[ée]n[ée]rale|cr[ée]dits ects|semestre \d"),
    ("certificate", r"\battestation\b|certificat|certificate of (completion|achievement)|this is to certify"),
    ("recommendation", r"recommandation|recommendation|to whom it may concern|je soussign[ée]"),
    ("letter", r"lettre|cover_letter|objet ?:|subject ?:|madame, monsieur|dear (dr|prof|mr|ms|hiring)"),
    ("email", r"\.eml$|^from:|^to:|^subject:|objet du mail"),
    ("report", r"rapport|report|m[ée]moire|r[ée]sum[ée]|abstract|introduction g[ée]n[ée]rale|table des mati"),
    ("cv", r"\bcv\b|curriculum|formation|education|exp[ée]rience professionnelle|professional experience|comp[ée]tences"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], timeout: int = 120) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False).stdout


def extract(path: Path) -> tuple[str, str]:
    """Return (text, method). Empty text means Claude must read the file itself (image / scan)."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        text = run(["pdftotext", "-layout", str(path), "-"])
        if len(text.strip()) < 40:  # scanned PDF
            if shutil.which("tesseract"):
                with tempfile.TemporaryDirectory() as td:
                    run(["pdftoppm", "-r", "300", "-png", str(path), f"{td}/p"], timeout=600)
                    pages = sorted(Path(td).glob("p*.png"))
                    text = "\n\f".join(run(["tesseract", str(p), "-", "-l", "fra+eng"]) for p in pages)
                return text, "ocr-tesseract"
            return "", "needs-visual-read (scanned PDF, no tesseract)"
        return text, "pdftotext"
    if ext in TEXT_EXT:
        return path.read_text(encoding="utf-8", errors="replace"), "plain"
    if ext == ".docx":
        try:
            with zipfile.ZipFile(path) as z:
                xml = z.read("word/document.xml").decode("utf-8", errors="replace")
            xml = re.sub(r"</w:p>", "\n", xml)
            return re.sub(r"<[^>]+>", "", xml), "docx-xml"
        except Exception as exc:  # noqa: BLE001
            return "", f"docx-error: {exc}"
    if ext in {".doc", ".odt", ".rtf", ".pptx", ".ppt"}:
        with tempfile.TemporaryDirectory() as td:
            run(["soffice", "--headless", "--convert-to", "txt:Text", "--outdir", td, str(path)], timeout=180)
            out = next(Path(td).glob("*.txt"), None)
            return (out.read_text(errors="replace"), "soffice") if out else ("", "soffice-failed")
    if ext in {".xlsx", ".xlsm"}:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        lines = []
        for ws in wb.worksheets:
            lines.append(f"## sheet {ws.title}")
            for row in ws.iter_rows(values_only=True):
                if any(c is not None for c in row):
                    lines.append(" | ".join("" if c is None else str(c) for c in row))
        return "\n".join(lines), "openpyxl"
    if ext in IMAGE_EXT:
        if shutil.which("tesseract"):
            return run(["tesseract", str(path), "-", "-l", "fra+eng"]), "ocr-tesseract"
        return "", "needs-visual-read (image, no tesseract)"
    return "", f"unsupported extension {ext}"


def classify(path: Path, text: str) -> str:
    rel = str(path.relative_to(ROOT)).lower() if path.is_relative_to(ROOT) else path.name.lower()
    if "/cvs/" in rel:
        return "cv"
    if "/cover-letters/" in rel:
        return "letter"
    if "/emails/" in rel:
        return "email"
    hay = (path.name.lower() + "\n" + text[:1500].lower())
    for cls, rx in CLASS_RULES:
        if re.search(rx, hay, re.M):
            return cls
    return "other"


def guess_language(text: str) -> str:
    t = text.lower()
    fr = sum(t.count(w) for w in (" les ", " des ", " une ", " pour ", " avec ", "é"))
    en = sum(t.count(w) for w in (" the ", " and ", " with ", " for ", " of "))
    return "fr" if fr > en else ("en" if en else "unknown")


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {"version": 1, "files": {}}


def save_manifest(m: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv: list[str]) -> int:
    manifest = load_manifest()
    if argv and argv[0] == "--mark":
        today = dt.date.today().isoformat()
        for h in argv[1:]:
            if h in manifest["files"]:
                manifest["files"][h]["status"] = "ingested"
                manifest["files"][h]["ingested_on"] = today
        save_manifest(manifest)
        print(json.dumps({"marked": argv[1:]}))
        return 0

    full = "--full" in argv
    dry = "--dry-run" in argv
    extra = [Path(a).resolve() for a in argv if not a.startswith("--")]
    files: list[Path] = []
    for d in SCAN_DIRS + extra:
        if d.is_file():
            files.append(d)
        elif d.is_dir():
            files += [p for p in sorted(d.rglob("*")) if p.is_file() and p.name not in SKIP_NAMES]

    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"new": [], "skipped_already_ingested": 0, "duplicates": [], "needs_visual_read": []}
    seen: dict[str, str] = {}
    for p in files:
        h = sha256(p)
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
        if h in seen:
            report["duplicates"].append({"file": rel, "same_as": seen[h]})
            continue
        seen[h] = rel
        entry = manifest["files"].get(h)
        if entry and entry.get("status") == "ingested" and not full:
            report["skipped_already_ingested"] += 1
            continue
        text, method = extract(p)
        txt_path = TEXT_DIR / f"{h[:12]}__{p.stem}.txt"
        if text and not dry:
            txt_path.write_text(text, encoding="utf-8")
        info = {
            "sha256": h, "path": rel, "class": classify(p, text), "language": guess_language(text),
            "extraction": method, "text_file": str(txt_path.relative_to(ROOT)) if text else None,
            "pages": int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(p)])).group(1))
            if p.suffix.lower() == ".pdf" else None,
            "modified": dt.datetime.fromtimestamp(p.stat().st_mtime).date().isoformat(),
        }
        if not text:
            report["needs_visual_read"].append(rel)
        report["new"].append(info)
        if not dry:
            prev = manifest["files"].get(h, {})
            manifest["files"][h] = {**info, "first_seen": prev.get("first_seen", dt.date.today().isoformat()),
                                    "status": prev.get("status", "extracted") if not full else "extracted"}
    if not dry:
        save_manifest(manifest)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
