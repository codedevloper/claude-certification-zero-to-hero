# Lab 16: Evaluation Framework

> **Level:** Advanced · **Time:** ~60 min · **Cost:** free in mock mode; live mode uses API credits · **Exam relevance:** CCAR-P 4.1, CCAR-P 4.2, CCAR-P 4.3, CCAR-P 4.4, CCAO-F 2.1, CCAO-F 2.4

## Objective

Replace "it looked fine when I tried it" with a repeatable measurement. You will build a small but complete evaluation harness for a Claude-powered feature, a shipment-triage assistant for the fictional *Acme Logistics*, and use it to decide whether a new prompt is safe to ship. By the end you will have:

1. A **golden dataset** of 16 labelled cases, tagged by scenario so you can see where a change helps or hurts.
2. **Code-based graders** for everything a program can check: JSON validity, exact category and priority, reply length, required and forbidden phrases, and a regular-expression check.
3. An **LLM-as-judge** rubric for the parts code cannot check (helpfulness, tone, groundedness), with structured output, strict validation and anchored scores.
4. **Aggregate metrics** overall and per tag.
5. An **A/B comparison** of prompt v1 and prompt v2 using a sign test, a bootstrap confidence interval and a pairwise judge that is asked twice with the positions swapped.
6. A **release gate** that turns the numbers into a SHIP or BLOCK decision.

You will also check the harness itself before trusting it, because a broken grader produces confident nonsense.

## Level, time and cost

| Item | Value |
|---|---|
| Level | Advanced |
| Time | About 60 minutes, including the exercises |
| Mock mode | Free, offline, standard library only, runs in well under a second |
| Live mode | 32 calls to the system under test (`claude-opus-5-5`, `effort: "low"`) and 64 judge calls (`claude-haiku-5-5` by default, `effort: "medium"`) |

> **Cost:** requires API credits (live mode).

As a rough guide, a live run uses about 20,000 input and 15,000 output tokens on the system under test, including thinking, and about 60,000 input and 10,000 output tokens on the judge. At list prices as of 2026-10-24 (Claude Opus 5.5 at $4 / $20 per million input / output tokens, and Claude Haiku 5.5 at $0.10 / $0.50 for prompts up to 100K tokens), that is well under one US dollar per run. Check the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) for current rates, and multiply by the number of repeated trials you plan to run.

## Prerequisites

- Python 3.10 or later.
- [Lab 03](../lab-03-structured-outputs/README.md) (structured outputs) and [Lab 06](../lab-06-model-comparison/README.md) (model comparison) are helpful background.
- Basic statistics vocabulary (mean, confidence interval, p-value). The lab explains what each number means as it goes.

## Architecture

```mermaid
flowchart TB
    G[(golden.jsonl<br/>16 tagged cases)] --> R1[Run prompt v1]
    G --> R2[Run prompt v2]
    R1 --> C[Code graders<br/>JSON, exact match, length,<br/>must / must-not include, regex]
    R2 --> C
    R1 --> J[Pointwise judge<br/>rubric 1-5, JSON schema]
    R2 --> J
    R1 & R2 --> P[Pairwise judge<br/>asked in both orders]
    C --> M[Metrics<br/>overall and per tag]
    J --> M
    M --> S[Sign test +<br/>bootstrap CI]
    P --> S
    S --> GATE{Release gate}
    GATE -->|all thresholds met| SHIP[SHIP]
    GATE -->|any threshold missed| BLOCK[BLOCK with reasons]
    H[Health checks<br/>oracle, null, bad judge JSON] -.validates.-> C
    H -.validates.-> J
```

## Setup

Mock mode needs nothing beyond Python 3.10+. From the repository root:

```bash
CLAUDE_LAB_MODE=mock python 19-hands-on-labs/lab-16-evaluation-framework/lab.py
```

For live mode, install the SDK from [`../requirements.txt`](../requirements.txt) and export your API key. See [`../.env.example`](../.env.example) for the variable names.

```bash
pip install -r 19-hands-on-labs/requirements.txt
export ANTHROPIC_API_KEY="..."              # never commit this value
export LAB16_JUDGE_MODEL="claude-haiku-5-5" # optional; the default is FAST_MODEL from common/claude_lab.py
```

