# Content Map

The canonical list of planned files. Use these exact paths when cross-linking, mapping
objectives (`objective-map.yaml`) or setting a question's `module` field. If you add a file,
add it here as well.

## Learning modules (00–15)

| Module | Files |
|---|---|
| `00-getting-started/` | `README.md`, `how-to-use-this-repo.md`, `environment-setup.md`, `choose-your-path.md`, `roadmaps/README.md`, `roadmaps/7-day-accelerated.md`, `roadmaps/15-day-preparation.md`, `roadmaps/30-day-structured.md`, `roadmaps/60-day-comprehensive.md`, `roadmaps/90-day-enterprise-engineering.md` |
| `01-ai-and-llm-fundamentals/` | `README.md`, `01-what-is-ai.md`, `02-generative-ai.md`, `03-large-language-models.md`, `04-tokens-and-tokenisation.md`, `05-context-windows.md`, `06-hallucinations.md`, `07-capabilities-and-limitations.md` |
| `02-claude-fundamentals/` | `README.md`, `01-how-claude-works.md`, `02-first-conversation.md`, `03-prompt-fundamentals.md`, `04-anthropic-safety-approach.md`, `05-responsible-use.md` |
| `03-prompt-engineering/` | `README.md`, `01-clear-direct-instructions.md`, `02-structure-with-xml-tags.md`, `03-examples-few-shot.md`, `04-reasoning-and-thinking.md`, `05-task-decomposition-and-chaining.md`, `06-structured-output.md`, `07-system-prompts-and-roles.md`, `08-iterating-on-prompts.md` |
| `04-context-engineering/` | `README.md`, `01-what-is-context-engineering.md`, `02-managing-long-context.md`, `03-prompt-caching.md`, `04-memory-and-persistence.md`, `05-compaction-and-context-editing.md`, `06-progressive-disclosure-and-skills.md` |
| `05-claude-products-and-models/` | `README.md`, `01-product-ecosystem.md`, `02-model-families.md`, `03-model-selection.md`, `04-projects-and-knowledge.md`, `05-artifacts-and-output-formats.md`, `06-connectors-and-integrations.md` |
| `06-claude-api/` | `README.md`, `01-getting-started-with-the-api.md`, `02-messages-api.md`, `03-streaming.md`, `04-vision-documents-and-citations.md`, `05-batch-processing.md`, `06-errors-rate-limits-retries.md`, `07-cloud-platforms.md`, `08-token-counting-and-cost.md` |
| `07-tool-use-and-function-calling/` | `README.md`, `01-tool-use-fundamentals.md`, `02-defining-tools.md`, `03-the-tool-use-loop.md`, `04-server-tools.md`, `05-tool-design-best-practices.md`, `06-tool-security.md` |
| `08-model-context-protocol/` | `README.md`, `01-what-is-mcp.md`, `02-architecture.md`, `03-building-an-mcp-server.md`, `04-using-mcp-with-claude.md`, `05-mcp-security.md`, `06-mcp-vs-alternatives.md` |
| `09-claude-code/` | `README.md`, `01-what-is-claude-code.md`, `02-setup-and-first-session.md`, `03-claude-md-and-memory.md`, `04-permissions-and-settings.md`, `05-commands-skills-subagents.md`, `06-hooks.md`, `07-mcp-in-claude-code.md`, `08-team-rollout.md`, `09-headless-ci-and-agent-sdk.md` |
| `10-agentic-ai/` | `README.md`, `01-workflows-vs-agents.md`, `02-workflow-patterns.md`, `03-the-agent-loop.md`, `04-multi-agent-architecture.md`, `05-human-in-the-loop.md`, `06-managed-agents-and-agent-sdk.md`, `07-agent-reliability.md` |
| `11-rag-and-knowledge-systems/` | `README.md`, `01-rag-fundamentals.md`, `02-chunking-strategies.md`, `03-embeddings-and-indexing.md`, `04-retrieval-strategies.md`, `05-grounding-and-citations.md`, `06-rag-evaluation.md`, `07-rag-vs-long-context.md` |
| `12-ai-security/` | `README.md`, `01-llm-threat-modelling.md`, `02-prompt-injection.md`, `03-indirect-prompt-injection.md`, `04-data-exfiltration-and-disclosure.md`, `05-tool-misuse-and-excessive-agency.md`, `06-insecure-output-handling.md`, `07-supply-chain-risks.md`, `08-mcp-server-security.md`, `09-agent-identity-and-permissions.md`, `10-secrets-management.md`, `11-logging-and-auditability.md`, `12-ai-governance.md`, `13-human-oversight.md`, `14-enterprise-deployment-controls.md`, `owasp-llm-mapping.md` |
| `13-enterprise-ai-architecture/` | `README.md`, `01-solution-design-process.md`, `02-architecture-patterns.md`, `03-reference-architectures.md`, `04-integration-patterns.md`, `05-data-governance-and-compliance.md`, `06-stakeholder-communication.md`, `07-architecture-decision-records.md`, `08-business-value-and-roi.md`, `09-lifecycle-management.md` |
| `14-evaluation-and-testing/` | `README.md`, `01-why-evaluate.md`, `02-metrics.md`, `03-building-eval-datasets.md`, `04-grading-methods.md`, `05-ab-testing-and-iteration.md`, `06-diagnosing-failures.md`, `07-safety-and-red-team-evals.md` |
| `15-production-operations/` | `README.md`, `01-production-readiness.md`, `02-observability.md`, `03-cost-optimisation.md`, `04-latency-optimisation.md`, `05-reliability-engineering.md`, `06-rate-limits-and-capacity.md`, `07-incident-response.md`, `08-model-upgrades-and-change-management.md` |

