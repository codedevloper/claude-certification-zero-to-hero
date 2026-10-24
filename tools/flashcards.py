#!/usr/bin/env python3
"""Validate flashcard decks and optionally export them as Anki-importable CSV.

  python tools/flashcards.py                 # validate
  python tools/flashcards.py --export out/   # validate, then write <deck>.csv files
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import yaml

from common import FLASHCARDS_DIR, ROOT, Report, objective_index


def decks() -> list[Path]:
    return sorted((FLASHCARDS_DIR / "decks").glob("*.yaml"))


def validate() -> tuple[Report, dict[Path, dict]]:
    report = Report("flashcards")
    objectives = objective_index()
    seen: set[str] = set()
    loaded: dict[Path, dict] = {}
    for path in decks():
        rel = path.relative_to(ROOT)
        deck = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        loaded[path] = deck
        for key in ("deck", "title", "cards"):
            if key not in deck:
                report.error(f"{rel}: missing top-level '{key}'")
        for card in deck.get("cards", []):
            cid = card.get("id", "<missing>")
            if cid in seen:
                report.error(f"{rel}: duplicate card id {cid}")
            seen.add(cid)
            for key in ("front", "back"):
                if not str(card.get(key, "")).strip():
                    report.error(f"{rel} {cid}: empty '{key}'")
            if card.get("objective") and card["objective"] not in objectives:
                report.error(f"{rel} {cid}: unknown objective {card['objective']}")
            if card.get("module") and not (ROOT / card["module"].split("#")[0]).exists():
                report.error(f"{rel} {cid}: module path does not exist: {card['module']}")
    if not seen:
        report.error("no flashcards found")
    print(f"checked {len(seen)} flashcards in {len(loaded)} deck(s)")
    return report, loaded


def export(loaded: dict[Path, dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for path, deck in loaded.items():
        target = out_dir / f"{path.stem}.csv"
        with target.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            for card in deck.get("cards", []):
                writer.writerow([card["front"], card["back"], f"{deck['deck']} {card.get('objective', '')}".strip()])
        print(f"wrote {target}")


if __name__ == "__main__":
    r, data = validate()
    r.print()
    if r.ok and "--export" in sys.argv:
        export(data, Path(sys.argv[sys.argv.index("--export") + 1]))
    sys.exit(0 if r.ok else 1)