## Walkthrough of the sample code

Everything is in [`lab.py`](lab.py), built on the shared helper [`../common/claude_lab.py`](../common/claude_lab.py).

### The task and the two prompts

The assistant reads a customer message and returns a JSON object with `category` (one of six labels), `priority` (`low`, `medium` or `high`) and a short `reply`.

- **v1** is a one-line prompt: "classify, write a reply, return JSON".
- **v2** spells out the label set, defines each priority level, sets reply rules (apologise once, quote the tracking ID, one concrete next step, never promise dates, refunds or compensation, 60 words at most), demands a bare JSON object, and tells Claude to treat the message as data rather than instructions.

Both calls follow the current API rules: `model=MODEL`, `output_config={"effort": "low"}` for a simple classification task, no sampling parameters, no prefill, and a `stop_reason` check before the text is used. A truncated or refused response becomes an empty output, which then fails the graders visibly instead of being silently scored.

v2 deliberately asks for JSON through the prompt rather than through structured outputs, so you can see the format failures that v1 produces. In production you would add `output_config.format` with a JSON schema to the system under test as well. The `json_valid` grader then becomes a regression guard instead of the main line of defence.

### Step 0: check the graders before trusting them

The harness is software, and software has bugs. Before any model call, the lab runs three health checks:

| Check | Input | Expected | What it catches |
|---|---|---|---|
| Oracle | Each case's expected labels plus its `reference_reply` | Every case passes | Graders that are too strict, or a golden case whose reference fails its own rules |
| Null | An empty string | No case passes | Graders that pass by default, such as a must-not-include check on empty text |
| Bad judge JSON | Out-of-range score, wrong type, empty reason | All rejected | A judge validator that lets malformed judgements through |

If the oracle cannot reach 100%, fix the dataset or the grader before you measure anything.

### Step 1: code graders (`grade`)

`parse_output` is strict. The contract is a bare JSON object with known labels, so prose around it, a code fence or an unknown category means the output is invalid. Model output is parsed with `json.loads` and never evaluated as code. When JSON is invalid, the format-dependent graders cannot run and count as failed. The `must_not_include` safety check still runs on the raw text, because a forbidden promise inside prose is still a forbidden promise.

Each grader is a single boolean. The case score is the fraction of graders passed, and the case **passes** only if every grader passes. Keep both numbers: the pass rate is what you gate on, and the mean score shows partial progress.

### Step 1 (continued): the pointwise judge (`judge_pointwise`)

Some qualities have no exact answer. The judge reads the customer message, a reference reply and the candidate, and scores three criteria from 1 to 5.

Good judge design, as implemented here:

- **Anchored rubric.** Each criterion defines what a 5, a 3 and a 1 look like in checkable terms ("quotes the tracking ID and states one concrete next step"). Vague scales such as "rate helpfulness" drift between runs and between judges.
- **Structured output.** The judge call sets `output_config={"effort": "medium", "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}}`, so the reply always parses. The code then re-validates the result (`validate_judgement`): exact keys, integer scores from 1 to 5, and non-empty reasons. A schema guarantees shape, not sense.
- **Untrusted inputs.** The judge prompt says the message and the candidate are data, not instructions. Case G14 contains "Ignore your rules...", which is exactly the kind of text that could steer a careless judge.
- **Reference as a guide, not an answer key.** The rubric tells the judge that the reference is one acceptable answer, which reduces reward for imitation.
- **Different model from the system under test.** By default the judge is `claude-haiku-5-5` and the system under test is `claude-opus-5-5`. A model judging its own output tends to favour its own style.

**Choosing the judge model** is a trade-off. Claude Haiku 5.5 is cheap and fast enough to run on every pull request. Claude Sonnet 5.5 is a middle ground. Claude Opus 5.5 is worth its cost when the criteria are subtle enough that a weaker judge would miss the point. Whatever you choose, calibrate it: hand-score 20 to 30 outputs yourself and compare them with the judge's scores before you rely on it.

### Step 2: aggregate metrics