## Certification tracks (16) — one folder per supported certification

`16-certification-tracks/README.md`, `registry.yaml`, and for each `<slug>` in {`ccao-f`, `ccar-f`, `ccar-p`}:
`README.md` (exam overview), `objective-map.yaml`, `coverage-matrix.md` (generated), `study-guide/domain-1.md` … `study-guide/domain-7.md`,
`practical-exercises.md`, `decision-scenarios.md`, (`ccar-f` only) `scenarios.md`, `revision-notes.md`, `common-misconceptions.md`, `exam-day.md`, `readiness-assessment.md`.

## Practice, mock exams, flashcards

- `17-practice-questions/README.md`, `schema/question-bank.schema.json`, `<slug>/d1.json` … `<slug>/d7.json` (CCAR-F has `d1` … `d5`)
- `18-mock-examinations/README.md`, `run_mock_exam.py`, `engine/`, `forms/<slug>-form-<n>.json`, `web/`
- `23-flashcards/README.md`, `decks/fundamentals.yaml`, `decks/ccao-f.yaml`, `decks/ccar-f.yaml`, `decks/ccar-p.yaml`

## Hands-on labs (19)

`19-hands-on-labs/README.md`, `requirements.txt`, `.env.example`, `common/claude_lab.py`, and one folder per lab, each with
`README.md`, `lab.py` (runs non-interactively and exits 0 in mock mode), and optional `data/` and extra modules:

| # | Folder | Level |
|---|---|---|
| 01 | `lab-01-first-claude-interaction` | Beginner |
| 02 | `lab-02-prompt-improvement` | Beginner |
| 03 | `lab-03-structured-outputs` | Beginner |
| 04 | `lab-04-document-grounded-qa` | Beginner |
| 05 | `lab-05-context-management` | Intermediate |
| 06 | `lab-06-model-comparison` | Intermediate |
| 07 | `lab-07-api-integration` | Intermediate |
| 08 | `lab-08-tool-invocation` | Intermediate |
| 09 | `lab-09-mcp-fundamentals` | Intermediate |
| 10 | `lab-10-claude-code-workflows` | Intermediate |
| 11 | `lab-11-rag-pipeline` | Intermediate |
| 12 | `lab-12-agentic-task-execution` | Advanced |
| 13 | `lab-13-human-in-the-loop` | Advanced |
| 14 | `lab-14-prompt-injection-testing` | Advanced |
| 15 | `lab-15-sensitive-data-protection` | Advanced |
| 16 | `lab-16-evaluation-framework` | Advanced |
| 17 | `lab-17-cost-optimisation` | Intermediate |
| 18 | `lab-18-reliability-engineering` | Advanced |
| 19 | `lab-19-observability` | Advanced |
| 20 | `lab-20-secure-enterprise-architecture` | Advanced |

## Real-world projects (20)

`20-real-world-projects/README.md` and `01-document-summarisation-assistant/`, `02-knowledge-base-qa-assistant/`,
`03-security-alert-triage-assistant/`, `04-devsecops-code-review-assistant/`, `05-agentic-investigation-assistant/`,
each with `README.md`, `src/`, `tests/`, `data/`.

## Reference sections

- `21-interview-preparation/`: `README.md`, `conceptual-questions.md`, `system-design-questions.md`, `security-questions.md`, `stakeholder-and-behavioural.md`
- `22-cheat-sheets/`: `README.md`, `claude-api.md`, `prompt-engineering.md`, `model-selection.md`, `claude-code.md`, `mcp.md`, `ai-security.md`, `ccao-f-one-pager.md`, `ccar-f-one-pager.md`, `ccar-p-one-pager.md`
- `24-troubleshooting/`: `README.md`, `api-errors.md`, `prompts-and-outputs.md`, `tools-and-agents.md`, `claude-code.md`, `mcp.md`, `rag.md`, `labs-and-repository.md`
- `25-official-resources/`: `README.md`, `exam-facts.md`, `verification-log.md`
- `website/`: `README.md`, `mkdocs.yml`, `hooks.py`, `assets/` (GitHub Pages site; built by `tools/build_site.py`)
- Root: `README.md`, `ROADMAP.md`, `PROGRESS.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`, `CHANGELOG.md`, `FAQ.md`, `GLOSSARY.md`
