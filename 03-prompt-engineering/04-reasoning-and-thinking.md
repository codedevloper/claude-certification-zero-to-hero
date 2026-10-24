# Reasoning and Thinking

> **Level:** Intermediate · **Time:** ~50 min · **Exam relevance:** CCAO-F D1 · CCAR-P D2, D3, D4

## In plain English

When you face a hard problem, you think it through before you answer: you sketch the steps, check a calculation,
notice a contradiction. Language models benefit from the same thing. Giving Claude room to reason before it commits
to an answer improves results on multi-step problems such as analysis, maths, planning and debugging.

There are two ways to get that reasoning today:

1. **Prompted chain of thought (CoT).** You ask Claude, in the prompt, to reason step by step, often in a tagged
   section of its visible answer. This works in any Claude product.
2. **Built-in thinking.** Current Claude models have a dedicated thinking phase. In the API you control it with
   *adaptive thinking* and the *effort* setting; Claude decides how much to think for each request.

## Why it matters

- Reasoning improves accuracy on tasks with several dependent steps, ambiguous evidence or competing constraints.
- Reasoning costs tokens and time. Knowing how to turn it up for hard work and down for routine work is a core
  cost-quality lever (CCAR-P-3.3 accuracy–latency trade-offs, CCAR-P-4.5 cost-performance).
- The exam guides list chain-of-thought prompting as a named technique (CCAR-P-2.3). You should know both the classic
  prompt pattern and how current models do this natively.
- The API surface changed in 2025–2026: fixed thinking budgets (`budget_tokens`) are legacy and rejected on current
  models. Code and study material written before that is now wrong.

## How it works

### Prompted chain of thought

The classic technique asks for reasoning in the response itself:

```text
Before answering, work through the problem inside <analysis> tags:
list the relevant facts, check each eligibility rule in order, and note any conflicts.
Then give your conclusion inside <answer> tags.
```

Levels of guidance, from light to heavy:

| Level | Prompt wording | When to use |
|---|---|---|
| Basic | "Think this through before answering." | Quick boost on a moderately tricky question |
| Guided | "First check X, then compare with Y, then decide Z." | You know the right method and want it followed |
| Structured | Reasoning in `<analysis>`, answer in `<answer>` | You need to show or parse the reasoning separately |

Prompted CoT is still valuable when you want reasoning that **reviewers can read** in the output, in the Claude apps
where you do not control API settings, and for teaching the method you expect.

Two cautions with current models:

- Do not ask Claude to reproduce its internal thinking word for word in the answer. Some current models treat requests
  to extract their internal reasoning as a refusal category (`reasoning_extraction`). Ask for a *written analysis* or
  *justification* instead, or read the thinking summary the API provides.
- Visible reasoning lengthens every response. Use it where a human needs it, not by default.

### Built-in thinking in the API (as of 2026-10-24)

On current models such as `claude-opus-5-5`, `claude-sonnet-5-5` and `claude-haiku-5-5`, thinking is **adaptive**:
Claude decides when and how much to think based on the difficulty of the request and the effort level you set.

| Setting | Where | What it does |
|---|---|---|
| `thinking={"type": "adaptive"}` | Top-level request parameter | Lets Claude think as needed. On Claude Opus 5.5 this is also what happens when you omit `thinking`; it cannot be disabled on that model. |
| `thinking={"type": "adaptive", "display": "summarized"}` | Same | Returns a readable summary of the reasoning. The default on current models is `"omitted"`, which returns thinking blocks with empty text. |
| `output_config={"effort": ...}` | `output_config` object | `low`, `medium`, `high`, `xhigh` or `max`. Higher effort means more thinking, more thorough tool use and more tokens. |
| `max_tokens` | Top-level | The hard ceiling on output, **including** thinking. Leave headroom at high effort. |

Key rules that changed:

- **`budget_tokens` is legacy.** `thinking={"type": "enabled", "budget_tokens": N}` returns a 400 error on current
  models. Move budget control to `effort`.