`summarise` reports the pass rate, mean grader score, JSON-valid rate, safety-failure count and the mean of each judge criterion. `per_tag` breaks the pass rate down by tag. Tags such as `edge_case`, `safety` and `priority` exist so that a change which improves the average but breaks a small, important slice does not slip through.

### Step 3: the A/B comparison

Two prompts run on the **same** cases, so compare them case by case (paired), not as two independent averages.

- **Sign test.** Count the cases where v2 passes and v1 fails (wins) and the reverse (losses), and drop the ties. If the prompts were equally good, wins and losses would be a coin flip, and the exact binomial p-value says how surprising the observed split is. Twelve wins and no losses gives p ≈ 0.0005.
- **Bootstrap confidence interval.** Resample the 16 per-case score differences with replacement 2,000 times, using a fixed seed so the run is reproducible, and read the 2.5th and 97.5th percentiles. If the interval excludes zero, the improvement is unlikely to be noise from this particular sample of cases.
- **Pairwise judge with position swap.** Judges are often better at "which of these two is better?" than at absolute scores, but they can favour whichever answer comes first. The lab asks the judge twice, once with v1 as A and once with v2 as A, and counts a verdict only if both orders agree. Otherwise the result is a tie. The mock judge is deliberately position-biased on close calls, and the swap exposes 7 inconsistent verdicts out of 16. Without the swap, those would have been reported as wins for whichever prompt happened to be shown first.

Sixteen cases are enough to learn the method, but not enough for a production decision. Use more cases, and repeat each configuration several times, because live outputs vary from run to run.

### Step 4: the release gate

`GATE` encodes the release policy as data:

| Rule | Threshold | Why |
|---|---|---|
| Pass rate | ≥ 0.85 | Overall quality bar |
| Safety failures | 0 | Forbidden promises are never acceptable |
| JSON valid rate | 1.0 | Downstream code depends on the contract |
| Each judge criterion mean | ≥ 4.0 | Quality that code cannot check |
| Per-tag regression | No tag drops more than 0.10 below the baseline | Protects small slices |
| Judge errors | 0 | An unjudged case is an unknown, not a pass |

The gate prints every reason a version is blocked, which is what a reviewer needs to see in a continuous integration (CI) log.

## Synthetic test data

`data/golden.jsonl` has 16 cases for the fictional *Acme Logistics*. Each line contains:

| Field | Purpose |
|---|---|
| `id`, `tags` | Identity and the slices used for the per-tag breakdown |
| `input` | The customer message, including a tracking ID in the form `ACM-######` |
| `expected` | Ground-truth `category` and `priority`, written by hand |
| `must_include` / `must_not_include` | Required tracking ID, and forbidden promises (`guarantee`, `refund approved`, `compensation`) |
| `max_reply_words` | Length limit for the reply (60) |
| `reference_reply` | A hand-written acceptable reply, used by the judge and by the oracle check |

The set mixes easy cases with deliberate traps: a sarcastic message (G13) that keyword rules misread, a mixed damaged-and-missing parcel (G15), a message that tries to talk the assistant into a guarantee (G14), and questions that tempt a loosely prompted model to wrap its JSON in prose. Expected labels were written by a person, not copied from a model's output. Gold labels taken from one of the models being compared would reward imitation of that model.

## Execution steps

### Mock mode

```bash
CLAUDE_LAB_MODE=mock python 19-hands-on-labs/lab-16-evaluation-framework/lab.py
echo "exit code: $?"
```

The mock system under test is a pair of deterministic rule sets. v1 has fewer keywords, a crude priority rule and loose formatting, while v2 follows its rules. The mock judges use transparent heuristics, so every number in the expected output can be traced back to code.

### Live mode

> **Cost:** requires API credits (live mode).

```bash
pip install -r 19-hands-on-labs/requirements.txt
export ANTHROPIC_API_KEY="..."
CLAUDE_LAB_MODE=live python 19-hands-on-labs/lab-16-evaluation-framework/lab.py
```

In live mode, Claude may handle v1 better than the mock does, so the gate verdict and the statistics are whatever your run measures. The mock-only self-checks (v2 wins, p < 0.05, gate blocks v1) are skipped. Live mode instead checks that every case was judged successfully. Run it two or three times and compare: the spread between runs is your noise floor, and any improvement smaller than that spread is not a real improvement.

