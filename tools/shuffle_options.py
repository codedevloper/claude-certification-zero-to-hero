#!/usr/bin/env python3
"""Give every practice question a fair, reproducible answer order.

Options are permuted per question with a seed derived from the question ID, then the
`answer` and `why_incorrect` keys are remapped. Questions whose text refers to options by
letter are left alone (and reported), because shuffling would make those references wrong.

  python tools/shuffle_options.py            # shuffle every bank in place
  python tools/shuffle_options.py --check    # report position balance only
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys

from common import ROOT, question_files
from validate_questions import cueing_stats

LETTER_REF = re.compile(r"\b(?i:options?|answers?|choices?)\s+\(?[A-F]\b|\(([A-F])\)|^[A-F][.:)]", re.MULTILINE)
SALT = "claude-cert-zero-to-hero/v1"


def refers_to_letters(q: dict) -> bool:
    texts = [q["scenario"], q["question"], q["explanation"], *q["options"].values(), *q["why_incorrect"].values()]
    return any(LETTER_REF.search(t) for t in texts)


def shuffle(q: dict) -> dict:
    letters = sorted(q["options"])
    seed = int(hashlib.sha256(f"{SALT}:{q['id']}".encode()).hexdigest(), 16)
    order = letters[:]
    random.Random(seed).shuffle(order)          # order[i] = old letter that moves to position letters[i]
    new_of = {old: letters[i] for i, old in enumerate(order)}
    q["options"] = {new_of[old]: q["options"][old] for old in order}
    q["answer"] = sorted(new_of[a] for a in q["answer"])
    q["why_incorrect"] = {new_of[k]: v for k, v in sorted(q["why_incorrect"].items(), key=lambda kv: new_of[kv[0]])}
    return q


def main(check: bool) -> int:
    skipped = []
    by_track: dict[str, list[dict]] = {}
    for path in question_files():
        bank = json.loads(path.read_text(encoding="utf-8"))
        for q in bank["questions"]:
            if not check:
                if refers_to_letters(q):
                    skipped.append(q["id"])
                else:
                    shuffle(q)
        by_track.setdefault(bank["track"], []).extend(bank["questions"])
        if not check:
            path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for track, qs in sorted(by_track.items()):
        stats = cueing_stats(qs)
        pos = ", ".join(f"{k}={o}/{e}" for k, (o, e) in stats["positions"].items())
        print(f"{track}: longest-option key rate {stats['longest_rate']:.0%}; keys by position (observed/expected): {pos}")
    if skipped:
        print("left unshuffled (text refers to option letters):", ", ".join(skipped))
    print(f"{'checked' if check else 'shuffled'} {sum(len(v) for v in by_track.values())} questions in {ROOT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
