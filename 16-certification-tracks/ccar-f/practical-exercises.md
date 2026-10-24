# CCAR-F Practical Exercises

> Hands-on build exercises that map to CCAR-F objectives in [`registry.yaml`](../registry.yaml). They are original
> to this repository, use fictional organisations and synthetic data, and are not the preparation exercises
> printed in the official exam guide. Product facts are as of 2026-10-24.

CCAR-F rewards people who have actually built these things. Each exercise produces something you can run or
inspect. Work in a scratch folder of your own (for example `my-ccar-f-work/`). Where an exercise uses a lab, run
the lab in mock mode first (`CLAUDE_LAB_MODE=mock`, the default) and switch to live mode only when you want real
model behaviour.

> **Cost:** requires API credits (live mode). Exercises 1–3 and 7 need live calls to see real model behaviour;
> the others can be done with Claude Code on your own subscription or in mock mode.

| # | Exercise | Objectives | Deliverable | Time |
|---|---|---|---|---|
| 1 | A correct agent loop, then break it | 1.1, 2.2 | Loop script plus a failure log | 90 min |
| 2 | Coordinator with two subagents | 1.2, 1.3, 2.3, 5.6 | Agent SDK script and a hand-off schema | 2 h |
| 3 | Guardrail hooks | 1.4, 1.5, 5.2 | Two hooks with tests | 90 min |
| 4 | An MCP server with structured errors | 2.1, 2.2, 2.4 | Server, `.mcp.json`, test transcript | 2 h |
| 5 | Team Claude Code configuration | 3.1, 3.2, 3.3 | CLAUDE.md, rules, two skills | 90 min |
| 6 | CI review job | 3.6, 4.1, 4.2, 4.6 | CI script, schema, prompt, precision log | 2 h |
| 7 | Extraction pipeline with validation and batches | 4.3, 4.4, 4.5, 5.5 | Pipeline script and accuracy report | 3 h |
| 8 | Long-session context drill | 1.7, 5.1, 5.4 | Session log, scratchpad, comparison notes | 60 min |

---

## Exercise 1 — A correct agent loop, then break it (CCAR-F-1.1, 2.2)

**Scenario.** *Acme Logistics* wants a small agent that answers "where is my shipment?" using two client tools:
`lookup_shipment(tracking_id)` and `lookup_depot(depot_code)`, both backed by a local JSON file of synthetic data.

**Tasks.**

1. Write a manual loop on the Messages API that branches on `stop_reason` (`tool_use` → run tools and append all
   results in one user message; `end_turn` → finish; anything else → handle explicitly). Use
   [Lab 08](../../19-hands-on-labs/lab-08-tool-invocation/README.md) as a starting point.
2. Make `lookup_depot` fail for one depot code with `is_error: true` and a message that says the code format is
   wrong and gives the right format. Confirm Claude corrects the argument.
3. Deliberately introduce three bugs, one at a time, and record what happens: (a) stop when the response contains
   any text; (b) append only the text of the assistant turn; (c) split two parallel tool results across two user
   messages.

**Deliverable.** `agent_loop.py` and `failure-log.md` describing each bug's symptom.

**Success criteria.** The correct loop handles multi-tool turns and the error case; the log explains why each bug
fails (early stop, lost `tool_use` IDs, degraded parallel calling).

---

## Exercise 2 — Coordinator with two subagents (CCAR-F-1.2, 1.3, 2.3, 5.6)

**Scenario.** *Fabrikam Labs* wants a brief on "heat-pump adoption barriers in three fictional regions" built from
a folder of synthetic reports you write yourself (six short Markdown files with dates and a deliberate conflict
between two figures).

**Tasks.**

1. With the Agent SDK, define a `reader` subagent (`tools=["Read", "Grep", "Glob"]`) and a `synthesiser` subagent
   (no file tools). Give each a precise `description`.
2. Define the reader's output as claim records: `claim`, `source_file`, `section`, `excerpt`, `published`.
3. Have the coordinator delegate one reader per region **in a single turn** (check the trace for parallel Agent
   tool calls), then pass all claim records to the synthesiser.
4. Require the synthesiser to separate established from contested findings and to show the conflicting figures
   with both sources.

**Deliverable.** `research_coordinator.py`, `claim-record.schema.json`, and the generated brief.

**Success criteria.** Every statement in the brief traces to a claim record; the conflict is shown, not resolved
by guesswork; `allowed_tools` is used only for approvals and the readers' tool lists do the restricting.

---

## Exercise 3 — Guardrail hooks (CCAR-F-1.4, 1.5, 5.2)

**Scenario.** *Contoso Outfitters'* support agent has MCP tools `find_account`, `get_order`, `issue_credit` and
`open_handoff`. Policy: credits require a verified account and may not exceed 150.00 without a supervisor.

**Tasks.**

1. Write a `PreToolUse` hook for `issue_credit` that denies the call unless `find_account` returned
   `verified: true` earlier in the same session (track this in your own state keyed by `session_id`).
2. In the same hook, deny amounts above 150.00 with a reason that tells Claude to use `open_handoff`.
3. Write a `PostToolUse` hook for `get_order` that converts epoch-second timestamps to ISO 8601 and drops fields
   the agent never needs (use `updatedToolOutput`).
4. Write unit tests that call the hook functions directly with synthetic inputs.

**Deliverable.** `hooks.py`, `test_hooks.py` and a short note on what the hooks cannot catch (for example, the
same action reached through a different tool).

**Success criteria.** Tests pass in mock mode; you can explain why these rules are hooks rather than prompt text.

