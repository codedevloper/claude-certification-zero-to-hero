# CCAR-F Decision Scenarios

> Fourteen original configuration and design case studies with options analysis and a recommended decision. They
> are written for this repository, use fictional organisations and are **not** exam questions or reconstructions of
> exam content. Objective IDs refer to [`registry.yaml`](../registry.yaml). Product facts are as of 2026-10-24.

How to use: read the context and constraints, choose an option yourself *before* reading the analysis, and write
one sentence of rationale. The skill being trained is spotting where a rule is enforced, what each agent can see,
and which configuration fits the stated constraint.

| # | Scenario | Objectives |
|---|---|---|
| 1 | The loop that stops too early | 1.1 |
| 2 | Research coordinator that always fans out | 1.2, 1.3 |
| 3 | Synthesiser with no citations | 1.3, 5.6 |
| 4 | Warranty claims need a serial number first | 1.4, 1.5 |
| 5 | Two backends, two date formats | 1.5, 5.1 |
| 6 | Resume after a weekend of refactoring | 1.7 |
| 7 | Twenty-two tools on one agent | 2.1, 2.3 |
| 8 | Upgrade breaks forced tool calls | 2.3, 4.3 |
| 9 | Where the team's MCP server belongs | 2.4 |
| 10 | Conventions that span forty packages | 3.1, 3.3 |
| 11 | A skill that floods the conversation | 3.2, 5.4 |
| 12 | Review comments developers ignore | 4.1, 4.2, 3.6 |
| 13 | Supplier invoices with missing fields | 4.3, 4.4 |
| 14 | Overnight audit on a deadline | 4.5 |

---

## Scenario 1 — The loop that stops too early

**Context.** *Acme Logistics'* manual agent loop sometimes returns "I'll look that up for you" as the final answer.
The loop ends when the response contains a text block.

| Option | Analysis |
|---|---|
| A. Add "never reply until you have the answer" to the system prompt | Treats a control-flow bug as a prompting issue; Claude legitimately writes text before tool calls. |
| B. Branch on `stop_reason`: continue on `tool_use`, finish on `end_turn`, handle others explicitly | Fixes the root cause; text plus `tool_use` in one turn is normal. |
| C. Always run five iterations | Arbitrary; wastes calls on simple questions and truncates complex ones. |
| D. Search the text for "look that up" and continue | Brittle natural-language parsing. |

**Recommended decision: B.** Keep a turn or budget cap only as a safety net.

---

## Scenario 2 — Research coordinator that always fans out

**Context.** *Fabrikam Labs'* coordinator invokes all four subagents (search, read, synthesise, write) for every
question, including "what year was the standard first published?". Costs are high and simple answers are slow.

| Option | Analysis |
|---|---|
| A. Remove the coordinator and hard-code the pipeline | Makes every question pay full cost; loses adaptivity. |
| B. Tell the coordinator to assess each request and invoke only the subagents it needs, with examples of simple and complex questions | Model-driven selection; cheap questions stay cheap. |
| C. Use a smaller model for every subagent | May lower cost but does not stop unnecessary work. |
| D. Cap the coordinator at one subagent per run | Breaks genuinely complex research. |

**Recommended decision: B**, with spend and concurrency limits as a backstop.

---

## Scenario 3 — Synthesiser with no citations

**Context.** Readers return excellent findings with sources, but the synthesiser's report has no citations and
occasionally merges two sources' figures.

| Option | Analysis |
|---|---|
| A. Instruct the synthesiser to "always cite sources" | It cannot cite what it never received. |
| B. Have readers return structured claim records (claim, source, location, excerpt, date) and pass all of them into the synthesiser's brief; require it to keep the mapping and flag conflicts | Provenance travels as data; conflicts become visible. |
| C. Let the synthesiser call the search tools again | Duplicates work and gives an off-role agent search tools. |
| D. Fork the readers' sessions into the synthesiser | Imports bulky history instead of a clean, structured hand-off. |

**Recommended decision: B.** Subagents only know what their brief contains.

---

## Scenario 4 — Warranty claims need a serial number first

**Context.** *Contoso Appliances'* agent must confirm a product serial number with `verify_serial` before calling
`create_warranty_claim`. The system prompt says so; audits find about 2% of claims created without verification.

