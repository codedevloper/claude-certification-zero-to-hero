# 19 · Hands-On Labs

Twenty practical labs, from your first API call to a secure enterprise AI gateway. Every lab runs in two modes:

| Mode | How | Cost | Use it to |
|---|---|---|---|
| **Mock** (default) | `CLAUDE_LAB_MODE=mock` | Free, offline | Learn the code path and run the self-checks. CI runs every lab this way. |
| **Live** | `CLAUDE_LAB_MODE=live` plus an API key | Uses API credits | See real model behaviour |

> **Cost:** live mode calls the Claude API and is billed to your account. Most labs make a handful of short requests;
> each lab README states what live mode does. Set a spend limit in the Console before experimenting.

## Setup (once)

```bash
# from the repository root
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt                 # repo tooling
pip install -r 19-hands-on-labs/requirements.txt    # only needed for live mode
cp 19-hands-on-labs/.env.example 19-hands-on-labs/.env   # optional; .env is git-ignored
```

For live mode, provide credentials through the environment, never in code:

```bash
export CLAUDE_LAB_MODE=live
export ANTHROPIC_API_KEY=...   # or run `ant auth login`; the SDK picks up the active profile
```

Run a lab:

```bash
python 19-hands-on-labs/lab-01-first-claude-interaction/lab.py
```

Run them all in mock mode (as CI does):

```bash
python tools/run_lab_smoke.py
```

## How the labs work

All labs import [`common/claude_lab.py`](common/claude_lab.py). It provides:

- `get_client()`: the real `anthropic.Anthropic()` client in live mode, or a deterministic offline mock in mock mode.
- `register_mock(fn)`: each lab registers realistic canned responses, so mock mode exercises the same code path.
- Guardrails that mirror the current API: the mock rejects `temperature`, `top_p`, `top_k`, assistant prefill and forced
  `tool_choice`, so mistakes surface offline before they cost money.
- `MODEL` (default `claude-opus-5-5`) and `FAST_MODEL` (default `claude-haiku-5-5`), overridable via environment variables.

## Lab catalogue

| # | Lab | Level | You will learn | Main modules |
|---|---|---|---|---|
| 01 | [First Claude interaction](lab-01-first-claude-interaction/README.md) | Beginner | Messages, system prompts, stop reasons, usage | [06](../06-claude-api/README.md) |
| 02 | [Prompt improvement](lab-02-prompt-improvement/README.md) | Beginner | Iterating a prompt against a rubric | [03](../03-prompt-engineering/README.md) |
| 03 | [Structured outputs](lab-03-structured-outputs/README.md) | Beginner | JSON Schema outputs and validation | [03](../03-prompt-engineering/06-structured-output.md) |
| 04 | [Document-grounded Q&A](lab-04-document-grounded-qa/README.md) | Beginner | Quote-first grounding; saying "not found" | [04](../04-context-engineering/02-managing-long-context.md) |
| 05 | [Context management](lab-05-context-management/README.md) | Intermediate | Token counting, summarising, caching layout | [04](../04-context-engineering/README.md) |
| 06 | [Model comparison](lab-06-model-comparison/README.md) | Intermediate | Quality, latency and cost trade-offs | [05](../05-claude-products-and-models/03-model-selection.md) |
| 07 | [API integration](lab-07-api-integration/README.md) | Intermediate | Retries, timeouts, request IDs, streaming | [06](../06-claude-api/06-errors-rate-limits-retries.md) |
| 08 | [Tool invocation](lab-08-tool-invocation/README.md) | Intermediate | The tool-use loop, validation, errors | [07](../07-tool-use-and-function-calling/README.md) |
| 09 | [MCP fundamentals](lab-09-mcp-fundamentals/README.md) | Intermediate | MCP handshake, tools, allow-lists | [08](../08-model-context-protocol/README.md) |
| 10 | [Claude Code workflows](lab-10-claude-code-workflows/README.md) | Intermediate | CLAUDE.md, permissions, hooks, commands | [09](../09-claude-code/README.md) |
| 11 | [RAG pipeline](lab-11-rag-pipeline/README.md) | Intermediate | Chunking, BM25, retrieval metrics, citations | [11](../11-rag-and-knowledge-systems/README.md) |
| 12 | [Agentic task execution](lab-12-agentic-task-execution/README.md) | Advanced | Bounded agent loops and traces | [10](../10-agentic-ai/03-the-agent-loop.md) |
| 13 | [Human-in-the-loop approvals](lab-13-human-in-the-loop/README.md) | Advanced | Risk-tiered actions and approval gates | [10](../10-agentic-ai/05-human-in-the-loop.md) |
| 14 | [Prompt injection testing](lab-14-prompt-injection-testing/README.md) | Advanced | A defensive test harness for injection | [12](../12-ai-security/02-prompt-injection.md) |
| 15 | [Sensitive data protection](lab-15-sensitive-data-protection/README.md) | Advanced | PII detection, redaction, tokenisation | [12](../12-ai-security/04-data-exfiltration-and-disclosure.md) |
| 16 | [Evaluation framework](lab-16-evaluation-framework/README.md) | Advanced | Golden sets, graders, LLM-as-judge, A/B | [14](../14-evaluation-and-testing/README.md) |
| 17 | [Cost optimisation](lab-17-cost-optimisation/README.md) | Intermediate | Caching, batch and routing economics | [15](../15-production-operations/03-cost-optimisation.md) |
| 18 | [Reliability engineering](lab-18-reliability-engineering/README.md) | Advanced | Backoff, circuit breakers, fault injection | [15](../15-production-operations/05-reliability-engineering.md) |
| 19 | [Observability](lab-19-observability/README.md) | Advanced | Structured logs, spans, metrics, redaction | [15](../15-production-operations/02-observability.md) |
| 20 | [Secure enterprise AI architecture](lab-20-secure-enterprise-architecture/README.md) | Advanced | An AI gateway combining labs 13–19 | [13](../13-enterprise-ai-architecture/README.md), [12](../12-ai-security/README.md) |

Suggested paths: **business users (CCAO-F)** take labs 01–06; **architects (CCAR-P)** take all twenty, focusing on 08–20;
**security engineers** take 08, 09, 13–15 and 18–20.

## Lab conventions

Each lab README has the same sections: Objective; Level, time and cost; Prerequisites; Architecture; Setup; Walkthrough;
Synthetic test data; Execution steps; Expected results; Troubleshooting; Security considerations; Cleanup; Exam relevance.

- All data is synthetic and every organisation is fictional.
- No credentials are ever stored in the repository. `tools/scan_secrets.py` and gitleaks enforce this in CI.
- Treat model output as untrusted input. Labs validate it before acting on it.
- Problems? See [24-troubleshooting/labs-and-repository.md](../24-troubleshooting/labs-and-repository.md).
