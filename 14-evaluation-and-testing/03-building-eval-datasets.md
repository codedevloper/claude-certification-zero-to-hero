# Building Eval Datasets

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P D4 (4.2), CCAO-F D2 (2.3)

## In plain English

An eval is only as good as its cases. An eval dataset is a collection of inputs, each with either an expected answer or
enough information for a grader to judge the output. It should look like the work your system really does, include
the awkward cases that break systems, and be protected and versioned like code.

There are three main sources of cases: real traffic (sampled and cleaned), cases written by experts (golden sets), and
cases generated with a model and then reviewed (synthetic). Most good datasets mix all three.

## Why it matters

- CCAR-P-4.2 asks you to design evaluation datasets and mixed-method test frameworks.
- A dataset that does not represent real use gives you confident wrong answers. Teams often optimise prompts against a
  dataset and then discover production looks nothing like it.
- Edge cases are where systems fail and where users lose trust. If the dataset has none, the eval cannot see those
  failures.

## How it works

### Anatomy of a case

```json
{
  "id": "refund-policy-017",
  "input": {"question": "Can I return a laptop after 40 days if it was a gift?"},
  "context_ids": ["policy-returns-v12#s3"],
  "expected": {
    "answer_contains": ["30 days", "gift receipt"],
    "must_not_contain": ["40 days is fine"],
    "should_refuse": false
  },
  "rubric": "Correctly states the 30-day window, mentions the gift-receipt exception, cites the policy section.",
  "tags": ["returns", "edge:gift", "source:expert"],
  "split": "dev",
  "provenance": {"author": "returns-team", "verified_on": "2026-10-01", "ground_truth": "human-written"}
}
```

Useful fields: a stable `id`, the `input`, the expected outcome (exact answer, acceptable answers, checklist or
rubric), `tags` for slicing results, a `split` (dev or test), and `provenance` that records where the ground truth came
from and when it was last verified.

### Source 1: sampled production traffic

1. Sample inputs across time, user segments and channels, not just the busiest hour.
2. Remove or replace personal data (names, account numbers, addresses) before the data leaves the production boundary.
3. Label with domain experts. Use two labellers on a subset and measure agreement; disagreement shows where the task
   definition is unclear.
4. Stratify so small but important classes have enough cases to measure.

### Source 2: golden sets written by experts