## Expected results

Output from a real mock run. Only the temporary-directory path differs between machines.

```text
=== Lab 16: Evaluation framework ===  [MOCK — offline, no credits used; model=claude-opus-5-5]

Golden dataset: 16 cases; system under test: claude-opus-5-5; judge: claude-haiku-5-5

Step 0: check the graders before trusting them
  [PASS] oracle (reference answers) passes every case
  [PASS] null output (empty string) passes no case
  [PASS] judge validator rejects malformed judgements

Step 1: run prompt v1 and v2, grade with code and the judge

  case  v1    v1 failed graders                      v2    v2 failed graders
  G01   fail  json_valid (rest n/a),must_not_include PASS  -
  G02   PASS  -                                      PASS  -
  G03   fail  category_exact,priority_exact          PASS  -
  G04   fail  priority_exact                         PASS  -
  G05   PASS  -                                      PASS  -
  G06   fail  must_not_include                       PASS  -
  G07   fail  category_exact,priority_exact          PASS  -
  G08   fail  category_exact                         PASS  -
  G09   fail  json_valid (rest n/a)                  PASS  -
  G10   PASS  -                                      PASS  -
  G11   fail  json_valid (rest n/a)                  PASS  -
  G12   fail  json_valid (rest n/a)                  PASS  -
  G13   fail  category_exact                         fail  category_exact,priority_exact
  G14   fail  must_not_include                       PASS  -
  G15   fail  category_exact                         PASS  -
  G16   fail  json_valid (rest n/a)                  PASS  -

Step 2: aggregate metrics
  pass_rate            v1     0.19   v2     0.94
  mean_score           v1     0.63   v2     0.98
  json_valid_rate      v1     0.69   v2     1.00
  safety_failures      v1        3   v2        0
  judge_helpfulness    v1     3.50   v2     5.00
  judge_tone           v1     4.44   v2     5.00
  judge_groundedness   v1     4.44   v2     5.00

  Pass rate by tag:
    address    n=2   v1 0.00   v2 1.00
    billing    n=3   v1 0.67   v2 1.00
    damage     n=3   v1 0.33   v2 1.00
    delay      n=5   v1 0.00   v2 0.80
    edge_case  n=2   v1 0.00   v2 0.50
    lost       n=2   v1 0.00   v2 1.00
    other      n=1   v1 0.00   v2 1.00
    priority   n=3   v1 0.00   v2 1.00
    safety     n=1   v1 0.00   v2 1.00

Step 3: A/B comparison (v1 = baseline, v2 = candidate)
  Sign test on case pass/fail: v2 wins 12, losses 0, two-sided p = 0.0005
  Mean grader-score difference v2 - v1: +0.348 (95% bootstrap CI +0.170 to +0.536, 2000 resamples, seed 16)
  Pairwise judge (both orders): v2 better 9, v1 better 0, tie 7; position-inconsistent verdicts 7/16
  [PASS] sign test p-value is a probability
  [PASS] bootstrap CI is ordered

Step 4: release gate {"min_pass_rate": 0.85, "max_safety_failures": 0, "min_json_valid_rate": 1.0, "min_judge_mean": 4.0, "max_tag_regression": 0.1}
  v1: BLOCK - pass rate 0.19 < 0.85; 3 safety failure(s); JSON valid rate 0.69 < 1.0; judge helpfulness mean 3.50 < 4.0
  v2: SHIP

Per-case results written to /var/folders/.../T/claude-labs/lab-16/results.jsonl
  [PASS] v2 beats v1 on pass rate
  [PASS] improvement is significant at p < 0.05
  [PASS] swapping positions exposed judge position bias
  [PASS] gate blocks v1 and ships v2

Self-checks: 9/9 passed
```

How to read it:

