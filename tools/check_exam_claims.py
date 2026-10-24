#!/usr/bin/env python3
"""Make sure official exam facts are sourced and consistent with the registry.

Any Markdown file that states exam logistics (pass mark, fee, item count) must
link to the registry or an official source, and must not contradict the registry.
"""
from __future__ import annotations

import re
import sys

from common import ROOT, Report, certifications, iter_markdown

FACT = re.compile(r"(?i)(scaled score|cut score|exam fee|\b720\b|\$\s?(?:99|125|175)\b)")
SOURCE = re.compile(r"registry\.yaml|anthropic-partners\.skilljar\.com|pearsonvue\.com/us/en/anthropic|exam-facts\.md")
# A phrase like "70 questions" next to a known exam code is a red flag.
ITEM_COUNT = re.compile(r"(?i)\b(CCAO-F|CCAR-P|CCAR-F|CCDV-F)\b[^.\n]{0,80}?\b(\d{2,3})\s+(?:items|questions)\b")


def check() -> Report:
    report = Report("exam claims")
    items = {c["code"]: c["format"]["items"] for c in certifications()}
    for md in iter_markdown():
        text = md.read_text(encoding="utf-8")
        rel = md.relative_to(ROOT)
        if "17-practice-questions" in rel.parts:
            continue
        if FACT.search(text) and not SOURCE.search(text):
            report.error(f"{rel}: states exam facts but does not link registry.yaml / exam-facts.md / official source")
        for code, n in ITEM_COUNT.findall(text):
            if int(n) != items.get(code) and int(n) >= 50:
                report.error(f"{rel}: says {code} has {n} items; registry says {items.get(code)}")
    return report


if __name__ == "__main__":
    r = check()
    r.print()
    sys.exit(0 if r.ok else 1)
