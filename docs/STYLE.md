# Documentation Standards

These standards keep the repository consistent, accurate and safe to publish. Every
contribution, human or AI-assisted, follows them. CI enforces the mechanical parts.

## 1. Accuracy and sourcing

1. **Official sources first.** Prefer, in order: the official exam guides, `platform.claude.com/docs`,
   `code.claude.com/docs`, `modelcontextprotocol.io`, `support.claude.com`, `anthropic.com/engineering`,
   then OWASP / NIST / other standards bodies. Community material is supporting evidence only.
2. **Exam facts live in one place.** Item counts, fees, pass marks, domains and weights come from
   [`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml). Any page that
   states an exam fact links to the registry or to [`exam-facts.md`](../25-official-resources/exam-facts.md).
   `tools/check_exam_claims.py` enforces this.
3. **Label anything unverified.** If you cannot confirm a fact against an official source, write
   `> **Unverified:** …` and explain what is uncertain. Never invent exam details.
4. **Date-sensitive facts carry a date.** Model names, prices, context windows and feature availability
   change. Write them as "as of 2026-10-24" and link to the live page (models overview, pricing).
5. **Current API rules** (as of 2026-10-24) that examples must respect:
   - Model IDs: `claude-opus-5-5` (default), `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-fable-5-1`.
     No date suffixes.
   - Do not send `temperature`, `top_p` or `top_k`. They are not supported on current models.
   - No assistant-message prefill. Use structured outputs (`output_config.format` or
     `client.messages.parse(...)`) or instructions to shape output.
   - `tool_choice` of `any` or `tool` is rejected on current models. Use `auto` plus a clear instruction,
     `strict: true` tools, or structured outputs.
   - Thinking is adaptive (`thinking={"type": "adaptive"}` or omitted). Depth is tuned with
     `output_config={"effort": "low" | "medium" | "high" | "xhigh" | "max"}`. `budget_tokens` is legacy.
   - Prompt caching is a prefix match: stable content first, `cache_control` breakpoints, check
     `usage.cache_read_input_tokens`.
   - Always check `stop_reason` (`end_turn`, `max_tokens`, `tool_use`, `pause_turn`, `refusal`) before
     using `content`.

## 2. Original work and intellectual property

- Write every explanation, example, diagram and question yourself. **Do not copy** tutorials, courses,
  repository docs, blog posts, diagrams or question banks, and do not lightly reword them.
- **Never** reproduce, reconstruct or "remember" real exam questions. Do not reuse or paraphrase the sample
  questions printed in the official exam guides. Anthropic's exam policy treats exam content as confidential.
- Quote sparingly (a sentence at most), in quotation marks, with attribution and a link.
- Link to official resources rather than restating them at length.
- Use fictional organisations (e.g. *Northwind Lending*, *Contoso Health*, *Acme Logistics*) and synthetic data.
  No real customer data, no real personal data, and no names of real employers.

## 3. Teaching structure for a topic page

Each concept page in modules `00`–`15` uses these headings, in this order. Merge or omit a heading only
when it truly does not apply, and avoid repeating material covered elsewhere. Link to it instead.

```markdown
# <Topic>
> **Level:** Beginner | Intermediate | Advanced · **Time:** ~N min · **Exam relevance:** CCAO-F D3, CCAR-P D2

## In plain English          <!-- beginner-friendly explanation, analogy welcome -->
## Why it matters
## How it works             <!-- technical explanation -->
## Example                  <!-- practical, runnable or copy-pasteable -->
## Enterprise use case      <!-- fictional organisation -->
## Common mistakes
## Security considerations
## Troubleshooting
## Check your understanding <!-- 3–5 questions, answers in a <details> block -->
## Further reading          <!-- official docs first -->
```

Each module folder has a `README.md` that gives the learning objectives, the page order, prerequisites,
exam relevance (objective IDs) and a "next module" link.

## 4. Writing style

- Plain, direct English. Spell out acronyms the first time they appear in a page.
- Second person ("you"), active voice, short paragraphs.
- Use tables for comparisons and Mermaid (` ```mermaid `) for diagrams. GitHub renders both natively.
- Code blocks always carry a language tag. Python is the primary language. Include TypeScript or cURL only
  where it adds something.
- Relative links only for files inside the repository; link targets must exist (`tools/check_links.py`).
- No marketing language, no emojis in body text, no fabricated statistics or quotes.

## 5. Code standards

- Python 3.10+ (3.11+ for the optional MCP server in lab 09, because the `mcp` v2 SDK requires it). Labs import the shared helper `19-hands-on-labs/common/claude_lab.py`, so they run offline in
  **mock mode** by default and against the real API with `CLAUDE_LAB_MODE=live`.
- **Never hardcode credentials.** Read them from environment variables, and ship a `.env.example` with
  placeholder values. Real `.env` files are git-ignored.
- Every runnable sample has a test in `tests/` or is executed by `tools/run_lab_smoke.py` in mock mode.
- Mark any step that costs money: `> **Cost:** requires API credits (live mode).`
- Treat model output as untrusted input: validate before acting on it, never `eval` it, and escape it before rendering.

## 6. Practice questions

See [`17-practice-questions/README.md`](../17-practice-questions/README.md). In short: JSON matching
the schema, one file per domain, unique IDs, every distractor explained, every question mapped to an
objective and a module, and every question marked unofficial.

## 7. Review checklist (copied into the PR template)

- [ ] Original wording; no copied or reconstructed exam content
- [ ] Facts checked against official sources; date-sensitive facts dated; unverified facts labelled
- [ ] Links resolve (`python tools/validate_all.py`)
- [ ] Code runs in mock mode; no secrets; costs flagged
- [ ] Security considerations included where relevant
