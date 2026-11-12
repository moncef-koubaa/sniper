#!/usr/bin/env python3
"""Helpers for /tailor-cv: split a library source.tex into blocks and reassemble it.

Library use:  from cv_blocks import load, save
  cv = load("resumes/library/process_en/source.tex")
  cv.summary = "..."                      # education summary paragraph
  cv.projects -> list of (title, body)    # body = the \\begin{bul}...\\end{bul} text
  cv.reorder_projects(["Prediction of", "Ethylene Oxide", ...])  # by title prefix; others dropped
  cv.add_project(title, [bullets], pos)   # new project from me.md facts
  cv.replace(old, new)                    # exact-text edit anywhere (raises if old not found)
  save(cv, "resumes/custom/<date>_<Co>/source.tex", header_comment)
"""
from __future__ import annotations

import re
from pathlib import Path

PROJ = re.compile(r"\\project\{(.+?)\}\n(\\begin\{bul\}.*?\\end\{bul\})", re.S)


class CV:
    def __init__(self, text: str):
        self.text = text

    @property
    def summary(self) -> str:
        return re.search(r"\\summary\{(.*?)\}\n", self.text, re.S).group(1)

    @summary.setter
    def summary(self, s: str) -> None:
        self.text = re.sub(r"\\summary\{.*?\}\n", lambda m: "\\summary{" + s + "}\n", self.text, count=1, flags=re.S)

    def _proj_section(self):
        m = re.search(r"(\\section\{(?:ACADEMIC PROJECTS|PROJETS ACADÉMIQUES)\}\n)(.*?)(\n\\section)", self.text, re.S)
        return m

    @property
    def projects(self) -> list[tuple[str, str]]:
        return PROJ.findall(self._proj_section().group(2))

    def _write_projects(self, projs):
        m = self._proj_section()
        body = "\n".join(f"\\project{{{t}}}\n{b}" for t, b in projs) + "\n"
        self.text = self.text[:m.start(2)] + body + self.text[m.end(2):]

    def reorder_projects(self, prefixes: list[str]) -> None:
        cur = self.projects
        out = []
        for p in prefixes:
            hit = [x for x in cur if x[0].startswith(p)]
            if not hit:
                raise KeyError(f"no project starting with {p!r}: {[t for t, _ in cur]}")
            out.append(hit[0])
        self._write_projects(out)

    def add_project(self, title: str, bullets: list[str], pos: int) -> None:
        cur = self.projects
        cur.insert(pos, (title, "\\begin{bul}\n" + "\n".join("\\item " + b for b in bullets) + "\n\\end{bul}"))
        self._write_projects(cur)

    def replace(self, old: str, new: str) -> None:
        if old not in self.text:
            raise KeyError(f"text not found: {old[:80]!r}")
        self.text = self.text.replace(old, new, 1)


def load(path: str) -> CV:
    return CV(Path(path).read_text())


def save(cv: CV, path: str, header: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    text = re.sub(r"\A(%.*\n)+", "", cv.text)
    p.write_text("".join(f"% {l}\n" for l in header.splitlines()) + text)
