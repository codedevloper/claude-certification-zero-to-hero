#!/usr/bin/env python3
"""Check external http(s) links in Markdown and question banks (needs network access).

CI uses lychee for this; this script is a dependency-free local equivalent.

  python tools/check_external_links.py            # check every unique URL
  python tools/check_external_links.py --list     # just list the URLs
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from check_links import strip_code
from common import QUESTIONS_DIR, Report, iter_markdown, question_files

URL = re.compile(r"https?://[^\s)<>\"'`\]]+")
SKIP = re.compile(r"api\.anthropic\.com/v1|localhost|127\.0\.0\.1|example\.(com|org)|\.example\b|\.test\b|\.internal\b|<|\{")
# Sites that reject automated requests but are known to be valid when visited in a browser.
SOFT_FAIL = {401, 403, 429}


def collect() -> dict[str, set[str]]:
    urls: dict[str, set[str]] = {}
    # Code blocks hold API endpoints and sample URLs, not links to visit.
    sources = [(p, strip_code(p.read_text(encoding="utf-8"))) for p in iter_markdown()]
    sources += [(p, json.dumps(json.loads(p.read_text(encoding="utf-8")))) for p in question_files()]
    for path, text in sources:
        for url in URL.findall(text):
            url = url.rstrip(".,;:*_")
            if not SKIP.search(url):
                urls.setdefault(url, set()).add(str(path.relative_to(QUESTIONS_DIR.parent)))
    return urls


def status(url: str) -> int:
    if urllib.parse.urlsplit(url).scheme not in {"http", "https"}:
        return 0  # never open file:, ftp: or custom schemes
    headers = {"User-Agent": "Mozilla/5.0 (link-check; claude-certification-zero-to-hero)"}
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            # Scheme is restricted to http/https above; URLs come from the repository's own docs.
            with urllib.request.urlopen(req, timeout=20) as resp:  # nosec B310  # noqa: S310
                return resp.status
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {403, 404, 405, 501}:
                continue  # some servers mishandle HEAD
            return exc.code
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if method == "GET":
                return 0
    return 0


def main() -> int:
    urls = collect()
    if "--list" in sys.argv:
        print("\n".join(sorted(urls)))
        return 0
    report = Report("external links")
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = dict(zip(urls, pool.map(status, urls)))
    for url, code in sorted(results.items()):
        where = ", ".join(sorted(urls[url])[:3])
        if code in SOFT_FAIL:
            report.warn(f"{code} {url} (bot-blocked? verify manually) — {where}")
        elif not 200 <= code < 400:
            report.error(f"{code or 'unreachable'} {url} — {where}")
    print(f"checked {len(urls)} unique external URLs")
    report.print()
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
