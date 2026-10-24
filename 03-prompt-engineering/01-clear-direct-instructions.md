# Clear and Direct Instructions

> **Level:** Beginner · **Time:** ~40 min · **Exam relevance:** CCAO-F D1, D7 · CCAR-P D2

## In plain English

Imagine you hire a brilliant contractor who has never worked at your company. They are quick, well read and eager,
but they do not know your customers, your house style, what "the usual format" means, or why the task matters. If
you hand them a sticky note that says "write up the incident", you will get *something*, but probably not what you
had in mind.

Claude is in the same position at the start of every conversation. It brings broad knowledge and strong reasoning, but
none of your context. A clear, direct prompt closes that gap: it says what you want, who it is for, what "good" looks
like, and any constraints, in plain words.

## Why it matters

- **Most poor outputs are specification problems, not model problems.** When an answer misses the mark, the first
  thing to check is whether the prompt actually said what you wanted.
- **Current models follow instructions closely.** Anthropic's guidance (as of 2026-10-24) notes that recent Claude
  models do what you ask rather than guessing at what you might also want. If you want Claude to go beyond the
  minimum, say so explicitly.
- **Clarity is cheaper than iteration.** A precise first prompt saves several rounds of "no, I meant…", which costs
  time in the apps and tokens in production.
- **It is examined.** Writing effective prompts and adapting them to task type are explicit objectives in both the
  Foundations and Professional exam guides (see the [module README](README.md) for objective IDs).

## How it works

### The colleague test

Anthropic suggests a simple check: show your prompt to a colleague who knows little about the task and ask them to do
it. If they would need to ask questions, Claude will have to guess the answers. Every question your colleague would
ask is a sentence missing from the prompt.

### The building blocks of a clear prompt

| Element | What to state | Example phrase |
|---|---|---|
| Task | The action, in one sentence | "Summarise this design review for the steering group." |
| Purpose | Why the output is needed | "They will decide whether to fund phase 2." |
| Audience | Who reads it, what they know | "Non-technical executives; avoid jargon." |
| Inputs | What material Claude has | "The review notes are in `<notes>` below." |
| Output | Format, length, structure | "Five bullet points, then a one-line recommendation." |
| Constraints | Must and must-not rules | "Do not speculate about costs not in the notes." |
| Success criteria | How you will judge it | "A reader should know the decision needed within 30 seconds." |

You rarely need every row. A short task might need only the task and output lines. A high-stakes task usually needs
all of them.

### Explain the reason, not just the rule

Claude generalises from explanations. "Never use abbreviations" is a rule Claude will follow literally. "This text
will be read by a screen reader for visually impaired users, so spell out abbreviations and avoid symbols" lets Claude
also avoid things you did not think to list, such as ampersands or emoji.

### Say what to do, not only what to avoid

Positive instructions are easier to follow than prohibitions. Instead of "don't be so verbose", try "answer in at
most three sentences". Instead of "no markdown", try "write in plain prose paragraphs".

### Use numbered steps when order matters

If a task has a required sequence (check eligibility, then calculate, then explain), write the steps as a numbered
list. If order does not matter, prose is fine.

### Be explicit about scope and initiative

Because current models follow instructions closely, scope language matters:

- "Suggest changes" produces suggestions. "Make the changes" produces edits.
- "Fix the bug" may not include tidying nearby code. If you want that, ask for it.
- "Include as many relevant details as you can" will produce a fuller answer than "describe it".

### Adapting the strategy to the task type

Different kinds of work need different emphases. This is a named Foundations objective (CCAO-F-1.4).

| Task type | What to emphasise in the prompt | Typical pitfalls |
|---|---|---|
| **Analysis** (evaluate, compare, diagnose) | The criteria or framework to apply, the evidence Claude may use, and how to show its reasoning. Ask it to separate facts from judgements. | Vague criteria ("is this good?"), conclusions not tied to evidence |
| **Research** (gather, synthesise, verify) | The question, the scope (time range, sources), how to handle conflicting sources, and a requirement to cite or quote. Ask for confidence levels and open questions. | Overconfident synthesis, missing citations, scope creep |
| **Drafting** (write, rewrite, adapt) | Audience, purpose, tone, length and a sample of the house style. State what must be preserved when editing. | Generic tone, wrong length, losing facts during rewrites |
| **Brainstorming** (generate options) | Quantity, variety, constraints that matter and constraints to ignore for now. Ask for options before evaluation. | Early convergence on obvious ideas, ideas that break real constraints |