| Option | Analysis |
|---|---|
| A. Repeat the rule in capitals in the system prompt | Lowers the rate, does not remove it. |
| B. A `PreToolUse` hook that denies `create_warranty_claim` until `verify_serial` succeeded in this session, with a reason telling Claude what to do | Deterministic; the denial guides recovery. |
| C. Remove `verify_serial` and verify inside `create_warranty_claim` | Also enforces, but loses the separate step the agent uses to talk to the customer about mismatches; acceptable if the server check is the only requirement. |
| D. Review a weekly sample | Detects after the fact. |

**Recommended decision: B** (or server-side enforcement as in C, ideally both). Requirements that must always hold
belong in code.

---

## Scenario 5 — Two backends, two date formats

**Context.** One MCP server returns delivery times as epoch seconds, another as local-time strings with offsets.
The agent occasionally tells customers the wrong day.

| Option | Analysis |
|---|---|
| A. Add a prompt paragraph explaining both formats | Relies on the model converting correctly every time. |
| B. A `PostToolUse` hook that converts both to ISO 8601 UTC (with a local display field) before Claude sees them | Deterministic normalisation at the boundary. |
| C. Ask both teams to change their APIs | Right long term, slow, and other consumers may depend on the formats. |
| D. Switch to a more capable model | Does not address the inconsistency. |

**Recommended decision: B**, and raise C as a backlog item.

---

## Scenario 6 — Resume after a weekend of refactoring

**Context.** On Friday a named session analysed the payments module. Over the weekend a teammate renamed three
classes and moved two files. On Monday you want to continue.

| Option | Analysis |
|---|---|
| A. `claude --resume payments-audit` and carry on | The agent trusts stale reads of moved and renamed code. |
| B. Resume and tell the agent exactly which files and classes changed so it re-reads them | Efficient when most earlier analysis still holds. |
| C. Start fresh with a summary of Friday's conclusions that still hold | Best when much of the earlier context is stale. |
| D. Fork Friday's session | Creates a branch with the same stale context. |

**Recommended decision: B**, because only a few files changed. If the refactor had touched most of the module, C.

---

## Scenario 7 — Twenty-two tools on one agent

**Context.** *Northwind Freight's* operations agent has 22 tools across four MCP servers. It often calls
`search_documents` when it should call `search_shipments`, and occasionally uses an admin tool it should never need.

| Option | Analysis |
|---|---|
| A. Add a long paragraph to the system prompt listing which tool to use when | Helps a little; descriptions remain ambiguous and the admin tool remains available. |
| B. Split into role-specific agents with four to six tools each, rename and rewrite overlapping descriptions, and remove the admin tool from this agent | Better selection and least privilege. |
| C. Use a larger model | May improve selection, does not remove the dangerous tool. |
| D. Keep all tools but list the admin tool in `allowedTools` so it does not prompt | The opposite of what is needed: `allowedTools` approves, it does not restrict. |

**Recommended decision: B.**

---

## Scenario 8 — Upgrade breaks forced tool calls

**Context.** A classification step used `tool_choice: {"type": "tool", "name": "record_label"}` on an older model.
After switching to Claude Opus 5.5 every request returns a 400.

| Option | Analysis |
|---|---|
| A. Switch to `tool_choice: {"type": "any"}` | Also returns a 400 on Opus 5.5. |
| B. Use `tool_choice: auto`, instruct Claude to call `record_label`, set `strict: true`, and check a call was made | Keeps the tool-based design within current model rules. |
| C. Replace the tool with structured outputs (`output_config.format`) since the call existed only to return JSON | Simpler if no action is involved. |
| D. Move this step to Claude Haiku 5.5, which still accepts forced tool use | Valid if Haiku's quality meets the bar; decide on eval results, not on the error. |

**Recommended decision: C** if the step only needs data back; otherwise **B**. D is a legitimate option when the
eval supports it.

---

## Scenario 9 — Where the team's MCP server belongs

**Context.** Every engineer at *Litware* needs the internal incident-tracker MCP server in Claude Code. It needs a
bearer token. One engineer also wants to try an experimental notes server.

| Option | Analysis |
|---|---|
| A. Each engineer adds the tracker at user scope | Inconsistent setups; onboarding friction. |
| B. Commit `.mcp.json` with the token in plain text | Leaks a secret into git. |
| C. Commit `.mcp.json` (project scope) with `Authorization: Bearer ${TRACKER_TOKEN}`; the experimental server goes in the engineer's user scope | Shared, secret-free, personal experiments stay personal. |
| D. Put the tracker in managed settings for the whole company | Possible for organisation-wide servers, but heavier than needed for one team. |

