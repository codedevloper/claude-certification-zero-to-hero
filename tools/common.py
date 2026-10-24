"""Shared helpers for repository tooling.

All tools are dependency-light: PyYAML is required, jsonschema is optional
(schema validation is skipped with a warning if it is not installed).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "16-certification-tracks" / "registry.yaml"
QUESTIONS_DIR = ROOT / "17-practice-questions"
SCHEMA_PATH = QUESTIONS_DIR / "schema" / "question-bank.schema.json"
FLASHCARDS_DIR = ROOT / "23-flashcards"
LABS_DIR = ROOT / "19-hands-on-labs"

# Directories never scanned by content checks.
EXCLUDED_DIRS = {".git", ".venv", "venv", ".site", "site", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache"}


def load_registry() -> dict:
    with REGISTRY_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def certifications(status: str | None = None) -> list[dict]:
    certs = load_registry()["certifications"]
    return [c for c in certs if status is None or c.get("status") == status]


def objective_index() -> dict[str, dict]:
    """Map objective ID -> {track, domain, text}."""
    index: dict[str, dict] = {}
    for cert in certifications():
        for dom in cert["domains"]:
            for obj in dom.get("objectives", []):
                index[obj["id"]] = {"track": cert["code"], "domain": dom["id"], "text": obj["text"]}
    return index


def question_files(slug: str | None = None) -> list[Path]:
    pattern = f"{slug}/*.json" if slug else "*/*.json"
    return sorted(p for p in QUESTIONS_DIR.glob(pattern) if p.parent.name != "schema")


def load_questions(slug: str | None = None) -> list[dict]:
    """Return every question, each annotated with `track`, `domain` and `_file`."""
    out: list[dict] = []
    for path in question_files(slug):
        bank = json.loads(path.read_text(encoding="utf-8"))
        for q in bank.get("questions", []):
            out.append({**q, "track": bank["track"], "domain": bank["domain"], "_file": str(path.relative_to(ROOT))})
    return out


def iter_markdown() -> Iterator[Path]:
    for path in ROOT.rglob("*.md"):
        if not EXCLUDED_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def iter_text_files() -> Iterator[Path]:
    suffixes = {".md", ".py", ".js", ".json", ".yaml", ".yml", ".toml", ".txt", ".html", ".css", ".sh", ".example", ".cfg", ".ini"}
    for path in ROOT.rglob("*"):
        if path.is_file() and not EXCLUDED_DIRS.intersection(path.relative_to(ROOT).parts):
            if path.suffix in suffixes or path.name.startswith(".env"):
                yield path


@dataclass
class Report:
    name: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def print(self) -> None:
        status = "FAIL" if self.errors else "OK"
        print(f"[{status}] {self.name}: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        for e in self.errors:
            print(f"  ERROR  {e}")
        for w in self.warnings:
            print(f"  warn   {w}")

    @property
    def ok(self) -> bool:
        return not self.errors