- **Defaults differ by model.** Claude Opus 5.5 defaults to `medium` effort; Claude Sonnet 5.5 defaults to `high`.
  Set effort explicitly so behaviour does not change silently when you switch models.
- **Sampling parameters are gone.** Do not send `temperature`, `top_p` or `top_k`; current models reject them.
- **Thinking is billed as output tokens** whether or not you display it.

### Choosing an effort level

Effort is the first lever to adjust when you trade quality against latency and cost on a single model.

| Effort | Good for | Notes |
|---|---|---|
| `low` | Classification, extraction, short chat replies, sub-agent chores | Fewer, more consolidated tool calls; terse output |
| `medium` | Everyday analysis and drafting; the Opus 5.5 default | A strong cost-quality balance on current models |
| `high` | Intelligence-sensitive work: complex analysis, multi-step agents | A common sweet spot for hard tasks |
| `xhigh` | Long-horizon coding and agentic work | Measure the gain before adopting |
| `max` | Problems where correctness matters far more than cost | Uncapped; use only when evals show headroom |

Tune effort **per route**, not globally, and measure on real samples (see
[iterating on prompts](08-iterating-on-prompts.md)). Changing thinking or effort settings between requests
invalidates part of the prompt cache, so keep them stable within a conversation (see
[prompt caching](../04-context-engineering/03-prompt-caching.md)).

### Steering thinking with the prompt

Adaptive thinking is promptable:

- To encourage reflection in agent loops: "After each tool result, consider whether it answers the question before
  choosing the next step."
- To reduce over-thinking on simple traffic: "Use extended reasoning only for problems that need several steps; answer
  simple questions directly."
- To stop indecision: "Choose an approach and commit to it; revisit only if new information contradicts it."

### Thinking in multi-turn and tool-use conversations

When a response contains thinking blocks, pass the whole `response.content` back unchanged in the next request. Do not
edit, reorder or strip the blocks yourself; the API drops any block a model cannot use. Editing earlier turns can
invalidate thinking blocks on current models, so keep conversation history append-only (more in
[compaction and context editing](../04-context-engineering/05-compaction-and-context-editing.md)).

## Example

The fictional *Northwind Lending* risk team uses Claude to review whether a loan restructuring proposal is consistent
with internal policy. This is multi-step analysis, so they use high effort and request a summary of the reasoning for
the audit trail.

```python
import anthropic

client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY

policy = open("data/restructuring_policy.md", encoding="utf-8").read()
proposal = open("data/proposal_1187.md", encoding="utf-8").read()

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,                      # includes thinking; leave headroom at high effort
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "high"},
    messages=[{
        "role": "user",
        "content": (
            f"<policy>\n{policy}\n</policy>\n\n<proposal>\n{proposal}\n</proposal>\n\n"
            "Check the proposal against each numbered rule in the policy. For every rule, say "
            "whether it is met, not met, or not determinable from the proposal, and quote the "
            "evidence. Finish with an overall assessment for a human credit officer."
        ),
    }],
)

if response.stop_reason == "max_tokens":
    raise RuntimeError("Output was cut off; raise max_tokens or lower effort.")
if response.stop_reason == "refusal":
    raise RuntimeError("Request declined; review the input and route to a human.")

for block in response.content:
    if block.type == "thinking":
        print("[reasoning summary]", block.thinking[:500])
    elif block.type == "text":
        print(block.text)

print("output tokens (including thinking):", response.usage.output_tokens)
```

The same request with cURL, useful for quick experiments:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-5-5",
    "max_tokens": 16000,
    "thinking": {"type": "adaptive", "display": "summarized"},
    "output_config": {"effort": "high"},
    "messages": [{"role": "user", "content": "Is 2,147,483,647 prime? Explain briefly."}]
  }'