**Recommended decision: C.**

---

## Scenario 10 — Conventions that span forty packages

**Context.** A monorepo has 40 packages. Test-file conventions apply to every `*.spec.ts` file wherever it lives.
Someone has started copying a `CLAUDE.md` into each package.

| Option | Analysis |
|---|---|
| A. Keep copying subdirectory CLAUDE.md files | Forty copies to maintain; drift guaranteed. |
| B. Put the conventions in the root CLAUDE.md | Loads them into every session, including ones that never touch tests. |
| C. A `.claude/rules/testing.md` with `paths: ["**/*.spec.ts"]` | One file; loads only when a matching file is touched. |
| D. A `/test-conventions` skill developers must remember to run | Depends on people remembering. |

**Recommended decision: C.**

---

## Scenario 11 — A skill that floods the conversation

**Context.** A `/map-dependencies` skill reads dozens of files and prints long tables. After running it, the main
session's answers get vaguer.

| Option | Analysis |
|---|---|
| A. Run `/compact` after each use | Treats the symptom and loses detail. |
| B. Add `context: fork` (with `agent: Explore`) so the skill runs in a subagent and returns a summary | Isolates verbose output; main context stays clean. |
| C. Ask the skill to print less | Helps a little; the file reads still happen in the main context. |
| D. Move the content into CLAUDE.md | Loads it into every session. |

**Recommended decision: B.** Remember forked skills run in the background by default; set `background: false` if
the conversation must wait.

---

## Scenario 12 — Review comments developers ignore

**Context.** *Litware's* CI review posts about 25 comments per PR. Developers say most are style nitpicks and
dismiss them all, including real bugs. The prompt says "report only high-confidence, important issues".

| Option | Analysis |
|---|---|
| A. Change the wording to "report only very high-confidence issues" | Still no definition of what counts. |
| B. Explicit report/skip criteria, severity definitions with examples, few-shot pairs of acceptable vs problematic code, and temporarily disable the noisiest category | Directly targets precision and rebuilds trust. |
| C. Cap the output at five comments | Drops real issues arbitrarily. |
| D. Ask the same session that generated the code to review it | Self-review is weaker, and it does not fix criteria. |

**Recommended decision: B**, and record a `rule_id` on each finding to see which rules get dismissed.

---

## Scenario 13 — Supplier invoices with missing fields

**Context.** *Adventure Works* extracts invoice data with a strict schema in which `purchase_order` is required.
About 8% of invoices have no purchase order, and the pipeline sometimes outputs a plausible-looking but invented one.

| Option | Analysis |
|---|---|
| A. Add "do not invent values" to the prompt | Helps, but the schema still demands a value. |
| B. Make `purchase_order` nullable, instruct "null when absent", add an example invoice without one, and route nulls to the right queue | Removes the pressure to invent; handles the business case. |
| C. Retry until a value appears | The value is not in the document; retries cannot produce it. |
| D. Remove the field | Loses data the 92% of invoices do contain. |

**Recommended decision: B.**

---

## Scenario 14 — Overnight audit on a deadline

**Context.** *Contoso Health* audits about 18,000 synthetic policy documents. Results are needed within 40 hours
of each document's arrival; documents arrive all day. A pre-merge lint check on the policy repository also runs on
Claude.

| Option | Analysis |
|---|---|
| A. Run both through the Message Batches API | The pre-merge check blocks developers; batches can take up to 24 hours. |
| B. Synchronous API for the pre-merge check; batches for the audit, submitted at least every 16 hours (40 − 24), matched by `custom_id`, failures re-submitted individually after a prompt tuned on a sample | Matches each workload to its latency need; half price for the bulk work. |
| C. Synchronous API for everything | Works, at roughly twice the token cost for the audit. |
| D. One batch per day for the audit | A document arriving just after submission could wait up to 48 hours. |

**Recommended decision: B.** Leave margin below the 16-hour interval for retries.

---

See the [scenario study guide](scenarios.md) for how these themes map to the six exam scenarios, and the
[common misconceptions](common-misconceptions.md) for the beliefs behind the wrong options.
