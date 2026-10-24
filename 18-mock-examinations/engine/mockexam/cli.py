"""Command-line mock examination.

Examples:
  python 18-mock-examinations/run_mock_exam.py                       # interactive menu
  python 18-mock-examinations/run_mock_exam.py --track CCAO-F --mode timed
  python 18-mock-examinations/run_mock_exam.py --track CCAR-P --mode learn --domain 3 --count 15
  python 18-mock-examinations/run_mock_exam.py --track CCAR-P --form ccar-p-form-1
  python 18-mock-examinations/run_mock_exam.py --track CCAO-F --weak  # retry what you missed
  python 18-mock-examinations/run_mock_exam.py --history
"""
from __future__ import annotations

import argparse
import random
import sys
import textwrap
import time
from typing import Callable

from . import progress
from .bank import Question, Track, load_forms, load_tracks
from .scoring import WEAK_THRESHOLD, Result, is_correct, parse_answer
from .selection import select_questions

DISCLAIMER = (
    "UNOFFICIAL PRACTICE. Questions are independently written and have never appeared on an "
    "Anthropic exam. Percent-correct here is not an Anthropic scaled score and does not predict "
    "an official result."
)
WIDTH = 92

InputFn = Callable[[str], str]


def wrap(text: str, indent: str = "") -> str:
    return "\n".join(
        textwrap.fill(p, WIDTH, initial_indent=indent, subsequent_indent=indent) for p in text.split("\n")
    )


def show_question(q: Question, n: int, total: int, out: Callable[[str], None]) -> None:
    out("")
    out("-" * WIDTH)
    out(f"Question {n}/{total}   [{q.id} · Domain {q.domain} · {q.difficulty}]")
    out(wrap(q.scenario))
    out("")
    out(wrap(q.question))
    if q.type == "multiple":
        out(f"(Choose {q.select_count}.)")
    for letter, text in q.options.items():
        out(wrap(f"{letter}. {text}", "  "))


def show_feedback(q: Question, given: tuple[str, ...] | None, out: Callable[[str], None]) -> None:
    ok = is_correct(q, given)
    out(f"\n{'Correct' if ok else 'Incorrect'} — answer: {', '.join(q.answer)}"
        + ("" if ok else f" (you chose: {', '.join(given) if given else 'nothing'})"))
    out(wrap(q.explanation, "  "))
    for letter, why in q.why_incorrect.items():
        out(wrap(f"{letter}: {why}", "    "))
    if q.module:
        out(f"  Study: {q.module}")
    if q.references:
        out(f"  Docs:  {q.references[0]}")


def ask(q: Question, prompt_in: InputFn, out: Callable[[str], None], allow_skip: bool) -> tuple[str, tuple[str, ...] | None]:
    """Return (action, answer). action is 'answer', 'skip' or 'quit'."""
    hint = "letter(s)" + (", s=skip" if allow_skip else "") + ", q=quit"
    while True:
        raw = prompt_in(f"Your answer ({hint}): ").strip()
        if raw.lower() in {"q", "quit"}:
            return "quit", None
        if allow_skip and raw.lower() in {"s", "skip"}:
            return "skip", None
        given = parse_answer(raw)
        if not given or not set(given) <= set(q.options):
            out(f"Please enter one of {', '.join(q.options)}.")
            continue
        if len(given) != q.select_count:
            out(f"Select exactly {q.select_count} option(s).")
            continue
        return "answer", given


def run_session(
    track: Track,
    questions: list[Question],
    mode: str,
    minutes: int | None,
    prompt_in: InputFn = input,
    out: Callable[[str], None] = print,
    clock: Callable[[], float] = time.monotonic,
) -> Result:
    responses: dict[str, tuple[str, ...] | None] = {q.id: None for q in questions}
    start = clock()
    deadline = start + minutes * 60 if minutes else None
    timed_out = False
    queue = list(enumerate(questions, 1))
    skipped: list[tuple[int, Question]] = []

    while queue:
        n, q = queue.pop(0)
        if deadline and clock() > deadline:
            timed_out = True
            out("\nTime is up. Unanswered questions are scored as incorrect.")
            break
        if deadline:
            remaining = int(deadline - clock())
            out(f"\n[time remaining {remaining // 60:02d}:{remaining % 60:02d}]")
        show_question(q, n, len(questions), out)
        action, given = ask(q, prompt_in, out, allow_skip=(mode == "timed"))
        if deadline and clock() > deadline:
            # The answer arrived after time ran out: like the real exam, it does not count.
            timed_out = True
            out("\nTime is up. That answer was not recorded; unanswered questions are scored as incorrect.")
            break
        if action == "quit":
            out("\nEnding the session early; unanswered questions count as incorrect.")
            break
        if action == "skip":
            skipped.append((n, q))
        else:
            responses[q.id] = given
            if mode == "learn":
                show_feedback(q, given, out)
        if not queue and skipped:
            out(f"\nReturning to {len(skipped)} skipped question(s).")
            queue, skipped = skipped, []

    return Result(track, questions, responses, clock() - start, timed_out)


