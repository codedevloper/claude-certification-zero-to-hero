"""Load the certification registry, question banks and fixed mock-exam forms."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "16-certification-tracks" / "registry.yaml"
QUESTIONS = REPO_ROOT / "17-practice-questions"
FORMS = REPO_ROOT / "18-mock-examinations" / "forms"


@dataclass(frozen=True)
class Question:
    id: str
    track: str
    domain: int
    objective: str
    type: str
    difficulty: str
    category: str
    scenario: str
    question: str
    options: dict[str, str]
    answer: tuple[str, ...]
    explanation: str
    why_incorrect: dict[str, str]
    module: str
    references: tuple[str, ...]
    select: int = 1

    @property
    def select_count(self) -> int:
        return len(self.answer)


@dataclass
class Track:
    code: str
    slug: str
    name: str
    items: int
    minutes: int
    domains: dict[int, dict]  # id -> {"name", "weight"}
    questions: list[Question] = field(default_factory=list)

    def by_id(self) -> dict[str, Question]:
        return {q.id: q for q in self.questions}


def _question(raw: dict, track: str, domain: int) -> Question:
    return Question(
        id=raw["id"], track=track, domain=domain, objective=raw["objective"], type=raw["type"],
        difficulty=raw["difficulty"], category=raw["category"], scenario=raw["scenario"],
        question=raw["question"], options=dict(sorted(raw["options"].items())),
        answer=tuple(sorted(raw["answer"])), explanation=raw["explanation"],
        why_incorrect=raw.get("why_incorrect", {}), module=raw.get("module", ""),
        references=tuple(raw.get("references", [])), select=raw.get("select", 1),
    )


def load_tracks(supported_only: bool = True) -> dict[str, Track]:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    tracks: dict[str, Track] = {}
    for cert in registry["certifications"]:
        if supported_only and cert.get("status") != "supported":
            continue
        track = Track(
            code=cert["code"], slug=cert["slug"], name=cert["name"],
            items=cert["format"]["items"], minutes=cert["format"]["minutes"],
            domains={d["id"]: {"name": d["name"], "weight": d["weight"]} for d in cert["domains"]},
        )
        for path in sorted((QUESTIONS / cert["slug"]).glob("*.json")):
            bank = json.loads(path.read_text(encoding="utf-8"))
            track.questions += [_question(q, bank["track"], bank["domain"]) for q in bank["questions"]]
        tracks[track.code] = track
    return tracks


def load_forms(track_slug: str | None = None) -> dict[str, dict]:
    """Fixed mock-exam forms: {form_id: {"track", "title", "minutes", "question_ids"}}."""
    forms = {}
    for path in sorted(FORMS.glob("*.json")):
        form = json.loads(path.read_text(encoding="utf-8"))
        if track_slug is None or form["track"].lower() == track_slug.lower():
            forms[form["id"]] = form
    return forms
