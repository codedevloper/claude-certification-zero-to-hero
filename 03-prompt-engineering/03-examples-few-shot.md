# Examples and Few-Shot Prompting

> **Level:** Beginner → Intermediate · **Time:** ~40 min · **Exam relevance:** CCAO-F D1 · CCAR-P D2

## In plain English

Some things are easier to show than to describe. You could write a page explaining your team's tone of voice, or you
could show three emails that get it right. Few-shot prompting means including a handful of worked examples in your
prompt so Claude can see the pattern you want: the format, the tone, the level of detail and how tricky cases are
handled.

- **Zero-shot**: instructions only, no examples.
- **One-shot**: a single example.
- **Few-shot** (or multishot): several examples, typically three to five.

## Why it matters

- Examples are one of the most reliable ways to control **format, tone and structure**.
- They convey **judgement on edge cases** that is hard to put into rules ("a complaint that mentions a refund but is
  really about delivery time goes under *delivery*").
- They make outputs **more consistent** across many runs, which matters for automation and evaluation.
- The Professional exam guide lists zero-shot, few-shot and chain-of-thought techniques as an explicit objective
  (CCAR-P-2.3). You should be able to say when each is the right choice.

## How it works

### When to use examples

| Situation | Start with | Why |
|---|---|---|
| Common task, flexible format (explain a concept) | Zero-shot | Claude already knows how; examples may narrow the answer unnecessarily |
| Strict or unusual format (house report style, specific labels) | Few-shot | Showing is faster and more precise than describing |
| Classification with fuzzy boundaries | Few-shot with boundary cases | Examples teach where the lines are |
| Brainstorming | Zero-shot, or examples that show variety | Similar examples cause similar ideas |
| Output that a program consumes | Structured outputs, optionally plus examples | A schema guarantees shape; examples teach content quality |

A reasonable default: try zero-shot with clear instructions first. Add examples when outputs are inconsistent or
the format keeps drifting.

### What makes a good example set

Anthropic's guidance asks for examples that are:

1. **Relevant.** They mirror your real inputs: same domain, length and messiness.
2. **Diverse.** They cover different cases, including edge cases, so Claude does not copy an accidental pattern. If
   every example is 50 words long and starts with "Dear customer", every output will too.
3. **Clearly marked.** Wrap each example in `<example>` tags, and the set in `<examples>`, so Claude knows they are
   illustrations, not part of the current task.

Three to five examples is the usual sweet spot. More can help with subtle classification but costs input tokens on
every call, so measure the benefit.

### Pitfalls examples can introduce

- **Over-copying.** Claude may reuse phrases or structure from examples verbatim. Vary wording across examples, and say
  "these show the format; do not reuse their wording".
- **Label imbalance.** If four of five classification examples are "low priority", Claude may lean that way.
  Balance the labels or explain the true distribution.
- **Stale examples.** When the policy changes, examples that reflect the old policy quietly override your new
  instructions. Version examples with the prompt.
- **Contradiction with instructions.** If an example breaks a rule you stated, Claude has to choose. Check every
  example against your instructions.

### Examples plus reasoning

For tasks that need judgement, an example can show the reasoning as well as the answer: a short `<reasoning>`
section followed by the `<label>`. This teaches the *why*, which generalises better than the label alone. With
[adaptive thinking](04-reasoning-and-thinking.md) on current models, you often do not need visible reasoning in
examples, but it remains useful when you want the reasoning in the output for reviewers.

### Getting help building examples

You can ask Claude to critique your example set for relevance and diversity, or to propose additional examples for
cases you have not covered. Review anything it generates before using it: synthetic examples can carry the model's
own blind spots.

### Examples in multi-turn form

Instead of putting examples in one block, you can supply earlier user and assistant turns that demonstrate the pattern.
This is useful in chat-style applications. Note that the final turn you send must be a `user` turn: current models do
not accept an assistant prefill as the last message (see [structured output](06-structured-output.md)).

## Example

The fictional *Tailspin Travel* support team triages incoming messages into four categories. Zero-shot results were
inconsistent on messages that mentioned several issues, so the team added boundary-case examples.

```python
import anthropic

client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY

SYSTEM = (
    "You triage customer messages for Tailspin Travel. Assign exactly one category: "
    "booking_change, payment, complaint or general_question. When a message mentions "
    "several issues, choose the one the customer needs resolved first."
)

EXAMPLES = """<examples>
<example>
<message>Can I move my flight from the 12th to the 14th? Same passengers.</message>
<category>booking_change</category>
</example>
<example>
<message>I was charged twice for the hotel in Lisbon and the room was also dirty.</message>
<category>payment</category>
<note>The double charge needs fixing first; the cleanliness issue is secondary.</note>
</example>
<example>
<message>Your agent hung up on me twice. This is unacceptable.</message>
<category>complaint</category>
</example>
<example>
<message>Do your packages include airport transfers?</message>
<category>general_question</category>
</example>
</examples>"""


def triage(message: str) -> str:
    response = client.messages.create(
        model="claude-haiku-5-5",  # a simple, high-volume task; validate quality with your evals
        max_tokens=50,
        output_config={"effort": "low"},
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"{EXAMPLES}\n\nClassify this message. Reply with the category name only.\n"
                       f"<message>{message}</message>",
        }],
    )
    if response.stop_reason != "end_turn":
        return "needs_review"
    label = next(b.text for b in response.content if b.type == "text").strip()
    allowed = {"booking_change", "payment", "complaint", "general_question"}
    return label if label in allowed else "needs_review"


print(triage("The app crashed while I was paying, and now I can't see my booking."))
```

> **Cost:** requires API credits (live mode).

Two design points: the code validates the label against an allow-list and routes anything else to review; and for a
production classifier you would likely move to a schema with an `enum` field, shown on the
[structured output](06-structured-output.md) page.

## Enterprise use case

*Riverbend Utilities* (fictional) drafts outage notices for customers. The communications team had a style guide, but
zero-shot drafts were too formal and too long. They curated four approved past notices covering a planned outage, an
emergency outage, a multi-day outage and an all-clear message, and wrapped them in `<example>` tags with the
instruction "match the tone, length and structure, not the wording".

Two lessons came out of their evaluation. First, the multi-day example had a long apology paragraph, and every draft
copied it, so they trimmed it. Second, when the regulator changed the required wording for estimated restoration
times, the old examples kept producing the old wording until the examples themselves were updated. They now version
examples in the same repository as the prompt and review both together.

## Common mistakes

- **Using only easy examples.** The examples that matter most are the borderline ones.
- **Too many near-identical examples.** They teach surface patterns, not the rule.
- **Forgetting the token cost.** Examples are re-sent on every request. Measure whether five examples beat three, and
  consider [prompt caching](../04-context-engineering/03-prompt-caching.md) for long, stable example sets.
- **Mixing examples with live input.** Without tags, Claude may treat an example as part of the task or answer it.
- **Using real customer data as examples.** Use synthetic or properly anonymised examples.

## Security considerations

- **Data protection.** Examples copied from production can contain personal data, which then appears in logs and
  prompts. Create synthetic examples or scrub them first.
- **Poisoned examples.** If examples are pulled dynamically (for example, the "most similar past cases" from a
  database), an attacker who can write to that store can steer outputs. Treat dynamic examples as untrusted input and
  restrict who can add them.
- **Behaviour leakage.** Examples that show the model revealing internal notes or system details teach it to do so.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Outputs copy example wording | Examples too uniform | Vary phrasing; instruct "match format, not wording" |
| Classifier favours one label | Imbalanced examples | Balance labels or state the expected distribution |
| New policy ignored | Old examples contradict it | Update or remove outdated examples |
| Claude answers an example instead of the task | Examples not clearly separated | Wrap in `<examples>`; put the live input in its own tag after them |
| No improvement over zero-shot | Examples not representative | Use real-shaped (synthetic) inputs, especially hard cases |

## Check your understanding

1. When would you choose zero-shot over few-shot for a task?
2. Give two properties a good example set should have, and the failure each prevents.
3. Why must example sets be versioned along with the prompt?
4. A dynamic few-shot system retrieves past tickets as examples. What new risk does this introduce?

<details>
<summary>Answers</summary>

1. When the task is common and the format flexible (explaining, summarising in a general way), or for brainstorming
   where examples might narrow the ideas. Start zero-shot and add examples when output is inconsistent.
2. Relevance (mirrors real inputs, so Claude learns the right patterns) and diversity (varied cases and wording, so
   Claude does not copy accidental surface features). Clear tagging is the third property; it stops Claude confusing
   examples with the live task.
3. Examples encode policy and style. If the policy changes but the examples do not, the examples can override the new
   instructions.
4. Example poisoning: anyone who can write to the source of examples can influence outputs. Restrict write access,
   filter retrieved examples, and treat them as untrusted input.

</details>

## Further reading

- [Prompting best practices: use examples effectively](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) (Anthropic docs)
- [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) (Anthropic docs)
- [Building evaluation datasets](../14-evaluation-and-testing/03-building-eval-datasets.md) in this repository
- Next page: [Reasoning and thinking](04-reasoning-and-thinking.md)
