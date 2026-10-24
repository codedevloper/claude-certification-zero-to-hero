# Troubleshooting: Prompts and Outputs

The request succeeded, but the answer is wrong, invented, too long, in the wrong shape, or refused. These problems are
usually fixed by giving Claude better context and clearer instructions, then **proving** the fix with a small
evaluation set. Concepts: [03 · Prompt engineering](../03-prompt-engineering/README.md),
[14 · Diagnosing failures](../14-evaluation-and-testing/06-diagnosing-failures.md).

> **As of 2026-10-24.** Current Claude models reject `temperature`, `top_p`, `top_k` and assistant prefill, so fixes
> below use instructions, examples, `effort` and structured outputs instead.

## First, classify the failure

| Category | Example | Usually fixed by |
|---|---|---|
| Missing knowledge | Answers about your internal policy are generic | Supplying the source (RAG, Projects, documents) |
| Misunderstood task | Summarises when you wanted a decision | Clearer goal and success criteria |
| Format problem | Prose instead of JSON; Markdown in a plain-text field | Structured outputs; explicit format spec |
| Reasoning error | Wrong arithmetic, skipped step | Adaptive thinking with higher `effort`; decomposition; code tools for maths |
| Fabrication | Invented citation or figure | Grounding, permission to say "unknown", verification |
| Policy / safety | `stop_reason: "refusal"` or a hedged non-answer | Context and legitimate framing; product-level review |

Collect 10–30 failing examples before changing anything, label each with a category, and fix the biggest category
first.

## Hallucination

**Symptom:** confident, specific claims (names, numbers, citations, API methods) that are not in any source or are
wrong.

**Likely causes:**

- The answer was not in the context, so Claude filled the gap from general knowledge.
- The prompt implied an answer must exist ("List the five clauses that ...").
- Long, noisy context buried the relevant passage.
- Retrieval returned the wrong chunks (see [RAG](rag.md)).

**Diagnosis:**

1. Check whether the correct fact was actually in the request (log the full prompt for the failing case).
2. Ask for supporting quotes; any claim without a quote is suspect.
3. Re-run with the source placed before the question and clearly tagged.

**Fix:**

```text
Answer only from the documents in <documents>. For each claim, quote the sentence you rely on in <quote> tags.
If the documents do not contain the answer, reply exactly: "Not found in the provided documents."
```

- Enable citations on `document` blocks and verify `cited_text` appears in the source programmatically.
- Remove leading questions; allow "unknown".
- Narrow the context to relevant passages; put long documents at the top.
- For numbers, have code compute them; ask Claude to explain, not to calculate large sums.
- Human review for high-stakes outputs (CCAO-F-2.4, CCAR-P-5.3).

See [01 · Hallucinations](../01-ai-and-llm-fundamentals/06-hallucinations.md) and the official
[reduce hallucinations guide](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations).

## Verbosity (too long, too much preamble)

**Symptom:** long introductions, repeated caveats, more sections than you need, or token costs higher than expected.

**Likely causes:** no length target; an open-ended request; high `effort` on a simple task; examples that are long;
the prompt itself is verbose (models mirror style).

**Diagnosis:** compare `usage.output_tokens` across a sample; look at which parts of the answer nobody uses.

**Fix:**

- Give a target and a reason: "Reply in at most three sentences; this appears in a mobile notification."
- "Start with the answer. No preamble, no closing summary."
- Lower `output_config.effort` for routine routes (`low` or `medium`).
- Shorten your examples; Claude matches their length.
- Use structured outputs with only the fields you need.
- Keep `max_tokens` as a safety cap, not as the length control (it truncates; it does not summarise).

## Too short or truncated

**Symptom:** the answer stops mid-sentence or JSON is cut off.

**Likely cause:** `stop_reason == "max_tokens"`.

**Diagnosis:** log `stop_reason` for every call.

**Fix:** raise `max_tokens` (stream for large values); ask for a shorter answer; split the task; never parse output
when `stop_reason` is `max_tokens`.