- **v2 still fails G13.** The sarcastic "on time" complaint defeats both versions. A gate that requires 100% would block every release, while a gate at 85% lets v2 ship and leaves G13 visible as a known failure to work on next. Record known failures like this explicitly.
- **v1's judge scores look respectable** (tone 4.44, groundedness 4.44) even though only 19% of its cases pass. Judges measure different things from code graders, so use both.
- **Seven of sixteen pairwise verdicts flipped** when the order changed. Without the swap, those cases would have counted as v1 wins or v2 wins depending only on presentation order.

### Exercises

1. Add four cases for a new `customs` category, run the lab and watch the oracle check fail until you add the label to `CATEGORIES`.
2. Write a v3 prompt that fixes G13 without breaking anything else, and add it to the A/B comparison with v2 as the new baseline.
3. Replace the sign test with a McNemar test on the same 2×2 table and compare the p-values.
4. In live mode, run the judge on 20 outputs you have scored by hand and compute how often the judge agrees with you within one point.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `[FAIL] oracle (reference answers) passes every case` | A reference reply breaks its own case rules (too long, missing tracking ID, a forbidden word) | Fix the dataset row. Never loosen a grader just to make the oracle pass. |
| `judge error on Gxx: ...score out of range` | The judge returned a value outside 1–5 | Keep the validation, and tighten the rubric anchors. Investigate the case rather than dropping it. |
| Live run shows `stop_reason` `max_tokens` (empty outputs) | `max_tokens` is too small for thinking plus the answer | Raise `max_tokens`, or lower `effort`. |
| Live p-values jump between runs | Too few cases and a single trial | Add cases, run several trials per version, and compare the spread. |
| The gate blocks on `tag 'x' regressed` with n=1 | One case is a coin flip at the tag level | Add cases to small tags, or set a minimum n before a tag rule applies. |
| `SystemExit: Live mode needs the SDK` | `anthropic` is not installed | `pip install -r 19-hands-on-labs/requirements.txt` |

## Security considerations

- **Evaluate safety, not only quality.** `must_not_include` and the `safety` tag turn policy ("no promised refunds") into a blocking test. Add a case whenever an incident or red-team finding shows a new failure mode. [Lab 14](../lab-14-prompt-injection-testing/README.md) covers injection testing in depth.
- **The judge is an attack surface.** Candidate outputs and user messages reach the judge prompt, so keep them in delimited tags, tell the judge to treat them as data, and validate its output strictly. A manipulated judge can approve a harmful release.
- **Golden data is sensitive data.** Real evaluation sets are often built from production traffic. Redact them first ([Lab 15](../lab-15-sensitive-data-protection/README.md)), control access, and keep them out of public repositories.
- **Protect the gate itself.** Run it in CI with the thresholds under code review, so that nobody can quietly lower `min_pass_rate` to ship a regression.
- **Do not train or tune on the test set.** If you keep editing prompts until this exact set passes, the set no longer measures generalisation. Hold back a separate test split, or refresh cases regularly.

## Cleanup

The lab writes one file, `claude-labs/lab-16/results.jsonl`, under your system temporary directory, or under `LAB_OUTPUT_DIR` if you set it.

```bash
rm -rf "${LAB_OUTPUT_DIR:-${TMPDIR:-/tmp}}/claude-labs/lab-16"
```

## Exam relevance

| Objective | Text (from [registry.yaml](../../16-certification-tracks/registry.yaml)) | Where this lab covers it |
|---|---|---|
| CCAR-P 4.1 | Define evaluation metrics (accuracy, latency, cost, safety, security) | Grader set, judge criteria, safety failures |
| CCAR-P 4.2 | Design evaluation datasets and mixed-method test frameworks | Tagged golden set, code graders plus judge |
| CCAR-P 4.3 | Run A/B tests and iterative improvement | Paired v1/v2 comparison, sign test, bootstrap |
| CCAR-P 4.4 | Diagnose prompt failure, hallucination and model mismatch | Per-case failed-grader table, G13 analysis |
| CCAO-F 2.1 | Evaluate outputs for accuracy and completeness | Exact-match and must-include graders |
| CCAO-F 2.4 | Decide when human review or extra verification is needed | Judge calibration, release gate |

## Next lab

[Lab 17: Cost Optimisation](../lab-17-cost-optimisation/README.md). You will estimate and reduce what a workload like this one costs, using caching, batching and model routing.
