#!/usr/bin/env python3
"""Check that every relative Markdown link points at a file (and heading) that exists.

External http(s) links are checked separately in CI by lychee, because they need
network access and are prone to transient failures.
"""
from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote

from common import ROOT, Report, iter_markdown

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^(```|~~~)")
HEADING = re.compile(r"^#{1,6}\s+(.*)$")


def slugify(text: str) -> str:
    """GitHub-style heading anchor."""
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


@lru_cache(maxsize=None)
def anchors(path: Path) -> set[str]:
    found: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        m = HEADING.match(line)
        if m and not in_fence:
            slug = slugify(m.group(1))
            n = counts.get(slug, 0)
            found.add(slug if n == 0 else f"{slug}-{n}")
            counts[slug] = n + 1
    found.update(re.findall(r'<a\s+(?:name|id)="([^"]+)"', path.read_text(encoding="utf-8")))
    return found


def strip_code(text: str) -> str:
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


def check() -> Report:
    report = Report("internal links")
    count = 0
    for md in iter_markdown():
        text = strip_code(md.read_text(encoding="utf-8"))
        for m in LINK.finditer(text):
            target = m.group(1) or m.group(2)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):  # http:, mailto:, etc.
                continue
            count += 1
            path_part, _, frag = target.partition("#")
            dest = md if not path_part else (md.parent / unquote(path_part)).resolve()
            rel = md.relative_to(ROOT)
            if not dest.exists():
                report.error(f"{rel}: broken link -> {target}")
                continue
            try:
                dest.relative_to(ROOT)
            except ValueError:
                report.error(f"{rel}: link escapes repository -> {target}")
                continue
            if frag and dest.suffix == ".md" and frag.lower() not in anchors(dest):
                report.error(f"{rel}: missing anchor #{frag} in {dest.relative_to(ROOT)}")
    print(f"checked {count} internal links")
    return report


if __name__ == "__main__":
    r = check()
    r.print()
    sys.exit(0 if r.ok else 1)
