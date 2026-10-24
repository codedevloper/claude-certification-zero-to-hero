#!/usr/bin/env python3
"""Keep a consistent "Previous · Module overview · Next" footer on every numbered module page.

GitHub readers have no site navigation, so each page in modules 01–15 ends with a generated
footer between page-nav markers. The website hides it (MkDocs has its own footer).

  python tools/build_page_nav.py           # write or refresh footers
  python tools/build_page_nav.py --check   # fail if any footer is missing or stale (CI)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from common import ROOT, Report

START, END = "<!-- page-nav:start -->", "<!-- page-nav:end -->"
BLOCK = re.compile(r"\n*" + re.escape(START) + r".*?" + re.escape(END) + r"\n*", re.DOTALL)
LINK = r"\[[^\]]+\]\([^)]+\)"
# Hand-written navigation lines that the generated footer replaces. Lines that add advice
# (for example "Next: [...]. Practise in [...]") are left alone.
OLD_NAV = re.compile(
    rf"^- (?:Previous: {LINK}(?: · (?:Next|Next module|Back to(?: the)?):? ?{LINK})?"
    rf"|Next page: {LINK}|Next: {LINK}\.?|Next module: {LINK})\s*$",
    re.MULTILINE,
)
FIRST, LAST = 1, 15


def title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return re.sub(r"[`*_]", "", line[2:]).strip()
    return path.stem


def modules() -> list[Path]:
    return sorted(d for d in ROOT.iterdir() if d.is_dir() and re.match(r"\d\d-", d.name) and FIRST <= int(d.name[:2]) <= LAST)


def footer(prev: tuple[str, str], nxt: tuple[str, str], next_is_module: bool) -> str:
    next_label = "Next module" if next_is_module else "Next"
    parts = [] if prev[0] == "README.md" else [f"[← Previous: {prev[1]}]({prev[0]})"]
    parts += ["[Module overview](README.md)", f"[{next_label}: {nxt[1]} →]({nxt[0]})"]
    return f"{START}\n---\n\n" + " · ".join(parts) + f"\n{END}\n"


def plan() -> dict[Path, str]:
    """Map each numbered page to the full text it should have."""
    mods = modules()
    wanted: dict[Path, str] = {}
    for i, mod in enumerate(mods):
        pages = sorted(mod.glob("[0-9][0-9]-*.md"))
        nxt_mod = mods[i + 1] if i + 1 < len(mods) else ROOT / "16-certification-tracks"
        for j, page in enumerate(pages):
            prev = (pages[j - 1].name, title(pages[j - 1])) if j else ("README.md", title(mod / "README.md"))
            if j + 1 < len(pages):
                nxt, is_mod = (pages[j + 1].name, title(pages[j + 1])), False
            else:
                nxt, is_mod = (f"../{nxt_mod.name}/README.md", title(nxt_mod / "README.md")), True
            body = BLOCK.sub("\n", page.read_text(encoding="utf-8"))
            body = OLD_NAV.sub("", body).rstrip() + "\n"
            wanted[page] = body + "\n" + footer(prev, nxt, is_mod)
    return wanted


def main(check: bool) -> int:
    report = Report("page navigation footers")
    for page, text in plan().items():
        if page.read_text(encoding="utf-8") != text:
            if check:
                report.error(f"{page.relative_to(ROOT)}: footer missing or stale; run python tools/build_page_nav.py")
            else:
                page.write_text(text, encoding="utf-8")
    report.print()
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
