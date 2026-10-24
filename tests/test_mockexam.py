"""Unit and integration tests for the mock-exam engine."""
import itertools
import random

import pytest

from mockexam import progress
from mockexam.bank import Question, Track, load_forms, load_tracks
from mockexam.cli import main, run_session
from mockexam.scoring import Result, is_correct, parse_answer
from mockexam.selection import allocate, select_questions


def make_q(qid, domain, answer=("A",), qtype="single"):
    return Question(
        id=qid, track="TEST-X", domain=domain, objective=f"TEST-X-{domain}.1", type=qtype, difficulty="foundation",
        category="concept", scenario="A synthetic scenario for testing.", question="Pick one?",
        options={"A": "a", "B": "b", "C": "c", "D": "d"}, answer=tuple(answer), explanation="Because A.",
        why_incorrect={}, module="00-getting-started/README.md", references=("https://example.com",),
        select=len(answer),
    )


@pytest.fixture
def track():
    t = Track(code="TEST-X", slug="test-x", name="Test", items=10, minutes=20,
              domains={1: {"name": "One", "weight": 70}, 2: {"name": "Two", "weight": 30}})
    t.questions = [make_q(f"TEST-X-D1-{i:03}", 1) for i in range(20)] + [make_q(f"TEST-X-D2-{i:03}", 2) for i in range(20)]
    return t


def test_allocate_is_exact_and_proportional():
    alloc = allocate({1: 14, 2: 21, 3: 12, 4: 16, 5: 12, 6: 15, 7: 10}, 60)
    assert sum(alloc.values()) == 60
    assert alloc[2] == max(alloc.values())


def test_select_respects_blueprint(track):
    qs = select_questions(track, 10, random.Random(1))
    assert len(qs) == 10 and len({q.id for q in qs}) == 10
    assert sum(q.domain == 1 for q in qs) == 7


def test_select_single_domain_and_weak_first(track):
    weak = {"TEST-X-D2-005"}
    qs = select_questions(track, 5, random.Random(2), domain=2, weak_ids=weak)
    assert all(q.domain == 2 for q in qs)
    assert qs[0].id == "TEST-X-D2-005"


def test_select_caps_at_pool_size(track):
    assert len(select_questions(track, 999, random.Random(3))) == 40


def test_parse_and_correctness():
    q = make_q("TEST-X-D1-999", 1, answer=("A", "C"), qtype="multiple")
    assert parse_answer("c, a") == ("A", "C")
    assert is_correct(q, ("A", "C"))
    assert not is_correct(q, ("A",))  # all-or-nothing
    assert not is_correct(q, None)


def test_result_breakdown_and_recommendations(track):
    qs = track.questions[:3] + track.questions[20:22]
    responses = {q.id: ("A",) for q in qs}
    responses[qs[0].id] = ("B",)
    r = Result(track, qs, responses, 60.0)
    assert (r.correct, r.total) == (4, 5)
    assert r.domain_scores == {1: (2, 3), 2: (2, 2)}
    assert r.weak_domains() == [1]
    assert r.recommendations() == ["00-getting-started/README.md"]


def test_progress_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("MOCKEXAM_PROGRESS", str(tmp_path / "p.json"))
    data = progress.load()
    progress.save(progress.record(data, {"track": "T", "mode": "learn", "total": 2, "correct": 1, "percent": 50.0}, {"a": True, "b": False}))
    again = progress.load()
    assert len(again["attempts"]) == 1
    assert progress.weak_question_ids(again) == {"b"}
    progress.reset()
    assert progress.load()["attempts"] == []


def test_run_session_learn_mode_scripted(track):
    qs = track.questions[:3]
    answers = iter(["A", "b", "A"])
    out = []
    result = run_session(track, qs, "learn", None, prompt_in=lambda _: next(answers), out=out.append)
    assert result.correct == 2
    assert any("Incorrect" in line for line in out)


def test_run_session_timed_skip_and_timeout(track):
    qs = track.questions[:3]
    answers = iter(["s", "A", "A", "A"])
    clock = iter([0, 0, 0, 0, 0, 0, 0, 9999, 9999, 9999])
    result = run_session(track, qs, "timed", 1, prompt_in=lambda _: next(answers), out=lambda _: None,
                         clock=lambda: next(clock))
    assert result.timed_out
    assert result.total == 3


def test_real_banks_load_and_cli_runs(tmp_path, monkeypatch):
    tracks = load_tracks()
    if not any(t.questions for t in tracks.values()):
        pytest.skip("question banks not present yet")
    monkeypatch.setenv("MOCKEXAM_PROGRESS", str(tmp_path / "p.json"))
    code = next(c for c, t in tracks.items() if t.questions)
    out = []
    # Cycle answer sizes so multiple-response items eventually get a valid number of selections.
    answers = itertools.cycle(["A", "A,B", "A,B,C"])
    rc = main(["--track", code, "--mode", "learn", "--count", "3", "--seed", "7"],
              prompt_in=lambda _: next(answers), out=out.append)
    assert rc == 0
    assert any("Score:" in line for line in out)


def test_forms_reference_existing_questions():
    tracks = load_tracks()
    for t in tracks.values():
        ids = set(t.by_id())
        for form in load_forms(t.slug).values():
            assert set(form["question_ids"]) <= ids, form["id"]
