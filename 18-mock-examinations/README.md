# 18 · Mock Examinations

A lightweight, local mock-exam engine. It has two front ends that share one question bank:

| | Terminal (Python) | Browser (static web page) |
|---|---|---|
| Install | Python 3.10+ and PyYAML | Any modern browser and Python, to serve files locally |
| Progress | `~/.claude-cert-zero-to-hero/progress.json` | This browser's `localStorage` |
| Best for | Keyboard-driven drills and scripting | A closer feel to an exam interface |

Neither needs an account, an API key, a database, a paid service or a network connection, and neither collects
personal information.

> **Read this first.** Every question is unofficial and was written independently. Your percent-correct is **not** an
> Anthropic scaled score. Official exams report 100–1,000 with a cut score of 720 ([exam facts](../25-official-resources/exam-facts.md)),
> and the scaling method is not public. Treat these results as a study signal, not a prediction.

## Features

- Certification selection (every track marked `supported` in the [registry](../16-certification-tracks/registry.yaml))
- **Timed mode:** exam conditions, with a countdown, no feedback until the end, skip-and-return, and a review of misses
- **Learning mode:** untimed, with an explanation after every question
- Blueprint-weighted random selection, or single-domain practice
- Fixed full-length and half-length **forms** (see [`forms/`](forms/)) for repeatable mock exams
- Automatic scoring with a domain-by-domain breakdown and weak-area flags (below 70%)
- Study recommendations that link the modules behind the questions you missed
- Local history, retry-missed-questions, and restart or reset

## Option 1: Terminal

```bash
# from the repository root
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt          # only PyYAML is needed to run the engine

python 18-mock-examinations/run_mock_exam.py                     # interactive menu
python 18-mock-examinations/run_mock_exam.py --track CCAO-F --mode timed
python 18-mock-examinations/run_mock_exam.py --track CCAR-P --mode learn --domain 3 --count 15
python 18-mock-examinations/run_mock_exam.py --track CCAR-P --form ccar-p-form-1
python 18-mock-examinations/run_mock_exam.py --track CCAO-F --mode learn --weak   # missed questions first
python 18-mock-examinations/run_mock_exam.py --history
python 18-mock-examinations/run_mock_exam.py --reset-progress
```

| Option | Meaning |
|---|---|
| `--track` | `CCAO-F` or `CCAR-P` |
| `--mode` | `timed` or `learn` |
| `--count` | Number of questions (default: the official item count when timed, 20 when learning) |
| `--minutes` | Override the time limit (default keeps the official pace, minutes per item) |
| `--domain N` | Practise one domain |
| `--form ID` | Use a fixed form, e.g. `ccao-f-form-1`, `ccar-p-form-3` |
| `--weak` | Put questions you answered wrongly last time first |
| `--seed N` | Reproducible selection |
| `--no-save` | Don't record the attempt |

While answering, type a letter (`B`) or several letters (`A,C`). In timed mode `s` skips and `q` ends the session.
Set `MOCKEXAM_PROGRESS=/path/file.json` to store progress somewhere else.

## Option 2: Browser

```bash
python tools/build_web_bundle.py        # refresh web/data/bank.json after any question change
python3 -m http.server 8000             # run from the repository root
```

Open <http://localhost:8000/18-mock-examinations/web/>. The page is plain HTML, CSS and JavaScript with a strict
Content Security Policy. It makes no external requests and renders all question text as text, never as HTML.

## How scoring works

- Each question scores 1 if your selection exactly matches the key, otherwise 0. **Multiple-response items are
  all-or-nothing.** That is this tool's assumption; the official guides do not say whether partial credit exists.
- Domain percentages use the questions drawn from that domain in the session. With small samples, read them as
  directional only.
- A domain below 70% is flagged for review. That threshold is a study heuristic, not an official pass mark.

## Forms

`forms/<slug>-form-1.json` and `-form-2.json` are full-length (60 items for CCAO-F and CCAR-F, 63 for CCAR-P, 120 minutes).
**Forms 1 and 2 share no questions**, so taking both gives two genuinely independent attempts. `-form-3.json` is a
half-length checkpoint drawn from the same bank, so it repeats questions you will meet in forms 1 and 2: take it
first, as a warm-up, rather than as a final readiness check. Regenerate the forms with
`python tools/build_mock_forms.py` after adding many questions.

**CCAR-F forms follow the real exam's structure:** each one presents 4 of the 6 published scenarios (listed in the
form's `scenarios` field), with an equal share of questions per scenario. Forms 1 and 2 together cover all six.

A suggested sequence: domain drills in learning mode, then form 3 as a checkpoint, then form 1 under timed
conditions, then remediation of weak domains, then form 2.

## Tests

```bash
python -m pytest tests -q
```

`tests/test_mockexam.py` covers selection (blueprint allocation, domain filters, weak-first ordering), scoring,
progress persistence and a full scripted CLI session.