A useful habit: name the task type in the prompt ("This is a brainstorming step; quantity and variety matter more
than polish right now"). It tells Claude which trade-offs to make.

## Example

The fictional *Acme Logistics* operations team wants a weekly summary of delivery exceptions.

**Before (unclear):**

```text
Summarise these delivery exceptions.
```

**After (clear and direct):**

```text
You are helping the Acme Logistics operations lead prepare for Monday's regional call.

Task: Summarise last week's delivery exceptions from the log in <exceptions> below.

Audience and purpose: Regional managers will use the summary to decide where to send
extra drivers next week. They know the depots by name but have not read the log.

Output:
1. A two-sentence overview of the week.
2. A table with one row per depot: depot, number of exceptions, most common cause.
3. Up to three recommended actions, each tied to a specific pattern in the data.

Constraints:
- Use only the data in the log. If a cause is listed as "unknown", report it as unknown
  rather than guessing.
- Keep the whole summary under 250 words, because it is read aloud on the call.

<exceptions>
{{EXCEPTION_LOG}}
</exceptions>
```

The same prompt in Python. The `{{EXCEPTION_LOG}}` placeholder is filled from a file, and the API key comes from the
`ANTHROPIC_API_KEY` environment variable, never from code.

```python
from pathlib import Path

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

prompt_template = Path("prompts/weekly_exceptions.txt").read_text(encoding="utf-8")
exception_log = Path("data/exceptions_week_42.csv").read_text(encoding="utf-8")
prompt = prompt_template.replace("{{EXCEPTION_LOG}}", exception_log)

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=2000,
    output_config={"effort": "low"},  # a routine summary does not need deep reasoning
    messages=[{"role": "user", "content": prompt}],
)

if response.stop_reason == "end_turn":
    print(next(b.text for b in response.content if b.type == "text"))
else:
    print(f"Unexpected stop reason: {response.stop_reason}")
```

> **Cost:** requires API credits (live mode).

## Enterprise use case

*Northwind Lending* (fictional) rolled out Claude to its credit operations analysts. Early prompts were one-liners
such as "check this application". Results varied between analysts, and reviewers could not tell which policy rules
had been applied.

The team built a short prompt checklist from the building-blocks table: task, purpose, audience, inputs, output
format and constraints. They added the reason for each constraint ("applicants may appeal, so every finding must
quote the source field"). Within two weeks the share of outputs that reviewers accepted without edits rose noticeably,
and, more importantly, outputs became consistent enough to evaluate. The checklist now lives in a shared Project as
part of the instructions, so analysts no longer have to remember it (see
[Projects and knowledge](../05-claude-products-and-models/04-projects-and-knowledge.md)).

## Common mistakes

- **Assuming shared context.** "Use the usual format" means nothing to Claude unless the format is in the prompt or
  the Project knowledge.
- **Stacking prohibitions.** A wall of "don't" rules is hard to follow and often contradictory. Rewrite as positive
  instructions with reasons.
- **Shouting.** Writing in capitals or repeating "IMPORTANT" was a workaround for older, less attentive models. With
  current models it can cause over-application of the rule. State it once, clearly, with a reason.
- **Under-specifying output.** If you will paste the result somewhere (a slide, a ticket, a spreadsheet), say what
  shape it must have.
- **Mixing several tasks in one sentence.** "Summarise, critique and rewrite this" invites a muddled answer. Number
  the steps or split them into a chain (see [task decomposition](05-task-decomposition-and-chaining.md)).

## Security considerations

- Clear instructions are not a security control. A precise prompt makes good behaviour likely; it does not stop a
  malicious input from trying to override it. Treat untrusted content as data and see
  [prompt injection](../12-ai-security/02-prompt-injection.md).
- Do not paste secrets, credentials or regulated personal data into prompts unless your organisation's policy and
  the product's data handling allow it.
- When a constraint matters for safety or compliance ("never give dosage advice"), enforce it in code or process as
  well as in the prompt.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Output is generic | No audience or purpose stated | Add who reads it and what decision it supports |
| Output is too long or too short | No length guidance | Give a word, sentence or bullet limit, and say why |
| Claude did less than you hoped | Instruction scoped too narrowly | Ask explicitly for the extra work ("also check…", "go beyond the basics") |
| Claude did more than you wanted | Open-ended wording | Narrow the scope: "only change X; leave everything else as is" |
| A rule is applied too rigidly | Rule given without a reason | Explain the reason so Claude can judge edge cases |

More diagnostics are in [troubleshooting prompts and outputs](../24-troubleshooting/prompts-and-outputs.md).

## Check your understanding

1. What is the "colleague test", and what does a failed test tell you?
2. Rewrite "Don't use technical terms" as a positive instruction with a reason.
3. Which elements would you add to a prompt for a research task that you might omit for a brainstorming task?
4. Why can repeating "IMPORTANT" in capitals backfire with current Claude models?

<details>
<summary>Answers</summary>

1. You imagine (or actually ask) a colleague with little context to follow the prompt. Every question they would need
   to ask marks missing information that Claude would otherwise have to guess.
2. For example: "Write for readers with no engineering background, explaining each idea in everyday words, because
   this goes to the customer advisory board."
3. Scope (time range, sources), how to handle conflicting sources, a requirement to cite or quote, and confidence
   levels. Brainstorming instead emphasises quantity and variety, and may relax evaluation until later.
4. Current models already attend closely to instructions, so heavy emphasis can make Claude over-apply the rule,
   including in cases where it should not. One clear statement with a reason works better.

</details>

## Further reading

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) (Anthropic docs; "Be clear and direct" and "Add context")
- [Prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)

<!-- page-nav:start -->
---

[Module overview](README.md) · [Next: Structure with XML Tags →](02-structure-with-xml-tags.md)
<!-- page-nav:end -->
