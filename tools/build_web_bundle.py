#!/usr/bin/env python3
"""Bundle the registry, question banks and forms into one JSON file for the browser mock-exam app.

  python tools/build_web_bundle.py           # write 18-mock-examinations/web/data/bank.json
  python tools/build_web_bundle.py --check   # fail if the bundle is stale (CI)
"""
from __future__ import annotations

import json
import sys

from common import ROOT, Report, certifications, load_questions

BUNDLE = ROOT / "18-mock-examinations" / "web" / "data" / "bank.json"
FORMS_DIR = ROOT / "18-mock-examinations" / "forms"


def build() -> str:
    tracks = []
    for cert in certifications("supported"):
        questions = [{k: v for k, v in q.items() if k != "_file"} for q in load_questions(cert["slug"])]
        forms = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(FORMS_DIR.glob(f"{cert['slug']}-form-*.json"))]
        tracks.append({
            "code": cert["code"],
            "name": cert["name"],
            "items": cert["format"]["items"],
            "minutes": cert["format"]["minutes"],
            "domains": [{"id": d["id"], "name": d["name"], "weight": d["weight"]} for d in cert["domains"]],
            "questions": questions,
            "forms": [{"id": f["id"], "title": f["title"], "minutes": f["minutes"], "question_ids": f["question_ids"]} for f in forms],
        })
    bundle = {
        "generated_by": "tools/build_web_bundle.py",
        "unofficial": True,
        "tracks": tracks,
    }
    return json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + "\n"


def main(check: bool) -> int:
    report = Report("web bundle")
    content = build()
    if check:
        if not BUNDLE.exists() or BUNDLE.read_text(encoding="utf-8") != content:
            report.error(f"{BUNDLE.relative_to(ROOT)} is stale — run python tools/build_web_bundle.py")
    else:
        BUNDLE.parent.mkdir(parents=True, exist_ok=True)
        BUNDLE.write_text(content, encoding="utf-8")
        print(f"wrote {BUNDLE.relative_to(ROOT)} ({len(content) // 1024} KB)")
    report.print()
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