Experts write cases that cover each requirement, policy rule or skill the system must show. Golden sets are small and
high quality. They are the core regression suite and the place to encode business rules ("never quote a refund
amount over 500 without escalation").

### Source 3: synthetic generation

Use Claude to generate variations at scale: paraphrases, different personas, other languages, adversarial phrasings,
long or messy inputs. Rules for synthetic data:

- Generate **inputs**, and get expected outputs from rules, experts or verified sources. If the expected outputs come
  from a model, you are measuring agreement with that model, not correctness. This is especially misleading when you
  compare that same model against an alternative.
- Seed generation with real examples and a coverage matrix (topic by difficulty by persona), so cases spread out
  rather than cluster.
- Review a sample by hand. If you find a systematic problem, fix the generator and regenerate rather than patching
  individual cases.
- Tag synthetic cases so you can report results with and without them.

### Edge cases to include deliberately

| Category | Examples |
|---|---|
| Boundary values | Exactly 30 days, zero amounts, maximum lengths |
| Ambiguity | Questions with two plausible readings; cases where experts disagree |
| Out of scope | Requests the system should decline or redirect |
| Missing information | The answer is not in the provided documents; the system should say so |
| Noisy input | Typos, mixed languages, pasted email threads, OCR errors |
| Long input | Near the context limits you expect in production |
| Conflicting sources | Two documents disagree; system should notice |
| Both directions | Cases where the system *should* call a tool or refuse, and cases where it *should not* |
| Adversarial | Prompt-injection attempts, policy-evasion phrasing (see [page 7](07-safety-and-red-team-evals.md)) |

"Both directions" matters: an eval that only checks that the agent searches when it should will reward an agent that
always searches.

### Splits and overfitting

When you iterate on a prompt against a dataset, you slowly fit the prompt to that dataset. Keep a **test split** that
you look at rarely (for example, only at release decisions), and iterate on a **dev split**. If dev scores rise and
test scores do not, you are overfitting.

### Dataset hygiene checklist

- Every case has a verified expected outcome; a reference answer actually passes the grader.
- No answer leakage: expected answers do not appear in the prompt, few-shot examples or files the system can read.
- Cases are not answerable from general knowledge when you mean to test retrieval or tools (use synthetic or obscure
  facts).
- Class balance is known, and a majority-class baseline is reported.
- Time-sensitive answers have a "verified on" date and a review schedule.
- The dataset is versioned with the grader; scores from different versions are not compared directly.

## Example

A coverage-driven synthetic input generator. It asks Claude for varied phrasings of each scenario using structured
outputs, and attaches the expected outcome from a rule table rather than from the model. It runs offline in mock mode.

```python
"""generate_cases.py - synthesise varied inputs; expected outcomes come from rules, not the model."""
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "19-hands-on-labs" / "common"))
from claude_lab import MODEL, get_client, register_mock, text_of  # noqa: E402

SCENARIOS = {  # scenario -> expected outcome, owned by the returns team
    "return_within_window": {"should_refuse": False, "answer_contains": ["30 days"]},
    "return_after_window": {"should_refuse": False, "answer_contains": ["30 days", "not eligible"]},
    "gift_without_receipt": {"should_refuse": False, "answer_contains": ["gift receipt"]},
    "asks_for_other_customer_order": {"should_refuse": True, "answer_contains": []},
}
PERSONAS = ["polite and brief", "frustrated, long message", "non-native English speaker"]

SCHEMA = {
    "type": "object",
    "properties": {"variants": {"type": "array", "items": {"type": "string"}}},
    "required": ["variants"],
    "additionalProperties": False,
}


@register_mock
def fake(**request):
    return json.dumps({"variants": ["Mock question A about returns?", "Mock question B about returns?"]})


def generate(client, scenario: str, persona: str, n: int = 2) -> list[str]:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": (
            f"Write {n} different customer messages to a retail returns assistant.\n"
            f"Scenario: {scenario.replace('_', ' ')}.\nCustomer style: {persona}.\n"
            "Use fictional details only. Vary wording and length. Return only the messages.")}],
    )
    if response.stop_reason != "end_turn":
        return []
    return json.loads(text_of(response))["variants"]


if __name__ == "__main__":
    client = get_client()
    cases = []
    for scenario, persona in itertools.product(SCENARIOS, PERSONAS):
        for i, text in enumerate(generate(client, scenario, persona)):
            cases.append({
                "id": f"{scenario}-{PERSONAS.index(persona)}-{i}",
                "input": {"question": text},
                "expected": SCENARIOS[scenario],
                "tags": [scenario, f"persona:{persona}", "source:synthetic"],
                "split": "dev",
                "provenance": {"ground_truth": "rule-table", "generator_model": MODEL},
            })
    print(f"generated {len(cases)} cases; first: {json.dumps(cases[0], indent=2)}")
```

> **Cost:** requires API credits (live mode). Generating a few hundred inputs is cheap; consider the
> [Message Batches API](../06-claude-api/05-batch-processing.md) for thousands.

## Enterprise use case

*Northwind Lending* builds an eval for an assistant that answers staff questions about hardship programmes. The team
assembles 420 cases:

- 180 from anonymised staff questions over two months, labelled by two senior servicing agents (agreement 91 percent;
  the disagreements exposed two ambiguous policy clauses, which the policy owner then clarified).
- 90 golden cases written by the policy team, one or more per policy rule.
- 120 synthetic variations covering personas and phrasing, with expected outcomes taken from the rule table.
- 30 edge and adversarial cases: questions the documents cannot answer, conflicting policy versions, and requests for
  another customer's details.

Twenty percent is held out as a test split reviewed only at release decisions. Each case records when its expected
answer was last verified, and a policy change triggers re-verification of the affected tags.

## Common mistakes

- Using model outputs as gold answers, then using that dataset to compare models.
- Only "happy path" cases.
- Iterating on the test set until it passes.
- No provenance, so nobody knows which cases are stale after a policy change.
- Personal data copied from production into a shared spreadsheet.

## Security considerations

- Treat datasets built from production as sensitive data: minimise, anonymise, control access, set retention.
- Keep adversarial cases private; publishing them helps attackers tune around your defences.
- Protect the dataset and grader against tampering with code review and access control; changes should be visible in
  version history.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Every variant scores near 100 percent | Dataset too easy or leaking answers | Add harder and edge cases; check for leakage |
| Every variant scores near 0 percent on some cases | Broken cases or grader | Run reference answers through the grader; fix cases |
| Labellers disagree often | Task definition unclear | Clarify guidelines; mark genuinely ambiguous cases |
| Synthetic cases all look alike | Generator prompt lacks diversity | Use a coverage matrix, real seeds, persona and length variation |

## Check your understanding

1. Why should synthetic generation produce inputs rather than expected outputs?
2. What is the purpose of a held-out test split?
3. Give three categories of edge case and an example of each.
4. Why record provenance and a "verified on" date for each case?

<details>
<summary>Answers</summary>

1. If a model writes the expected outputs, the eval measures agreement with that model rather than correctness, and
   unfairly favours that model in comparisons.
2. To detect overfitting: you iterate on the dev split and check the test split rarely, so improvements that do not
   generalise become visible.
3. Any three, for example: boundary values (exactly 30 days), missing information (answer not in documents),
   out-of-scope requests (asking for another customer's data), noisy input (OCR errors), conflicting sources.
4. So you know where the ground truth came from and when it may have gone stale, and can re-verify affected cases when
   policies or facts change.

</details>

## Further reading

- Anthropic: [Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- Anthropic: [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- In this repository: [RAG evaluation](../11-rag-and-knowledge-systems/06-rag-evaluation.md),
  [Lab 16](../19-hands-on-labs/lab-16-evaluation-framework/README.md),
  [Project 02](../20-real-world-projects/02-knowledge-base-qa-assistant/README.md)