```

> **Cost:** requires API credits (live mode). Higher effort produces more output tokens.

## Enterprise use case

*Acme Logistics* (fictional) runs three Claude-powered routes:

| Route | Task | Effort chosen | Reason |
|---|---|---|---|
| Parcel-label parser | Extract fields from scanned labels | `low` | Simple, high volume, latency-sensitive |
| Exception summariser | Weekly operational summary | `medium` | Moderate analysis; reviewed by humans |
| Network planner | Re-route freight after a depot closure | `high` | Many interacting constraints; errors are costly |

They started every route at the model default, ran a small evaluation set at the neighbouring levels, and kept the
lowest level that met the quality bar. The planner showed a clear gain from `medium` to `high` but none from `high` to
`xhigh`, so they stopped at `high`. They record the effort level in the prompt's version metadata, because a change in
effort is a behaviour change that needs the same review as a prompt change.

## Common mistakes

- **Sending `budget_tokens` or `temperature`.** Both are rejected on current models. Use `effort` and remove sampling
  parameters.
- **Setting `max_tokens` too low at high effort.** Thinking consumes the same budget, so the visible answer gets cut
  off (`stop_reason == "max_tokens"`).
- **Using maximum effort everywhere.** It inflates cost and latency with little gain on routine work.
- **Assuming effort means the same thing across models.** Levels are calibrated per model; re-test after a model
  change.
- **Prompting "think step by step" on top of high-effort thinking** for every request. It lengthens visible output
  without adding much. Use prompted CoT when people need to read the reasoning.
- **Treating reasoning as proof.** A fluent reasoning summary can still contain errors. Verify the conclusion.

## Security considerations

- Thinking summaries can include details from the input, including sensitive data. Apply the same logging and
  retention rules to them as to the rest of the response.
- Do not expose raw reasoning to end users as an authoritative explanation of a decision; it is a model artefact,
  not an audit record of policy. Keep human sign-off for consequential decisions (see
  [human oversight](../12-ai-security/13-human-oversight.md)).
- Longer reasoning does not make a model immune to injected instructions in its inputs.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 400 error mentioning `budget_tokens` or `thinking.type.disabled` | Legacy thinking configuration | Use `thinking={"type": "adaptive"}` (or omit it) and set `output_config.effort` |
| 400 error mentioning `temperature` | Sampling parameter sent | Remove `temperature`, `top_p`, `top_k` |
| Long pause before any text when streaming | Thinking display is `"omitted"` by default | Set `display: "summarized"` or show a progress indicator |
| Answer cut off | `max_tokens` too small for thinking plus answer | Raise `max_tokens`, stream, or lower effort |
| Responses got slower and costlier after a model upgrade | Different default effort or calibration | Set effort explicitly and re-run your effort sweep |
| `stop_reason == "refusal"` with category `reasoning_extraction` | Prompt asks Claude to reveal its internal reasoning | Ask for a written justification instead, or read the thinking summary |

## Check your understanding

1. What replaced `budget_tokens` for controlling how much Claude thinks on current models?
2. Name two situations where prompted chain of thought is still useful.
3. Why should you pin the effort level per route rather than changing it on every request?
4. A team switches a route from Claude Opus 5.5 to Claude Sonnet 5.5 without setting effort. What might change?

<details>
<summary>Answers</summary>

1. Adaptive thinking (`thinking={"type": "adaptive"}`, or omitted on models where it is the default) combined with
   `output_config={"effort": ...}`. `max_tokens` remains the hard ceiling.
2. When reviewers need to read the reasoning in the output; when working in the Claude apps without API settings; and
   when you want Claude to follow a specific method you spell out.
3. Effort changes behaviour and cost, so it should be evaluated and versioned like a prompt change. Changing it
   between requests also invalidates part of the prompt cache.
4. The default effort differs (`medium` on Opus 5.5, `high` on Sonnet 5.5) and levels are calibrated differently, so
   latency, cost and depth of reasoning may all shift. Set effort explicitly and re-test.

</details>

## Further reading

- [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) (Anthropic docs)
- [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) (Anthropic docs)
- [Prompting best practices: thinking and reasoning](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) (Anthropic docs)
- [Latency optimisation](../15-production-operations/04-latency-optimisation.md) and [cost optimisation](../15-production-operations/03-cost-optimisation.md) in this repository
- Next page: [Task decomposition and chaining](05-task-decomposition-and-chaining.md)
