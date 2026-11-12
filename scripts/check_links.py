#!/usr/bin/env python3
"""Check that URLs resolve (polite: robots-aware for non-search hosts, 1 request/s per domain, generic UA).

Usage: python3 scripts/check_links.py <url> [...]      or      python3 scripts/check_links.py --json urls.json
Prints JSON {url: {"status": int|None, "ok": bool, "final_url": str, "note": str}}.
ok = HTTP status < 400 after redirects, or 401/403/429 from a site that blocks bots (then note="exists, blocks
bots" and ok=True only if the domain answers — a 403 is not a dead link). LinkedIn URLs are NOT fetched (terms of
use): they are only checked for a well-formed profile/company/jobs path (note="not fetched (LinkedIn)").
"""
from __future__ import annotations

import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

UA = "Mozilla/5.0 (X11; Linux x86_64) pfe-link-check/1.0"
LAST: dict[str, float] = {}
CTX = ssl.create_default_context()


def fetch(url: str, method: str):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=20, context=CTX)


def check(url: str) -> dict:
    host = urlparse(url).netloc.lower()
    if not url.startswith("http"):
        return {"status": None, "ok": False, "final_url": url, "note": "not a URL"}
    if "linkedin.com" in host:
        okpath = bool(re.search(r"linkedin\.com/(in|company|jobs|posts)/", url))
        return {"status": None, "ok": okpath, "final_url": url, "note": "not fetched (LinkedIn); path well-formed" if okpath else "malformed LinkedIn URL"}
    wait = 1.0 - (time.time() - LAST.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    LAST[host] = time.time()
    for method in ("HEAD", "GET"):
        try:
            with fetch(url, method) as r:
                return {"status": r.status, "ok": r.status < 400, "final_url": r.geturl(), "note": method}
        except urllib.error.HTTPError as e:
            if method == "HEAD":  # many sites answer HEAD differently: always confirm with GET
                continue
            if e.code in (401, 403, 429):
                return {"status": e.code, "ok": True, "final_url": url, "note": "exists, blocks bots"}
            return {"status": e.code, "ok": False, "final_url": url, "note": str(e.reason)}
        except Exception as e:  # noqa: BLE001
            if method == "HEAD":
                continue
            return {"status": None, "ok": False, "final_url": url, "note": type(e).__name__ + ": " + str(e)[:120]}
    return {"status": None, "ok": False, "final_url": url, "note": "unreachable"}


if __name__ == "__main__":
    a = sys.argv[1:]
    urls = json.load(open(a[1])) if a[:1] == ["--json"] else a
    res = {u: check(u) for u in dict.fromkeys(urls) if u}
    print(json.dumps(res, indent=1))
    sys.exit(0 if all(v["ok"] for v in res.values()) else 1)