---

## Exercise 4 — An MCP server with structured errors (CCAR-F-2.1, 2.2, 2.4)

**Scenario.** *Northwind Freight* wants an MCP server over a synthetic parts catalogue.

**Tasks.**

1. Build a server (see [Lab 09](../../19-hands-on-labs/lab-09-mcp-fundamentals/README.md)) with
   `search_parts(query, category?)` and `get_part(part_number)`. Write descriptions that state when to use each,
   input formats with an example, and what an empty result means.
2. Return tool execution errors with `isError: true` and a JSON payload carrying your convention:
   `error_category` (`transient`, `validation`, `business_rule`, `permission`), `retryable` and a message.
   Return zero matches as a successful empty list.
3. Expose the category list as an MCP **resource**.
4. Register it in a project `.mcp.json` using `${PARTS_API_TOKEN}`, and register a second, personal server at user
   scope. Confirm both appear in `/mcp`.
5. Test selection with five ambiguous prompts and record which tool Claude chose.

**Deliverable.** Server code, `.mcp.json`, and `selection-test.md`.

**Success criteria.** No secrets in the repository; errors let Claude recover sensibly; selection is correct on at
least four of five prompts after you improve the descriptions.

---

## Exercise 5 — Team Claude Code configuration (CCAR-F-3.1, 3.2, 3.3)

**Scenario.** Take any repository you own (or create a small polyglot one) and configure it as if 30 engineers
will use Claude Code on it.

**Tasks.**

1. Write a short project `CLAUDE.md` (under 60 lines) with purpose, commands and pointers.
2. Move topic guidance into `.claude/rules/`: one unconditional rule and two path-scoped rules, one of which
   targets a file type spread across directories (for example `**/*.spec.ts`).
3. Create a skill with `argument-hint` and `disable-model-invocation: true` (for a release task), and a skill with
   `context: fork` and `agent: Explore` (for a codebase survey). Give the survey skill `disallowed-tools: Write, Edit`.
4. Put one personal preference in `~/.claude/CLAUDE.md` and confirm with `/memory` which files load.
5. Open a file matching each path-scoped rule and confirm the rule loads (an `InstructionsLoaded` hook can log it).

**Deliverable.** The configuration files and `verification.md` with what you observed.

**Success criteria.** Nothing personal is committed; path-scoped rules load only on matching files; you can state
the difference between `allowed-tools` and `disallowed-tools`.

---

## Exercise 6 — CI review job (CCAR-F-3.6, 4.1, 4.2, 4.6)

**Scenario.** *Litware's* platform team wants automated PR review that developers trust.

**Tasks.**

1. Write `findings.schema.json` with `file`, `line`, `severity`, `category`, `rule_id`, `message`,
   `suggested_fix`.
2. Write review instructions with explicit report/skip criteria, severity definitions with a code example each,
   and three few-shot pairs (acceptable pattern vs genuine issue).
3. Write a CI script that runs `claude --bare -p ... --output-format json --json-schema ...` with read-only tools
   and `--max-turns`, reads `structured_output` and checks it exists.
4. Add a re-run mode that passes the previous findings and asks for new or unresolved issues only.
5. Run it on five synthetic diffs; label each finding true or false positive; compute precision per category;
   disable the worst category and re-run.

**Deliverable.** Script, schema, instructions, and `precision-log.md`.

**Success criteria.** Output parses every time; precision improves after tightening criteria; the review runs in a
separate invocation from any code generation.

---

## Exercise 7 — Extraction pipeline with validation and batches (CCAR-F-4.3, 4.4, 4.5, 5.5)

**Scenario.** *Litware Insurance* receives synthetic claim letters (write 30 short ones in varied layouts,
including some missing a policy number and two whose itemised costs do not add up).

**Tasks.**

1. Define a schema with nullable optional fields, an `incident_type` enum with `"other"` and
   `incident_type_detail`, and per-field confidence.
2. Extract with `output_config.format` on the current default model; check `stop_reason` before parsing.
3. Write semantic validators (sum of items equals claimed total; dates in order). Retry once with the specific
   errors; do not retry when the data is absent.
4. Re-run the full set through the Message Batches API with `custom_id = letter_id`; match results by
   `custom_id`; re-submit only failures.
5. Hand-label the 30 letters and report accuracy per field and per layout; pick a confidence threshold per field.

**Deliverable.** `pipeline.py`, `validators.py`, and `accuracy-report.md`.

**Success criteria.** No invented policy numbers; inconsistent letters are flagged; the report shows at least one
layout or field that is weaker than the overall average.

---

## Exercise 8 — Long-session context drill (CCAR-F-1.7, 5.1, 5.4)

**Scenario.** Explore an unfamiliar open-source repository with Claude Code for about 45 minutes.

**Tasks.**

1. Start a named session (`claude -n "repo-tour"`). Delegate two discovery questions to the Explore subagent.
2. Keep a scratchpad file of findings; ask Claude to update it after each phase.
3. Run `/compact` midway and check which facts survived in the conversation versus the scratchpad.
4. Change two files yourself, then resume the session with `claude --resume repo-tour` and tell Claude exactly
   which files changed.
5. Fork the session with `--fork-session` to explore an alternative refactoring idea; confirm the original is
   untouched.

**Deliverable.** `session-notes.md` comparing what was retained or lost at each step.

**Success criteria.** You can explain when to resume, when to fork and when to start fresh with a summary.

---

Next: test your judgement with the [decision scenarios](decision-scenarios.md), then the
[readiness assessment](readiness-assessment.md).
