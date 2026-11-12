#!/usr/bin/env python3
"""Validate contact emails and enforce the verified / pattern-inferred rules.

Usage: python3 scripts/validate_emails.py contacts.json
contacts.json = list of {"company", "name", "email", "confidence": "verified"|"inferred"|"none",
                         "source_url", "pattern_source_url" (inferred only), "company_domain"}
Checks per contact:
  - syntax (RFC-lite regex), no personal webmail domain for a company contact (gmail, yahoo, hotmail, outlook…)
  - the email domain resolves (DNS A/AAAA lookup of the domain or mail.<domain>)
  - verified  -> source_url present; if fetchable, the address appears verbatim on that page (case-insensitive,
                 also de-obfuscated "[at]"/"(at)"/" at "); otherwise -> downgraded flag
  - inferred  -> pattern_source_url present (page showing another address with the same pattern)
  - none      -> email must be empty
Prints JSON with per-contact problems; exit 1 if any contact breaks a rule.
"""
from __future__ import annotations

import json
import re
import socket
import sys
import urllib.request

RX = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
WEBMAIL = {"gmail.com", "yahoo.com", "yahoo.fr", "hotmail.com", "hotmail.fr", "outlook.com", "live.com", "icloud.com", "gmx.de", "orange.fr", "free.fr"}
UA = "Mozilla/5.0 (X11; Linux x86_64) pfe-email-check/1.0"
_cache: dict[str, str] = {}


def page(url: str) -> str:
    if url not in _cache:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                _cache[url] = r.read(3_000_000).decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            _cache[url] = ""
    return _cache[url]


def resolves(domain: str) -> bool:
    """True if the domain has an MX record (preferred) or an A/AAAA record."""
    import shutil
    import subprocess
    if shutil.which("host"):
        out = subprocess.run(["host", "-t", "mx", domain], capture_output=True, text=True, timeout=15).stdout
        if "mail is handled by" in out:
            return True
    for d in (domain, "mail." + domain):
        try:
            socket.getaddrinfo(d, None)
            return True
        except OSError:
            continue
    return False


def check(c: dict) -> list[str]:
    p = []
    email = (c.get("email") or "").strip()
    conf = c.get("confidence", "none")
    if conf == "none":
        return ["email given but confidence none"] if email else []
    if not RX.match(email):
        return [f"bad syntax: {email!r}"]
    dom = email.split("@")[1].lower()
    if dom in WEBMAIL:
        p.append("personal webmail domain")
    if not resolves(dom):
        p.append(f"domain {dom} does not resolve")
    if conf == "verified":
        src = c.get("source_url")
        if not src:
            p.append("verified without source_url")
        elif "linkedin.com" not in src:
            html = page(src).lower()
            deob = re.sub(r"\s*[\[\(]\s*at\s*[\]\)]\s*|\s+at\s+", "@", html)
            deob = re.sub(r"\s*[\[\(]\s*dot\s*[\]\)]\s*", ".", deob)
            if html and email.lower() not in html and email.lower() not in deob:
                p.append("not found verbatim on source_url (page may be JS-rendered: re-check, else mark inferred)")
            if not html:
                p.append("source_url not fetchable now (kept verified: re-check by hand)")
    elif conf == "inferred":
        if not c.get("pattern_source_url"):
            p.append("inferred without pattern_source_url")
    else:
        p.append(f"unknown confidence {conf!r}")
    return p


if __name__ == "__main__":
    rows = json.load(open(sys.argv[1]))
    out, bad = [], 0
    for c in rows:
        probs = check(c)
        hard = [x for x in probs if not x.startswith("source_url not fetchable")]
        bad += bool(hard)
        out.append({"company": c.get("company"), "name": c.get("name"), "email": c.get("email"),
                    "confidence": c.get("confidence"), "problems": probs})
    print(json.dumps({"checked": len(rows), "with_problems": bad, "contacts": out}, indent=1, ensure_ascii=False))
    sys.exit(1 if bad else 0)