def print_report(result: Result, mode: str, out: Callable[[str], None] = print) -> None:
    out("\n" + "=" * WIDTH)
    out(f"{result.track.name} ({result.track.code}) — {mode} practice result")
    out("=" * WIDTH)
    mins, secs = divmod(int(result.elapsed_seconds), 60)
    out(f"Score: {result.correct}/{result.total} correct ({result.percent:.1f}%)   time {mins}m {secs:02d}s"
        + ("   (time expired)" if result.timed_out else ""))
    out("\nBy domain:")
    for d, (c, t) in result.domain_scores.items():
        pct = result.domain_percent(d)
        bar = "#" * int(pct / 5)
        flag = "  <- review" if pct < WEAK_THRESHOLD else ""
        out(f"  D{d} {result.track.domains[d]['name'][:44]:44} {c:>3}/{t:<3} {pct:5.1f}% {bar}{flag}")
    weak = result.weak_domains()
    if weak:
        out("\nWeak areas (below {:.0f}%): ".format(WEAK_THRESHOLD)
            + ", ".join(f"D{d} {result.track.domains[d]['name']}" for d in weak))
    recs = result.recommendations()
    if recs:
        out("\nRecommended study, most-missed first:")
        for m in recs:
            out(f"  - {m}")
    if mode == "timed" and result.missed():
        out("\nReview of missed questions:")
        for q in result.missed():
            out(f"\n{q.id}: {wrap(q.question)}")
            show_feedback(q, result.responses.get(q.id), out)
    out("\n" + wrap(DISCLAIMER))


def print_history(out: Callable[[str], None] = print) -> None:
    data = progress.load()
    attempts = data["attempts"]
    if not attempts:
        out("No attempts recorded yet.")
        return
    out(f"Progress file: {progress.progress_path()}")
    for a in attempts[-20:]:
        out(f"  {a['finished_at']}  {a['track']:7} {a['mode']:6} {a['correct']:>3}/{a['total']:<3} {a['percent']:5.1f}%")
    out(f"Questions answered wrongly last time: {len(progress.weak_question_ids(data))}")


def choose(prompt: str, options: list[str], prompt_in: InputFn, out: Callable[[str], None]) -> str:
    for i, opt in enumerate(options, 1):
        out(f"  {i}. {opt}")
    while True:
        raw = prompt_in(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        out(f"Enter a number from 1 to {len(options)}.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Unofficial Claude certification mock exams (local, offline).")
    p.add_argument("--track", help="Certification code, e.g. CCAO-F or CCAR-P")
    p.add_argument("--mode", choices=["timed", "learn"], help="timed = exam conditions; learn = instant feedback")
    p.add_argument("--count", type=int, help="Number of questions (default: official item count for timed, 20 for learn)")
    p.add_argument("--minutes", type=int, help="Time limit for timed mode (default: scaled from the official limit)")
    p.add_argument("--domain", type=int, help="Practise a single domain")
    p.add_argument("--form", help="Use a fixed mock-exam form, e.g. ccao-f-form-1")
    p.add_argument("--weak", action="store_true", help="Prioritise questions you previously got wrong")
    p.add_argument("--seed", type=int, help="Random seed for a reproducible selection")
    p.add_argument("--history", action="store_true", help="Show past attempts and exit")
    p.add_argument("--reset-progress", action="store_true", help="Delete local progress and exit")
    p.add_argument("--no-save", action="store_true", help="Do not record this attempt")
    return p


def main(argv: list[str] | None = None, prompt_in: InputFn = input, out: Callable[[str], None] = print) -> int:
    args = build_parser().parse_args(argv)
    if args.reset_progress:
        progress.reset()
        out("Progress deleted.")
        return 0
    if args.history:
        print_history(out)
        return 0

    if args.count is not None and args.count < 1:
        out("--count must be at least 1.")
        return 2
    if args.minutes is not None and args.minutes < 1:
        out("--minutes must be at least 1.")
        return 2

    tracks = load_tracks()
    out(wrap(DISCLAIMER) + "\n")
    code = (args.track or "").upper() or choose("Select a certification: ", sorted(tracks), prompt_in, out)
    if code not in tracks:
        out(f"Unknown or unsupported track {code!r}. Available: {', '.join(sorted(tracks))}")
        return 2
    track = tracks[code]
    if not track.questions:
        out(f"No questions found for {code}.")
        return 2
    mode = args.mode or choose("Select a mode: ", ["timed", "learn"], prompt_in, out)
    data = progress.load()
    rng = random.Random(args.seed)

    if args.form:
        forms = load_forms(track.slug)
        if args.form not in forms:
            out(f"Unknown form {args.form!r}. Available: {', '.join(forms) or 'none'}")
            return 2
        lookup = track.by_id()
        questions = [lookup[qid] for qid in forms[args.form]["question_ids"] if qid in lookup]
        rng.shuffle(questions)
        minutes = args.minutes or forms[args.form].get("minutes", track.minutes)
    else:
        default = track.items if mode == "timed" else 20
        count = args.count or default
        if args.domain is not None and args.domain not in track.domains:
            out(f"Unknown domain {args.domain} for {code}. Valid domains: {', '.join(map(str, sorted(track.domains)))}")
            return 2
        weak = progress.weak_question_ids(data) if args.weak else None
        questions = select_questions(track, count, rng, args.domain, weak)
        # Keep the official pace (minutes per item) when the session is shorter.
        minutes = args.minutes or max(1, round(track.minutes * len(questions) / track.items))
    if mode == "learn":
        minutes = None

    out(f"\n{track.name}: {len(questions)} questions, "
        + (f"{minutes} minutes" if minutes else "untimed learning mode") + ".")
    result = run_session(track, questions, mode, minutes, prompt_in, out)
    print_report(result, mode, out)
    if not args.no_save and result.total:
        answered = {q.id: is_correct(q, result.responses.get(q.id)) for q in questions
                    if result.responses.get(q.id) is not None or mode == "timed"}
        progress.save(progress.record(data, result.to_record(mode), answered))
        out(f"\nSaved to {progress.progress_path()} (no personal data stored).")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
