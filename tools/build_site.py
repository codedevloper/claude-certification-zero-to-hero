#!/usr/bin/env python3
"""Build the GitHub Pages site with MkDocs + Material.

  pip install -r requirements-docs.txt
  python tools/build_site.py            # build into ./site
  python tools/build_site.py --serve    # live preview on http://127.0.0.1:8000

Steps: stage the learning content into .site/docs (Markdown pages, images, the browser
mock-exam app and site assets), generate the navigation from the folder structure, write
.site/mkdocs.yml (which inherits website/mkdocs.yml), then run MkDocs.

Environment (set by the Pages workflow; optional locally):
  SITE_URL   e.g. https://<user>.github.io/claude-certification-zero-to-hero/
  REPO_URL   e.g. https://github.com/<user>/claude-certification-zero-to-hero
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / ".site"
DOCS = STAGE / "docs"
WEBSITE = ROOT / "website"

# Folders whose Markdown is program input or tooling, not reading material.
SKIP_PARTS = {
    ".git", ".github", ".venv", "venv", ".site", "site", "website", "tools", "tests", "node_modules",
    "__pycache__", ".pytest_cache", ".claude", "data", "sample-project", "src", "examples",
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

GROUPS = [
    ("Start here", ["README.md", "00-getting-started", "GLOSSARY.md", "FAQ.md"]),
    ("Learn", [f"{n:02d}-" for n in range(1, 16)]),
    ("Certify", ["16-", "17-", "18-", "23-", "22-", "21-"]),
    ("Build", ["19-", "20-", "24-"]),
    ("About", ["25-", "ROADMAP.md", "PROGRESS.md", "CHANGELOG.md", "CONTRIBUTING.md",
               "CODE_OF_CONDUCT.md", "SECURITY.md", "docs"]),
]


def wanted(rel: Path) -> bool:
    return not SKIP_PARTS.intersection(rel.parts[:-1]) and rel.parts[0] not in SKIP_PARTS


def stage() -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    DOCS.mkdir(parents=True)
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if not path.is_file() or not wanted(rel):
            continue
        if path.suffix == ".md" or path.suffix.lower() in IMAGE_SUFFIXES:
            dest = DOCS / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
    # Interactive mock-exam app (static HTML/JS/JSON).
    shutil.copytree(ROOT / "18-mock-examinations" / "web", DOCS / "18-mock-examinations" / "web")
    index = DOCS / "18-mock-examinations" / "web" / "index.html"
    index.write_text(index.read_text(encoding="utf-8").replace("<body>", '<body data-site="pages">', 1), encoding="utf-8")
    shutil.copytree(WEBSITE / "assets", DOCS / "assets")


def h1(md: Path) -> str:
    for line in md.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#\s+(.+)", line)
        if m:
            return re.sub(r"[`*_]|<[^>]+>", "", m.group(1)).strip()
    return md.stem.replace("-", " ").title()


def natural(path: Path) -> list:
    """Sort '7-day' before '15-day' and 'lab-2' before 'lab-10'."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.name)]


def section(directory: Path):
    """Nav entry for a folder: README first, then pages, then sub-folders."""
    rel = directory.relative_to(DOCS).as_posix()
    readme = directory / "README.md"
    pages = sorted((p for p in directory.glob("*.md") if p.name != "README.md"), key=natural)
    subdirs = sorted((d for d in directory.iterdir() if d.is_dir() and any(d.rglob("*.md"))), key=natural)
    children: list = [f"{rel}/README.md"] if readme.exists() else []
    children += [p.relative_to(DOCS).as_posix() for p in pages]
    for sub in subdirs:
        entry = section(sub)
        if entry is not None:
            children.append(entry)
    if not children:
        return None
    if len(children) == 1 and isinstance(children[0], str):
        return children[0]  # e.g. a lab folder with only a README
    title = h1(readme) if readme.exists() else directory.name.replace("-", " ").title()
    return {title: children}


def build_nav() -> list:
    top = sorted(p.name for p in DOCS.iterdir())
    nav, used = [], set()
    for group, patterns in GROUPS:
        items = []
        for pattern in patterns:
            for name in top:
                if name in used or not (name == pattern or (pattern.endswith("-") and name.startswith(pattern))):
                    continue
                used.add(name)
                path = DOCS / name
                if path.is_dir():
                    entry = section(path)
                    if entry is not None:
                        items.append(entry)
                elif path.suffix == ".md":
                    items.append({"Home": name} if name == "README.md" else name)
        if items:
            nav.append({group: items})
    return nav


def repo_url() -> str:
    """REPO_URL from the environment, else derived from `git remote get-url origin`."""
    if os.environ.get("REPO_URL"):
        return os.environ["REPO_URL"].rstrip("/")
    try:
        remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True,
                                text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""
    remote = re.sub(r"^git@github\.com:", "https://github.com/", remote)
    return remote.removesuffix(".git")


def write_config() -> Path:
    config = {
        "INHERIT": "../website/mkdocs.yml",
        "docs_dir": "docs",
        "site_dir": "../site",
        "hooks": ["../website/hooks.py"],
        "theme": {"name": "material", "custom_dir": "../website/overrides"},
        "nav": build_nav(),
    }
    if os.environ.get("SITE_URL"):
        config["site_url"] = os.environ["SITE_URL"]
    url = repo_url()
    if url:
        config["repo_url"] = url
        config["edit_uri"] = "blob/main/"
    else:
        print("note: no REPO_URL or git remote; links to code files stay relative (use without --strict)")
    path = STAGE / "mkdocs.yml"
    path.write_text("# Generated by tools/build_site.py — do not edit.\n" + yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def main() -> int:
    stage()
    config = write_config()
    pages = sum(1 for _ in DOCS.rglob("*.md"))
    print(f"staged {pages} pages into {DOCS.relative_to(ROOT)}")
    cmd = [sys.executable, "-m", "mkdocs", "serve" if "--serve" in sys.argv else "build", "-f", str(config)]
    if "--strict" in sys.argv:
        cmd.append("--strict")
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