## Format drift

**Symptom:** output matches the format most of the time, then occasionally adds prose, renames a field, wraps JSON in
code fences, or switches language.

**Likely causes:** format described only in prose; conflicting examples; long conversations where early instructions
lose weight; user content that asks for another format.

**Diagnosis:** run the prompt 50 times on varied inputs and count schema failures; inspect the inputs that fail.

**Fix:**

| Need | Use |
|---|---|
| Guaranteed JSON shape | `output_config.format` with a JSON Schema, or `client.messages.parse()` with a model class |
| Guaranteed tool arguments | `strict: true` on the tool definition |
| A text template | A filled example inside `<example>` tags plus "Use exactly this structure" |
| Stable style in long chats | Restate key format rules in a mid-conversation system message (supported models) or restart with a summary |

Validate in code anyway and keep a retry-with-error-message path for anything not schema-guaranteed.

## Ignored instructions

**Symptom:** a rule in the prompt is not followed.

**Likely causes:** the rule conflicts with another rule or an example; it is buried mid-document; it is phrased as a
vague negative ("don't be too technical"); the user turn contradicts it.

**Diagnosis:** search the prompt for contradictions; test the rule alone in a minimal prompt.

**Fix:** state the rule positively and specifically; explain why; place it in the system prompt or right before the
task; remove contradicting examples; state priority when rules compete.

## Inconsistent answers between runs

**Symptom:** the same input gives different answers.

**Likely causes:** under-specified task; ambiguity in the input; reasoning-heavy task at low effort.

**Diagnosis:** run 10 times and look at where outputs diverge; that is where the prompt is ambiguous.

**Fix:** add criteria and a rubric; use examples covering the ambiguous cases; use structured outputs for decisions;
raise effort for reasoning tasks; for classification, evaluate on a labelled set and accept the measured error rate.
(Sampling parameters are not available on current models, so consistency comes from specification, not randomness
settings.)

## Refusals

**Symptom:** `stop_reason: "refusal"` (with `stop_details.category` and `explanation`), or a polite decline in text.

**Likely causes:** the request falls in a restricted category; legitimate work (for example security testing) looks
risky without context; injected content in a document triggered safeguards.

**Diagnosis:** read `stop_details`; check whether the trigger is in the user's text or in retrieved content; try the
same task with the context of your legitimate purpose in the system prompt.

**Fix:**

- Explain the legitimate context and the authorised scope in the system prompt (operator context).
- Remove irrelevant risky content from the context.
- Handle refusals gracefully in the product: tell the user, offer an alternative path, log for review.
- For supported models on the Claude API, consider the server-side `fallbacks` option; see
  [06 · Messages API](../06-claude-api/02-messages-api.md).
- Do not attempt to bypass safeguards; if a legitimate use case is repeatedly blocked, raise it through official
  channels.

## Wrong language, tone or audience

**Symptom:** answers in the wrong language, too formal or too casual.

**Fix:** state the audience and language explicitly; give one example in the right tone; for multilingual products,
pass the user's locale as data and say "Reply in the user's language: {locale}".

## A short diagnostic script

```python
from collections import Counter

def audit(client, prompt_fn, cases, model="claude-opus-5-5"):
    """Run a prompt over labelled cases and count failure categories."""
    tally = Counter()
    for case in cases:
        resp = client.messages.create(model=model, max_tokens=1024,
                                      messages=[{"role": "user", "content": prompt_fn(case["input"])}])
        tally[resp.stop_reason] += 1
        text = "".join(b.text for b in resp.content if b.type == "text")
        if resp.stop_reason == "end_turn" and case["expected"] not in text:
            tally["mismatch"] += 1
    return tally
```

Works with this repository's mock client (`19-hands-on-labs/common/claude_lab.py`) offline. Grow it into a proper eval
in [lab 16](../19-hands-on-labs/lab-16-evaluation-framework/README.md).
